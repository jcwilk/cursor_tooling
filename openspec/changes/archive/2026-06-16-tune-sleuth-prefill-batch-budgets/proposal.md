## Why

Benchmarking against the Qwen3 inference endpoint shows that relevance filtering (raw input prefill) is fastest near ~2000 tokens of context, while filling the full ~16k window is substantially slower. Summarization and merge stages tolerate larger input but still benefit from moderate batch sizes (~8000 tokens) and pairing fewer summaries per merge step. The current pipeline uses one global context budget for all stages, which wastes time on oversized relevance batches and can over-pack merge groups.

## What Changes

- **Stage-specific context targets** for relevance filtering, summarization, and merge — each independently configurable with sensible defaults derived from benchmarking.
- **Relevance batch growth policy**: accumulate consecutive chunks until estimated input content reaches a configurable minimum target (~2000 tokens by default), then issue the relevance request; cap at a configurable maximum (~14000 tokens) with truncation when a single addition would exceed it.
- **Summarize batch policy**: group relevant chunks toward a larger but still bounded target (~8000 tokens by default) rather than the relevance minimum.
- **Merge batch policy**: prefer merging two summaries at a time (configurable maximum items per merge group, default 2) at a moderate input target (~8000 tokens), accounting for per-pass summary caps that may yield shorter actual summaries.
- **Configurable parameters** exposed in local sleuth processing configuration so operators can tune for their model without code changes.
- Update skill documentation to describe stage-specific budgets and defaults.

## Capabilities

### New Capabilities

_(none — behavior extends existing grouping and sleuth pipeline capabilities)_

### Modified Capabilities

- `context-budget-grouping`: stage-aware minimum-target batch growth for relevance; separate configurable ceilings per pipeline stage.
- `conversation-sleuths`: relevance, summarization, and hierarchical merge stages use distinct context targets and merge fan-in limits aligned with prefill performance characteristics.

## Impact

- Sleuth processing configuration schema (new optional processing fields with defaults).
- Context-budget grouping module and pipeline stage wiring (relevance, summarize, intra-segment reduce, cross-segment reduce).
- LangGraph segment pipeline orchestration (batch formation logic, not structural graph topology change).
- `.cursor/skills/sleuths/SKILL.md` configuration documentation.
- Existing checkpoints and summary artifacts remain compatible; next refresh may issue a different number of inference calls with similar or better latency.
