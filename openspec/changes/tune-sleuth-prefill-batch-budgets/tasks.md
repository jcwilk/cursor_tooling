## 1. Processing configuration

- [x] 1.1 Add stage-specific fields to `ProcessingConfig` with defaults: relevance min/max content tokens, summarize target, merge target, merge max items per batch
- [x] 1.2 Parse new fields from `.sleuths/config.yaml` `processing` section in `load_config`
- [x] 1.3 Document new processing fields and defaults in `.cursor/skills/sleuths/SKILL.md`

## 2. Context-budget grouping

- [x] 2.1 Implement `group_chunks_by_min_max_budget` for minimum-target growth with maximum ceiling and item count cap
- [x] 2.2 Unit tests: grows to minimum, finalizes before exceeding maximum, short tail below minimum, oversized leading chunk truncation
- [x] 2.3 Wire summarize and merge stages to use stage-specific content targets (existing `group_chunks_by_budget` / `group_by_budget` with new budgets)

## 3. Pipeline stage wiring

- [x] 3.1 Update `run_relevance_pass` to use minimum-target grouping with relevance min/max config
- [x] 3.2 Update `run_summarize_pass` to use summarize-stage content target instead of global context budget
- [x] 3.3 Update `recursive_reduce` to use merge-stage content target and `merge_max_items_per_batch` (default 2)
- [x] 3.4 Add stderr logging when relevance batch is below minimum due to segment tail (optional debug line)

## 4. Tests and verification

- [x] 4.1 Unit test: relevance pass forms batches meeting min target when enough chunks exist (mocked inference)
- [x] 4.2 Unit test: merge groups contain at most configured max items (default 2)
- [x] 4.3 Regression: full sleuth test suite passes
- [ ] 4.4 Rebuild via `scripts/build-local-tools.sh` and smoke `sleuth refresh` on smoke-test sleuth; compare inference call counts and wall time vs prior baseline (note in apply handoff)

## Explicitly deferred

- Auto-tuning stage budgets from runtime latency telemetry — manual config only for v1.
- Separate relevance `max_chunks_per_batch` default reduction — keep existing default unless benchmarking during apply shows id-list pain.
