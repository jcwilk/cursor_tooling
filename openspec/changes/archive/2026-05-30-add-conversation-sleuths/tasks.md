## 1. Gitignore and project hygiene

- [x] 1.1 Add `.sleuths/` to root `.gitignore`
- [x] 1.2 Add `.cursor/skills/sleuths/target/` (or equivalent per-crate target paths) to `.gitignore`

## 2. Rust summarization runner

- [x] 2.1 Create `.cursor/skills/sleuths/sleuth/` Cargo crate with CLI entrypoint
- [x] 2.2 Implement Cursor project slug derivation from `--project-root` (workspace + worktree paths)
- [x] 2.3 Implement transcript discovery: primary slug + `git worktree list` expansion + config `extra_transcript_slugs`
- [x] 2.4 Walk `agent-transcripts/**/*.jsonl` (parent + subagents), ordered by mtime
- [x] 2.5 Implement checkpoint read/write with `(transcript_id, relative_path, line_count)` granularity
- [x] 2.6 Implement JSONL → text extraction (user/assistant text; condensed tool_use representation)
- [x] 2.7 Implement map pass: Ollama HTTP call per chunk with sleuth query prompt (extract-only, preserve paths)
- [x] 2.8 Implement reduce pass: merge map output into existing `summary.md` with session/subagent tags
- [x] 2.9 Implement `refresh --sleuth <id>` and `refresh --all` subcommands; fail without advancing checkpoint on Ollama errors
- [x] 2.10 Load `.sleuths/config.yaml` for endpoint URL/model and optional slug overrides; require human-created config (no auto-generated defaults; sleuth never starts Ollama locally)

## 3. Local build tooling

- [x] 3.1 Add `.cursor/build-local-tools.sh` that builds all Rust crates under `.cursor/skills/*/`
- [x] 3.2 Document one-time build step in sleuths skill and/or README bundle table

## 4. Cursor skills

- [x] 4.1 Add `.cursor/skills/sleuths/SKILL.md` for establishing a new sleuth (human describes lens → write `.sleuths/queries/<id>.yaml` → initial refresh)
- [x] 4.2 Add refresh workflow to skill (or companion skill) for incremental `--sleuth` / `--all` refresh
- [x] 4.3 Include privacy warning: `.sleuths/` is gitignored and may contain secrets — do not commit

## 5. Agent guidance and bundle install

- [x] 5.1 Add AGENTS.md section: where summaries and query defs live, when agents should read them, refresh is human-only in v1
- [x] 5.2 Update `.cursor/skills/openspec-flow-install/SKILL.md` inventory to include sleuths skill, build script, and gitignore patterns
- [x] 5.3 Update `README.md` / `OPENSPEC_FLOW.md` capability table if the bundle documents shipped skills (optional short pointer)

## 6. Verification

- [ ] 6.1 Smoke test: with `.sleuths/config.yaml` pointing at the operator's inference endpoint (not localhost auto-start), create a sleuth and refresh; verify checkpoint advances on second refresh
- [ ] 6.2 Verify subagent jsonl under a session with Task history is processed when present
- [ ] 6.3 Verify refresh fails cleanly when the configured endpoint is unreachable (no checkpoint advance)

## 7. Archive (apply finish)

- [ ] 7.1 Run `/osf-apply-finish` to archive this change and merge `conversation-sleuths` spec into living specs
