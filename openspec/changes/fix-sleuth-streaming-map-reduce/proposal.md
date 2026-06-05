## Why

The current sleuth refresh pipeline processes fixed-size line chunks one at a time and merges each extraction immediately into the running summary. That approach ignores model context limits, cannot filter irrelevant material before summarization, and produces noisy incremental merges on long sessions. A streaming, context-budget-aware map/reduce pipeline will scale to large transcripts while keeping summaries focused and within bounded size.

## What Changes

- Replace per-chunk immediate merge with a **streaming session pipeline**: consume a session from the beginning as an ordered sequence of chunks, group chunks to fit within a configurable context budget, identify relevant chunks via a zero-based indexed relevance pass with structured JSON output, summarize only those chunks, then recursively merge summaries with deduplication.
- Introduce a **shared context-budget grouping** capability used by both the relevance and summarization/merge stages (gather until overflow, drop one to fit, truncate oversized leading chunks and carry remainder forward).
- Parameterize context budget (default 16k tokens), response headroom (default 1000 tokens), per-pass summary cap (default 4000 tokens), and final summary target (default 4000 tokens).
- On incremental refresh over an existing summary, run the same pipeline but seed recursive merge with the prior summary as the initial aggregate.
- Update the sleuth refresh runner and skill documentation to reflect the new behavior.

## Capabilities

### New Capabilities

- `context-budget-grouping`: Reusable rules for packing ordered text items into groups that fit within a model context budget after accounting for prompt overhead and response headroom, including truncation of oversized leading items.

### Modified Capabilities

- `conversation-sleuths`: Replace lazy incremental per-chunk merge with streaming relevance filtering and hierarchical map/reduce summarization bounded by configurable token limits; incremental refresh merges new session output into prior summary via the same reduce path.

## Impact

- **Sleuth runner** (Rust CLI under `.cursor/skills/sleuths/`): refresh pipeline, prompt templates, configuration defaults.
- **Living spec**: `conversation-sleuths` gains new requirements; new sibling spec `context-budget-grouping`.
- **Skill docs**: `.cursor/skills/sleuths/SKILL.md` — describe new pipeline behavior at a high level.
- **No breaking API** for humans invoking refresh; checkpoint and summary artifact locations unchanged. Summaries produced after refresh may differ in structure/quality from the old per-chunk merge.
