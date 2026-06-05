## Context

The sleuth refresh runner today reads transcript segments in fixed 40-line chunks, runs a map extraction on each chunk, and immediately reduces the result into the running summary. There is no relevance pre-filter, no batching against model context limits, and no hierarchical merge — so long sessions produce many small LLM calls and summaries that grow unbounded in merge noise.

The human wants a streaming pipeline that:

1. Consumes a session from the start as an ordered stream of chunks.
2. Groups chunks using a shared context-budget algorithm (default 16k minus prompt overhead minus 1000 response headroom).
3. Runs a relevance pass (zero-based indexed chunks → structured JSON list of relevant ids).
4. Summarizes only relevant chunks in budget-sized groups (each summary capped at ~4000 tokens).
5. Recursively merges summaries with the same grouping strategy toward a ~4000-token final summary with deduplicated facts.
6. On incremental refresh, seeds recursive merge with the existing summary.

## Goals / Non-Goals

**Goals:**

- Implement the streaming relevance → summarize → recursive-reduce pipeline per session segment.
- Extract shared context-budget grouping into reusable logic consumed by relevance, summarization, and merge stages.
- Parameterize context budget, response headroom, per-pass summary cap, and final summary target (sensible defaults: 16k, 1000, 4000, 4000).
- Preserve checkpoint semantics: only unprocessed transcript tail is consumed; failed refresh does not advance checkpoints.
- Keep summary and checkpoint artifact locations unchanged.

**Non-Goals:**

- Changing transcript discovery, slug resolution, or checkpoint key structure.
- Token-accurate counting tied to a specific model tokenizer — approximate counting (e.g. chars/4 or a lightweight heuristic) is acceptable for v1 if documented.
- Parallel LLM calls across groups within a session.
- Changing sleuth query YAML schema or human setup workflow.

## Decisions

### 1. Chunk source — retain line-based extraction, assign stable zero-based indices

Continue extracting plain text from JSONL in fixed line windows (existing `CHUNK_LINES` or configurable equivalent). Each chunk receives a monotonically increasing **zero-based** integer index within the session segment being processed (first chunk is `0`). Indices are stable for the duration of one refresh pass, are session-scoped (not reset per relevance group), and appear in relevance prompts.

**Rationale:** Reuses existing JSONL extraction; zero-based indices align with array lookup in code; indices give the LLM a compact handle for relevance selection without shipping full chunk text twice.

**Alternative considered:** Message-level chunks — richer semantics but requires new parsing; defer. **1-based indexing** — rejected; zero-based is simpler for implementation and equally clear when labeled explicitly in prompts.

### 2. Shared grouping module — `context_budget.rs`

Implement one function (conceptually: `group_by_budget(items, budget)`) that:

- Accepts ordered items with precomputed token estimates.
- Accumulates items until adding the next would exceed `budget - prompt_tokens - response_headroom`.
- When overflow occurs, if the group has more than one item, drop the last added item and emit the group; re-process dropped item in the next group.
- When the first (only) item in a candidate group exceeds the budget alone, truncate it to fit, emit the truncated prefix, and carry the remainder as the next item (same index or split index — implementation detail; behavior: no content lost across groups).

All three stages (relevance, summarize, merge) call this module with different item types mapped to token estimates.

**Rationale:** Human explicitly requested shared behavior; single module prevents drift between stages.

### 3. Three LLM prompt templates

| Stage | Input | Output |
|-------|-------|--------|
| Relevance | Zero-based indexed chunks + sleuth topic/lens | JSON object listing relevant chunk indices |
| Summarize | Indexed relevant chunks + lens | Markdown summary bounded by per-pass cap instruction |
| Merge | Multiple summaries (+ optional seed summary) + lens | Single merged summary with deduplicated facts, bounded by target cap |

**Relevance response contract:** the prompt instructs the model to respond with **only** a JSON object — no prose, no markdown fences — of the form:

```json
{"relevant_ids": [0, 2, 5]}
```

When nothing matches, the model returns `{"relevant_ids": []}`. The runner parses JSON, validates that `relevant_ids` is an array of integers, ignores out-of-range ids, and on parse failure treats the group as having no matches (log warning). Strip surrounding markdown code fences defensively before parse.

**Rationale:** Structured JSON is a common pattern for constrained LLM output; it avoids comma-separated parsing ambiguity and reduces “helpful” preamble around bare id lists. Separates filtering from compression; merge prompt explicitly instructs deduplication.

Prompt token overhead is measured (or estimated from template + topic) and subtracted from the context budget before grouping.

### 4. Per-session processing flow

For each pending transcript segment (checkpoint tail → end):

```
chunks := stream from start_line to end_line
for each relevance_group in group(chunks):
    ids := LLM relevance(relevance_group)
    relevant_chunks += lookup(ids)

intermediate_summaries := []
for each summary_group in group(relevant_chunks):
    intermediate_summaries += LLM summarize(summary_group)

final := recursive_reduce(intermediate_summaries, target=4000)
if existing summary non-empty:
    final := recursive_reduce([existing_summary, final], seed=existing_summary)
else:
    store final as summary
advance checkpoint to end_line
```

`recursive_reduce` repeatedly groups summaries, merges each group via LLM, and repeats until one summary remains within the target budget (or a single group merge suffices).

**Rationale:** Matches human-specified pipeline; existing summary participates only in the final reduce tree as seed aggregate.

### 5. Configuration — extend `.sleuths/config.yaml`

Add optional `processing` section with defaults:

```yaml
processing:
  context_budget_tokens: 16384
  response_headroom_tokens: 1000
  pass_summary_cap_tokens: 4000
  final_summary_target_tokens: 4000
  chunk_lines: 40
```

Omitted keys fall back to defaults. Document in skill README.

**Rationale:** Human asked for parameterized limits with stated defaults; YAML keeps machine-local tuning without changing query definitions.

### 6. Token estimation

Use a simple heuristic (`ceil(char_count / 4)`) for v1 budget accounting, applied consistently across grouping stages. Log when truncation occurs.

**Rationale:** Avoids pulling in model-specific tokenizers; good enough for budget packing. Can refine later.

### 7. Incremental refresh with prior summary

When `summary.md` already has content beyond the title header, pass it as the **seed aggregate** into the final recursive reduce alongside new session output — not into every map pass. New session material still runs relevance → summarize → reduce independently first; then `{prior_summary, new_session_summary}` merge via the same recursive reduce with prior summary as starting aggregate value in merge prompts.

**Rationale:** Matches human intent: "start with the prior summary as the aggregate value" during recursive reduction, not re-scanning old material.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Heuristic token counts cause occasional overflow/underflow vs real model limits | Conservative headroom default (1000); truncate on overflow; log warnings |
| Relevance pass misses important chunks | Chunks are small enough that adjacent context overlaps; human reviews summary quality |
| Structured relevance response malformed | JSON parse with fence-stripping; invalid shape or out-of-range ids ignored; parse failure → no matches for that group (log warning) |
| More LLM calls per session than old per-chunk merge | Fewer reduce calls on irrelevant material; net cost depends on session; acceptable for quality |
| Recursive merge depth on very large sessions | Same grouping caps breadth; depth logarithmic in summary count |

## Migration Plan

1. Ship updated runner behind same CLI (`sleuth refresh`).
2. Existing checkpoints compatible — next refresh processes tail with new pipeline.
3. Existing summaries used as merge seed; first refresh after upgrade may reshape summary format slightly.
4. Rollback: revert runner binary; checkpoints and summaries remain valid.

## Open Questions

- Whether to persist intermediate summaries for debugging — defer unless needed during apply spike.
