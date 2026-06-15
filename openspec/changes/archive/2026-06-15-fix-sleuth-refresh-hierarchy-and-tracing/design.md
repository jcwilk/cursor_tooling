## Context

The sleuth refresh runner processes pending transcript segments in a loop. Each segment runs a LangGraph pipeline (relevance → summarize → intra-segment reduce). After **every** segment, `refresh.py` calls `_merge_new_summaries`, which passes the **full growing list** of segment summaries into `recursive_reduce` with `prior_body` frozen at its initial value (empty on reset). That produces O(segments) cross-segment merge inference calls and re-merges earlier segment summaries repeatedly.

The archived map-reduce design (`2026-06-08-fix-sleuth-streaming-map-reduce`) intended cross-segment merge **once** after all segments in the batch, with prior summary as seed only in that final step. Implementation drifted.

Cloud tracing uses `@traceable` only on `InferenceClient.generate`. LangGraph creates a separate root trace per `graph.invoke()`. Rolling merges run outside the graph and become orphan root traces. A typical full refresh therefore exports ~28 top-level traces instead of one tree.

Measured on a recent tooling refresh: 76 inference calls (40 relevance, 17 summarize, 19 merge), of which 11 rolling merges were redundant re-merges. LangSmith showed 14 `LangGraph` roots + 14 orphan `sleuth_inference_generate` roots.

## Goals / Non-Goals

**Goals:**

- Restore hierarchical map-reduce at the refresh level: collect segment summaries during the batch, cross-segment reduce **once** at batch end (tree depth O(log N) in merge calls, not O(N)).
- On incremental refresh, merge **prior summary body + new segment summaries only**, using prior as seed — never re-merge segment summaries already represented in the prior artifact.
- When cloud tracing is enabled, export **one root trace per refresh** with named child spans for each conceptual cluster (refresh → segment → stage → inference call).
- Span names readable in isolation (~5 words acceptable).
- Preserve checkpoint semantics, artifact paths, segment-level pipeline, and local-only default.

**Non-Goals:**

- Changing relevance/summarize/intra-segment logic beyond nesting under new trace spans.
- Parallel inference within a segment.
- Changing sleuth query schema, discovery, or reset behavior.
- Requiring cloud tracing (remains opt-in).

## Decisions

### 1. Two-phase refresh orchestration

**Decision:** Split refresh into **collect** and **finalize** phases.

```
collect phase (per pending segment):
  segment_summary := run_segment_pipeline(...)
  if non-empty: append to batch_segment_summaries
  advance checkpoint + write provisional summary header only if needed for crash safety (see decision 3)

finalize phase (once per refresh, after all pending segments):
  if prior summary body non-empty:
    body := recursive_reduce([prior_body, *batch_segment_summaries], seed=prior_body)
  else:
    body := recursive_reduce(batch_segment_summaries, seed=None)
  write summary.md
```

**Alternatives considered:**

- *Incremental merge after each segment with updated prior_body* — still O(segments) merge calls; rejected.
- *Defer checkpoint until finalize* — simpler merge but loses incremental crash recovery; rejected.

### 2. Incremental refresh seed semantics

**Decision:** `prior_body` is read once at batch start from existing `summary.md`. During collect, only **new** segment summaries accumulate. Finalize merges `prior_body` (seed) + new summaries only. Prior body is never duplicated in the inputs list (avoid `[prior, s1, s2, …]` when prior is already the seed).

**Rationale:** Matches archived design and user expectation; eliminates redundant re-merge of historical segment summaries on full reset rebuilds.

### 3. Checkpoint vs summary write during collect

**Decision:** Continue advancing checkpoint after each segment (crash safety). During collect, **do not** run cross-segment merge or rewrite `summary.md` body. Optionally write a stale marker in summary header comment or leave summary unchanged until finalize — prefer **leave summary unchanged until finalize** so agents never read partially re-merged state mid-refresh.

On refresh failure mid-batch, checkpoint reflects processed segments; summary remains pre-batch until a successful finalize. Re-run refresh processes remaining tail only; finalize merges prior summary + any new segment summaries from the incomplete batch.

**Trade-off:** Mid-refresh, summary may lag checkpoint by at most one failed batch — acceptable; checkpoint is source of processing progress.

### 4. Observability hierarchy

**Decision:** Wrap refresh in a top-level `@traceable(name="sleuth refresh operation", run_type="chain")` (exact string in implementation). Nested spans:

| Span name (examples) | Scope |
|----------------------|--------|
| `sleuth refresh operation` | Entire refresh for one sleuth id |
| `sleuth process transcript segment` | One segment's LangGraph pipeline |
| `sleuth filter chunks for relevance` | Relevance pass (wrap `run_relevance_pass` or graph node) |
| `sleuth summarize relevant chunks` | Summarize pass |
| `sleuth merge pass summaries within segment` | Intra-segment hierarchical reduce |
| `sleuth merge segment summaries into summary` | Finalize-phase cross-segment reduce |
| `sleuth inference generate call` | Individual LLM HTTP call (rename from `sleuth_inference_generate`) |

LangGraph `invoke()` runs inside the segment span context so LangGraph children nest under `sleuth process transcript segment` rather than creating orphan roots.

Rolling/finalize merges run inside the refresh root span.

**Alternatives considered:**

- *Rely on LangGraph default names only* — rejected; produces opaque `LangGraph` roots.
- *One span per inference only* — rejected; missing orchestration layer.

Use LangSmith `@traceable` on orchestration functions; ensure `LANGCHAIN_CALLBACKS_BACKGROUND=false` remains for CLI flush (already set in `tracing.py`).

### 5. Merge call budget sanity check

**Decision:** Add a debug log line at finalize reporting `{relevance, summarize, intra_merge, cross_merge}` counts. Cross-segment merge calls for a batch SHALL be ≤ `ceil(log2(S)) + 1` groups in typical cases where S segment summaries fit budget groupings (not a hard requirement in spec — operational test in tasks).

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Summary stale until finalize completes | Document in skill; refresh is human-initiated and long-running already |
| Mid-batch failure leaves summary unchanged while checkpoint advanced | Next refresh finalizes with prior + new segments; acceptable |
| LangGraph trace nesting depends on LangSmith context propagation | Integration test with tracing enabled; verify single root in LangSmith |
| Summary wording changes vs old per-segment merge order | Expected; note in migration; quality should improve |

## Migration Plan

1. Ship via existing `sleuth refresh` CLI — no schema migration.
2. Checkpoints compatible.
3. Next refresh after upgrade uses new merge schedule; summary may differ slightly in structure.
4. Rollback: revert runner module.

## Open Questions

- Persist intermediate segment summaries for debugging — deferred.
- Whether to add a `--verbose-trace` flag for span metadata — defer; default names sufficient for v1.
