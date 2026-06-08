## 1. Context-budget grouping module

- [ ] 1.1 Add token estimation helper and configurable budget, headroom, and max-items-per-group types to sleuth config
- [ ] 1.2 Implement shared grouping with token budget, overflow back-off, leading truncation, and item-count cap
- [ ] 1.3 Add unit tests for grouping edge cases (count cap split, single oversized item, exact fit, multi-group split)

## 2. Prompt templates and inference stages

- [ ] 2.1 Add relevance prompt template (zero-based indexed chunks, JSON index list response, topic interpolation)
- [ ] 2.2 Add summarize prompt template with per-pass size cap instruction
- [ ] 2.3 Add merge prompt template with deduplication and final target cap; support prior summary as seed aggregate
- [ ] 2.4 Implement JSON relevance response parser (strip fences, validate integer array, ignore out-of-range ids; fallback to no matches on failure)

## 3. Refresh pipeline refactor

- [ ] 3.1 Stream small indexed chunks (default one line per chunk) from checkpoint forward
- [ ] 3.2 Wire relevance pass: group chunks (budget + max ~20) → inference → collect only returned indices
- [ ] 3.3 Wire summarize pass: group filtered chunks (same limits) → one pass summary per group
- [ ] 3.4 Wire recursive reduce: merge pass summaries in grouped batches until within final target; no-op when only one pass summary
- [ ] 3.5 On incremental refresh, seed final merge with existing summary content only at the recursive reduce step
- [ ] 3.6 Remove per-chunk immediate map/reduce path (including any char-budget interim implementation); checkpoint advances only on successful completion

## 4. Configuration and documentation

- [ ] 4.1 Extend local sleuth config with optional processing defaults (chunk lines, max chunks per batch, budget caps — document in skill)
- [ ] 4.2 Update `.cursor/skills/sleuths/SKILL.md` to describe filter → batch summarize → recursive reduce at a high level
- [ ] 4.3 Update `AGENTS.md` sleuths section if behavior description needs adjustment

## 5. Verification

- [ ] 5.1 Build sleuth binary via `scripts/build-local-tools.sh`
- [ ] 5.2 Manual smoke test: refresh a sleuth against a real transcript segment; confirm bounded summary, far fewer inference calls than per-chunk path, checkpoint advances
- [ ] 5.3 Manual smoke test: incremental refresh with existing summary confirms prior content preserved through merge seed

## Explicitly deferred

- Model-specific tokenizer integration for exact token counts
- Persisting intermediate relevance/summary artifacts for debugging
- Parallel inference calls across groups within a session
- Pipelined summarize while relevance is still running on later groups (phased processing is sufficient for v1)
