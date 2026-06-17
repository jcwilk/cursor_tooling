## 1. Processing configuration

- [ ] 1.1 Add `relevance_max_completion_tokens` (default 200) and `summary_max_completion_tokens` (default 1000) to `ProcessingConfig`
- [ ] 1.2 Parse new fields from `.sleuths/config.yaml` `processing` section in `load_config`
- [ ] 1.3 Lower default `pass_summary_cap_tokens` and `final_summary_target_tokens` from 2000 to 1000

## 2. Inference client

- [ ] 2.1 Extend `InferenceClient.generate` to accept a completion token limit and pass it to backend request bodies (`num_predict` for Ollama, `max_tokens` for OpenAI chat)
- [ ] 2.2 Unit tests: Ollama and OpenAI chat request bodies include the limit when provided

## 3. Pipeline wiring

- [ ] 3.1 Pass `relevance_max_completion_tokens` from relevance pass `generate` calls
- [ ] 3.2 Pass `summary_max_completion_tokens` from summarize and merge `generate` calls (intra-segment and cross-segment)
- [ ] 3.3 Integration or unit tests confirming stage-appropriate limits are used per inference stage

## 4. Documentation and verification

- [ ] 4.1 Document new processing fields and updated defaults in `.cursor/skills/sleuths/SKILL.md`
- [ ] 4.2 Run sleuth unit tests; rebuild CLI via `scripts/build-local-tools.sh`
- [ ] 4.3 Smoke dry-run on a short session to confirm relevance and summarize calls complete without runaway output

## Explicitly deferred

- Client-side retry when a completion hits the token limit mid-sentence
- Per-model automatic limit tuning
