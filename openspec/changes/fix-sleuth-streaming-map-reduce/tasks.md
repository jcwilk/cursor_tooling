## 1. Context-budget grouping module

- [ ] 1.1 Add token estimation helper and configurable budget/headroom types to sleuth config
- [ ] 1.2 Implement shared context-budget grouping (accumulate, overflow back-off, leading truncation)
- [ ] 1.3 Add unit tests for grouping edge cases (single oversized item, exact fit, multi-group split)

## 2. Prompt templates and LLM stages

- [ ] 2.1 Add relevance prompt template (zero-based indexed chunks, JSON `relevant_ids` response, topic interpolation)
- [ ] 2.2 Add summarize prompt template with per-pass token cap instruction
- [ ] 2.3 Add merge prompt template with deduplication and final target cap; support prior summary as seed aggregate
- [ ] 2.4 Implement JSON relevance response parser (strip fences, validate integer array, ignore out-of-range ids; fallback to no matches on failure)

## 3. Refresh pipeline refactor

- [ ] 3.1 Refactor segment processing to stream chunks with stable indices from checkpoint forward
- [ ] 3.2 Wire relevance pass: group chunks → LLM → collect relevant chunks
- [ ] 3.3 Wire summarize pass: group relevant chunks → LLM per group → collect pass summaries
- [ ] 3.4 Wire recursive reduce: group pass summaries → merge → repeat until within final target
- [ ] 3.5 On incremental refresh, seed final merge with existing summary content
- [ ] 3.6 Preserve checkpoint advance only on successful completion; remove old per-chunk immediate reduce path

## 4. Configuration and documentation

- [ ] 4.1 Extend `.sleuths/config.yaml` schema with optional `processing` defaults (document in skill)
- [ ] 4.2 Update `.cursor/skills/sleuths/SKILL.md` to describe streaming map/reduce behavior at a high level
- [ ] 4.3 Update `AGENTS.md` sleuths section if behavior description needs adjustment

## 5. Verification

- [ ] 5.1 Build sleuth binary via `scripts/build-local-tools.sh`
- [ ] 5.2 Manual smoke test: refresh a sleuth against a real transcript segment; confirm summary bounded and checkpoint advances
- [ ] 5.3 Manual smoke test: incremental refresh with existing summary confirms prior content preserved through merge seed

## Explicitly deferred

- Model-specific tokenizer integration for exact token counts
- Persisting intermediate relevance/summary artifacts for debugging
- Parallel LLM calls across groups within a session
