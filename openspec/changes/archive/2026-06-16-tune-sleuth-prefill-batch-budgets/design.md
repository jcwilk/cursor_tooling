## Context

Sleuth refresh runs three inference-heavy stages per segment: relevance filtering (many small JSON-id calls), batched summarization, and hierarchical merge (intra-segment and cross-segment). All stages currently derive batch size from one global `context_budget_tokens` (default 16384) minus prompt overhead, using `group_chunks_by_budget` / `group_by_budget` with `max_chunks_per_batch` (default 20).

Benchmarking Qwen3 on the configured inference endpoint shows **prefill latency scales poorly with input size** for the relevance stage. ~2000 tokens of raw input content is the sweet spot; filling toward 16k is much slower per call. Summarization and merge tolerate larger input but still benefit from moderate batches (~8000 content tokens) and **lower merge fan-in** (pairwise merges rather than triples) given per-pass summary caps (~4000 tokens) that often yield shorter actual outputs.

The LangGraph segment graph topology (chunk → relevance → summarize → reduce) stays the same; **batch formation policy** changes per stage.

## Goals / Non-Goals

**Goals:**

- Introduce **stage-specific content token targets** (minimum, target, maximum) configurable in local sleuth processing config.
- **Relevance**: grow consecutive chunk batches until estimated content ≥ minimum target (default 2000), never exceed maximum ceiling (default 14000); apply existing truncation rules when a single chunk overflows the ceiling.
- **Summarize**: group relevant chunks toward a summarize target (default 8000 content tokens), still respecting per-batch chunk count cap.
- **Merge** (intra-segment and cross-segment): group summaries toward merge target (default 8000 content tokens) with **default max 2 summaries per merge group** (configurable); shorter summaries naturally allow more headroom within the target.
- Preserve checkpoint semantics, refresh collect/finalize orchestration, tracing hierarchy, and backward-compatible config (new fields optional with defaults).
- Document new processing fields in sleuth skill.

**Non-Goals:**

- Changing relevance JSON schema, summarize/merge prompt templates, or LangGraph node topology.
- Model-specific tokenizer integration (keep char/4 token estimator).
- Auto-tuning budgets from runtime telemetry (manual config only in v1).
- Parallel inference within a stage.

## Decisions

### 1. New processing config fields (defaults from benchmarking)

| Field | Default | Used by |
|-------|---------|---------|
| `relevance_min_content_tokens` | 2000 | Relevance batch growth floor |
| `relevance_max_content_tokens` | 14000 | Relevance batch hard ceiling |
| `summarize_target_content_tokens` | 8000 | Summarize batch sizing |
| `merge_target_content_tokens` | 8000 | Intra- and cross-segment merge batch sizing |
| `merge_max_items_per_batch` | 2 | Merge fan-in cap |

Existing fields retained:
- `context_budget_tokens` / `response_headroom_tokens` — still define absolute ceiling for prompt+content+response math where stages need a hard cap; relevance max defaults below global budget.
- `pass_summary_cap_tokens` / `final_summary_target_tokens` — output size caps unchanged.
- `max_chunks_per_batch` — still caps chunk count for relevance and summarize; merge uses `merge_max_items_per_batch` instead.

**Rationale:** Stage-specific knobs let operators tune prefill without breaking operators who omit them.

### 2. Relevance batching: minimum-target growth

**Decision:** Add `group_chunks_by_min_max_budget(chunks, min_content, max_content, max_items)` in `context_budget.py`:

```
pending = chunks in order
while pending:
  group = []
  tokens = 0
  while pending:
    if max_items reached: break
    next = pending[0]
    if tokens >= min_content and tokens + next_tokens > max_content:
      break  # finalize at or above min without exceeding max
    if tokens == 0 and next_tokens > max_content:
      truncate prefix to max_content, emit, continue with remainder
    if tokens + next_tokens > max_content:
      if tokens >= min_content: break
      else: truncate / backoff per existing overflow rules
    append next; tokens += next_tokens
  emit group
```

**Alternatives considered:**
- *Fixed small batches always at 2000* — rejects variable tail segments; minimum-target handles short tails.
- *Reuse summarize grouping for relevance* — wrong latency profile; rejected.

### 3. Summarize batching: target-fill grouping

**Decision:** Use existing `group_chunks_by_budget` with `available_budget = summarize_target_content_tokens` (after prompt overhead subtraction in `content_budget()`), not the global 16k budget.

### 4. Merge batching: pairwise default

**Decision:** Use `group_by_budget` with `available_budget = merge_target_content_tokens` and `max_items = merge_max_items_per_batch` (default 2). Applies to `recursive_reduce` for both intra-segment and cross-segment paths.

**Rationale:** Two 4k-capped summaries often fit ~8k target; actual summaries may be shorter, allowing occasional three-way groups only if operator raises `merge_max_items_per_batch`.

### 5. Prompt overhead accounting unchanged

**Decision:** Each stage continues to subtract stage-specific prompt overhead and `response_headroom_tokens` from the configured content target when computing `content_budget(processing, overhead)` — but relevance uses min/max on **content tokens after overhead**, matching today's pattern in `run_relevance_pass`.

### 6. LangGraph structure

**Decision:** No new graph nodes. Batch policy changes live in `run_relevance_pass`, `run_summarize_pass`, and `recursive_reduce` call sites. Optional: log stderr when a relevance batch is below minimum because the segment tail is short.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| More relevance calls on very long segments (smaller batches) | Offset by faster per-call prefill; benchmark on smoke-test sleuth in tasks |
| Operators confuse global vs stage budgets | Document clearly in SKILL.md; defaults work out of the box |
| Min-target logic edge cases on tiny segments | Spec: emit partial batch even below minimum when no more chunks |
| Merge fan-in 2 increases merge depth for many pass summaries | Acceptable; merge calls are fewer than relevance; depth is O(log₂ N) |

## Migration Plan

1. Ship via `sleuth refresh` — new config fields optional; defaults apply when omitted.
2. No checkpoint or summary schema migration.
3. Next refresh may change inference call counts and latency profile.
4. Rollback: revert grouping/config changes.

## Open Questions

- Whether `max_chunks_per_batch` should also drop for relevance (e.g. 10) — defer; keep existing default 20 unless benchmarking shows id-list pain.
- Expose `relevance_max_content_tokens` higher for bulk mode presets — defer; single max field sufficient for v1.
