## Why

The sleuth refresh runner still processes transcript material in large chunks and merges each extraction immediately into the running summary. That produces many sequential inference calls, ignores model context limits, cannot filter irrelevant material before summarization, and lets summaries grow without bound. A batched pipeline — small indexed chunks, relevance filtering, grouped summarization, and recursive reduction — matches the intended design and scales to long sessions.

## What Changes

- Replace per-chunk immediate merge with a **session pipeline**: stream small indexed chunks, **filter** each budget-sized batch to relevant ids, **drop** non-selected chunks, **summarize** filtered chunks in budget-sized batches, then **recursively reduce** pass summaries until one bounded result remains.
- Size chunks as **small granular units** (typically single transcript lines) with a **cap on how many chunks appear in one relevance or summarize batch** (default ~20) so the model is not asked to choose among hundreds of ids at once.
- Pack batches using **shared context-budget grouping** that accounts for prompt overhead and response headroom at every stage.
- On incremental refresh, run the full pipeline on new material first, then merge with the prior summary via the same recursive reduce (prior summary as seed aggregate only at that final merge).
- Parameterize context budget, response headroom, per-pass summary cap, final summary target, chunk granularity, and max chunks per batch (sensible defaults documented in design).
- Update sleuth skill documentation to describe the pipeline at a high level.

## Capabilities

### New Capabilities

- `context-budget-grouping`: Reusable rules for packing ordered items into consecutive groups that respect both a token budget (after overhead and headroom) and an optional maximum item count per group.

### Modified Capabilities

- `conversation-sleuths`: Replace per-chunk immediate merge with relevance filtering, batched summarization, and hierarchical recursive reduction bounded by configurable limits; incremental refresh merges new session output into prior summary only at the final reduce step.

## Impact

- Sleuth refresh runner and local processing configuration.
- Living spec: `conversation-sleuths` gains new requirements; new sibling spec `context-budget-grouping`.
- Skill docs for `/sleuths`.
- No breaking change for humans invoking refresh; checkpoint and summary artifact locations unchanged. Summary content and structure may differ after upgrade.
