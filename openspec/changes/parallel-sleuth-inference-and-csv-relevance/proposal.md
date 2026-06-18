## Why

Sleuth refresh spends most of its time waiting on serial summarization-service calls within each pipeline stage. Relevance filtering also asks the model for a JSON object listing chunk indices, which roughly doubles the generated tokens for a short answer. Parallelizing inference within a stage and switching to a compact comma-separated index response should shorten refresh runs without changing batch sizing or cross-stage orchestration.

## What Changes

- Run up to four summarization-service requests in parallel within each stage that issues multiple calls (relevance batches, summarize batches, merge rounds), instead of strictly one-at-a-time loops.
- Expose a configurable maximum parallel inference concurrency on the local workstation (default four).
- Change relevance filtering to request and parse comma-separated zero-based chunk indices only (e.g. `0,2,5` or empty), replacing the JSON object format.
- Update implementation, tests, and operator documentation for the new relevance format and parallel execution model.

## Capabilities

### New Capabilities

<!-- None — behavior extends existing conversation-sleuths capability -->

### Modified Capabilities

- `conversation-sleuths`: Relevance filtering pass output format (structured JSON list → comma-separated indices); add bounded parallel inference within pipeline stages that issue multiple service calls.

## Impact

- Sleuth pipeline stages that loop over batch groups (`run_relevance_pass`, `run_summarize_pass`, `recursive_reduce` and related merge paths).
- Relevance prompt and response parser.
- Local sleuth processing configuration (new concurrency setting alongside existing stage sizing).
- Unit tests for relevance parsing and pipeline batch execution.
- Sleuth skill documentation and any AGENTS.md references to relevance JSON format.

## Non-goals

- Parallelism across different pipeline stages at the same time (only within a stage's batch list).
- Changing input batch sizing budgets or stage-specific content targets.
- New retry semantics for failed parallel calls beyond existing error handling.
