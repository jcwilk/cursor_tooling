## 1. Refresh orchestration — collect and finalize

- [x] 1.1 Refactor `refresh.py` into collect phase (segment pipeline + checkpoint advance) and finalize phase (single cross-segment `recursive_reduce`)
- [x] 1.2 Remove per-segment `_merge_new_summaries` calls; accumulate `batch_segment_summaries` during collect
- [x] 1.3 Implement finalize merge: prior summary body as seed + new batch segment summaries only (no duplicate prior in inputs list)
- [x] 1.4 Defer `summary.md` body write until successful finalize; leave body unchanged on mid-batch failure
- [x] 1.5 Add stderr summary of inference call counts by stage (relevance, summarize, intra merge, cross merge) at end of refresh

## 2. Observability hierarchy

- [x] 2.1 Add `@traceable` wrapper for refresh operation (root span when tracing enabled)
- [x] 2.2 Add named `@traceable` spans for segment processing, relevance pass, summarize pass, intra-segment merge, and cross-segment merge phases
- [x] 2.3 Rename inference span to a descriptive plain-language name; ensure calls nest under phase spans
- [x] 2.4 Verify LangGraph `invoke()` runs inside segment span context so graph traces nest rather than creating orphan roots
- [x] 2.5 Integration check: one root trace per refresh in LangSmith when credentials configured (document evidence in apply handoff)

## 3. Tests

- [x] 3.1 Unit test: full-reset refresh with mocked inference asserts cross-segment merge runs once after N segments
- [x] 3.2 Unit test: incremental refresh passes prior body as seed without duplicating it in merge inputs
- [x] 3.3 Unit test: mid-batch failure leaves summary body unchanged while checkpoint reflects processed segments
- [x] 3.4 Regression test: existing sleuth test suite passes after refactor

## 4. Documentation and local tooling

- [x] 4.1 Update `.cursor/skills/sleuths/SKILL.md` refresh pipeline section (batch finalize, tracing tree)
- [x] 4.2 Update `AGENTS.md` conversation sleuths section if tracing behavior description needs alignment
- [x] 4.3 Rebuild local sleuth CLI via `scripts/build-local-tools.sh` and verify `sleuth refresh` on smoke-test sleuth

## Explicitly deferred

- Persisting intermediate segment summaries for debugging — out of scope; revisit if refresh quality issues arise.
- `--verbose-trace` CLI flag for extra span metadata — out of scope for v1.
