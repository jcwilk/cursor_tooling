## Context

The refresh runner on the apply branch still uses a per-chunk map followed by immediate reduce into a growing summary (large char-budget chunks, no id-based filter). An exploratory implementation on `explore/fix-sleuth-streaming-map-reduce` introduced relevance → summarize → recursive reduce but defaulted to 40-line chunks and token-only grouping without a hard cap on items per batch.

The human’s target pipeline:

1. **Small chunks** — often one transcript line each; may grow lines only when needed to stay within a manageable batch size.
2. **Bounded id lists** — when packing a relevance batch, aim for **at most ~20 chunks** so the model selects from a short indexed list, not hundreds of ids.
3. **Filter first** — relevance pass returns which chunk indices match the sleuth lens; non-selected chunks are dropped before any summarization.
4. **Batch summarize** — pack filtered chunks into summarize batches (same budget + count rules); each batch produces one pass summary.
5. **Recursive reduce** — if multiple pass summaries exist, merge them in budget-sized batches until one summary remains; skip this step when only one pass summary exists.
6. **Incremental** — prior summary participates only in the final merge seed, not in every per-chunk step.

### Walkthrough (contrived)

80 transcript lines → chunk into **8 chunks** of 10 lines each (indices 0–7). All 8 fit one relevance batch (&lt;20 cap, within token budget).

- **Relevance**: one call → `{"relevant_ids": [1, 3, 5, 7]}` (4 chunks kept).
- **Summarize**: one call with chunks 1, 3, 5, 7 → **one pass summary**.
- **Reduce**: only one pass summary → **no further merge** for this segment.

Contrast with the old path: up to **8 map + up to 8 reduce** calls (16 sequential), each reduce re-sending the entire growing summary.

## Goals / Non-Goals

**Goals:**

- Implement relevance → batched summarize → recursive reduce per transcript segment.
- Small default chunk granularity with stable zero-based indices per segment pass.
- Enforce **max chunks per batch** (default 20) in addition to token-budget grouping at relevance, summarize, and merge stages.
- Shared grouping module for all stages.
- Preserve checkpoint semantics; keep artifact locations unchanged.
- Prior summary as merge seed only at the end of incremental refresh.

**Non-Goals:**

- Changing transcript discovery, slug resolution, or checkpoint key structure.
- Model-specific tokenizers (heuristic estimation is acceptable for v1).
- Parallel inference calls within a session.
- Changing sleuth query YAML schema or human setup workflow.
- Pipelining summarize while relevance is still running on later groups (phased: finish relevance collection for a segment, then summarize, then reduce — acceptable for v1).

## Decisions

### 1. Chunk formation — small units, stable indices

- Extract plain text from JSONL in **small line windows**; default **1 line per chunk** when not configured otherwise.
- Each chunk gets a monotonically increasing **zero-based index** for the segment pass (first chunk is `0`); indices are stable and session-scoped.
- **Optional line growth**: configuration MAY allow merging consecutive lines into one chunk up to a maximum line count when a single line is empty or trivially small — implementation detail; behavior goal is “small enough that a full relevance batch stays readable.”

**Rationale:** One-line chunks maximize filter precision; growth is an optimization, not the default story.

### 2. Dual constraint grouping — token budget **and** max items per group

`group_by_budget` (shared module) takes:

- ordered items with token estimates,
- available content budget (context budget − prompt overhead − response headroom),
- **max items per group** (default **20**).

Algorithm (same overflow back-off and leading truncation as today):

- Accumulate items until **either** the next item would exceed the token budget **or** the group already holds `max_items` items.
- On token overflow with 2+ items: back off last item to next group.
- On item-count cap: finalize group, start next group with remaining items.
- On oversized leading item: truncate prefix to fit budget, carry remainder forward.

All three stages (relevance, summarize, merge) use this module. **Relevance** and **summarize** default `max_items = 20`. **Merge** groups summary strings with the same rules (count cap prevents merging too many summaries in one prompt).

**Rationale:** Token-only grouping allowed 40-line chunks to pack few items but tiny lines could still produce huge id lists; the human’s “~1/20 of context → at most 20 chunks” policy is enforced explicitly.

### 3. Three inference stages

| Stage | Input | Output |
|-------|-------|--------|
| Relevance | Indexed chunks in one group + sleuth lens | JSON `{"relevant_ids": […]}` — zero-based indices only |
| Summarize | Indexed **filtered** chunks in one group + lens | Markdown summary bounded by per-pass cap |
| Merge | Multiple summaries (+ optional seed) + lens | Single merged summary, deduplicated, bounded by target cap |

**Relevance contract:** JSON only; empty list when nothing matches; parse failure → treat group as no matches (log warning); strip markdown fences defensively; ignore out-of-range ids.

**Drop rule:** Chunks whose indices are not returned are **excluded** from all later stages for that segment pass.

### 4. Per-segment processing flow (phased v1)

For each pending transcript segment (checkpoint tail → end):

```
chunks := stream small indexed chunks from start_line to end_line
relevant := []
for each group in group(chunks, budget, max_items=20):
    ids := LLM relevance(group)
    relevant += lookup(ids)   // drops non-selected

pass_summaries := []
for each group in group(relevant, budget, max_items=20):
    pass_summaries += LLM summarize(group)

segment_summary := recursive_reduce(pass_summaries, target=final_cap)
```

After all segments in the refresh batch:

```
if prior summary non-empty:
    summary := recursive_reduce([prior_summary, …segment_summaries…], seed=prior_summary)
else:
    summary := combine segment_summary results via recursive_reduce
```

`recursive_reduce`: while more than one summary, group them (budget + count cap), merge each group via LLM, repeat until one summary within final target.

**Single pass summary:** recursive reduce is a no-op (matches the 80-line / 4-relevant example).

### 5. Configuration (local, optional)

Extend machine-local sleuth config with optional processing defaults (exact keys in implementation; documented in skill):

| Parameter | Default | Role |
|-----------|---------|------|
| Context budget tokens | 16384 | Total window for packing |
| Response headroom tokens | 1000 | Reserved for model output |
| Pass summary cap tokens | 4000 | Upper bound instruction per summarize pass |
| Final summary target tokens | 4000 | Stop condition for recursive reduce |
| Chunk lines | 1 | Lines merged per chunk |
| Max chunks per batch | 20 | Item count cap per relevance/summarize/merge group |

Omitted keys use defaults.

### 6. Token estimation

`ceil(char_count / 4)` for v1, applied consistently. Log truncation events.

### 7. Incremental refresh

New tail material runs the full segment pipeline independently. Existing `summary.md` content is passed as **seed aggregate** only in the final cross-segment / cross-refresh recursive reduce — never in per-chunk map-style calls.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Heuristic tokens vs real model limits | Conservative headroom; truncate; log warnings |
| Relevance misses important chunks | Small chunks; human reviews summary quality |
| Malformed relevance JSON | Parse failure → no matches for that group; continue |
| More relevance calls on very long sessions | Batched by 20 chunks; still far fewer than per-chunk map+reduce |
| 1-line chunks increase chunk count | Count cap keeps relevance prompts bounded; irrelevant lines filtered cheaply |

## Migration Plan

1. Ship behind same `sleuth refresh` CLI.
2. Checkpoints compatible — next refresh processes tail with new pipeline.
3. Existing summaries used as merge seed; first refresh after upgrade may reshape content.
4. Rollback: revert runner binary.

## Open Questions

- Persist intermediate pass summaries for debugging — deferred.
- Adaptive chunk line growth heuristics beyond fixed `chunk_lines` — defer unless quality issues appear.
