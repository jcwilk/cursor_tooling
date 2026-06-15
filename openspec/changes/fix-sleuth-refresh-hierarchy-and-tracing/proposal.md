## Why

Sleuth refresh currently performs redundant cross-segment merges after every transcript segment (re-merging the full accumulator from scratch) and exports fragmented cloud traces (dozens of top-level runs per refresh instead of one coherent tree). This wastes inference calls, obscures cost and latency in observability tools, and contradicts the hierarchical map-reduce model the refresh pipeline was designed to follow.

## What Changes

- **Fix refresh merge hierarchy** so cross-segment reduction runs once at the end of a refresh batch (or incrementally with a proper accumulator seed), not after every segment. Merge call counts SHALL decrease relative to summarize call counts for typical refreshes.
- **Honor prior summary as merge seed** during incremental refresh: new segment summaries merge into the existing summary body rather than re-merging the entire segment list each time.
- **Unify observability under a single refresh trace** when cloud tracing is enabled: one root run per refresh operation with named child spans for each conceptual phase (segment processing, relevance, summarize, merge tiers).
- **Use descriptive span names** that read sensibly in isolation (e.g. five-word names are acceptable).
- Update sleuth skill documentation to reflect the corrected pipeline and tracing shape.

## Capabilities

### New Capabilities

_(none — behavior changes extend the existing conversation-sleuths capability)_

### Modified Capabilities

- `conversation-sleuths`: cross-segment merge scheduling and hierarchy; prior-summary seed semantics on incremental refresh; cloud tracing tree structure and span naming when observability is enabled.

## Impact

- Sleuth Python refresh runner (segment loop, merge orchestration, tracing instrumentation).
- Optional cloud observability exports (trace hierarchy only; no change to local-only default).
- `.cursor/skills/sleuths/SKILL.md` and `AGENTS.md` conversation-sleuths section (documentation alignment).
- Existing checkpoints and summary artifacts remain compatible; next refresh may produce slightly different summary wording due to corrected merge order.
