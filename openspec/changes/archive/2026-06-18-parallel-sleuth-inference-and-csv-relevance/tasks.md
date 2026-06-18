## Required for this change

## 1. Configuration

- [x] 1.1 Add `max_parallel_inference_requests: int = 4` to `ProcessingConfig` in `.cursor/skills/sleuths/sleuth/config.py`
- [x] 1.2 Load `processing.max_parallel_inference_requests` from `.sleuths/config.yaml` with clamp-to-1 for values below 1
- [x] 1.3 Document the new setting in `.cursor/skills/sleuths/SKILL.md` and any sleuth config examples

## 2. Parallel inference execution

- [x] 2.1 Add a small helper (e.g. in `pipeline.py` or a dedicated module) that runs batch callbacks with `ThreadPoolExecutor` capped at `max_parallel_inference_requests`, preserving result order per group index
- [x] 2.2 Refactor `run_relevance_pass` to submit relevance batch groups in parallel
- [x] 2.3 Refactor `run_summarize_pass` to submit summarize batch groups in parallel
- [x] 2.4 Refactor `recursive_reduce` merge-round inner loop to submit merge groups in parallel within each round (rounds remain sequential)

## 3. Comma-separated relevance format

- [x] 3.1 Update `relevance_prompt()` in `.cursor/skills/sleuths/sleuth/prompts.py` to request comma-separated zero-based indices only (no JSON)
- [x] 3.2 Rewrite `parse_relevant_ids()` in `.cursor/skills/sleuths/sleuth/relevance.py` for CSV parsing (strip fences, split commas, validate range, dedupe, sort)
- [x] 3.3 Update relevance tests in `.cursor/skills/sleuths/tests/test_sleuth.py` for CSV inputs and edge cases (empty, whitespace, out-of-range, non-numeric tokens, unparseable)

## 4. Verification

- [x] 4.1 Run sleuth unit tests: `python -m pytest .cursor/skills/sleuths/tests/ -q`
- [x] 4.2 Add or extend tests asserting parallel batch submission respects configured concurrency cap (mock client call tracking)

## Explicitly deferred

- Parallelism across different pipeline stages simultaneously (by intent — see proposal non-goals)
- Changing input batch sizing budgets or stage-specific content targets
- New retry/backoff semantics for failed parallel inference calls
