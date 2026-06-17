## 1. CLI and refresh filtering

- [ ] 1.1 Add `--session <transcript_id>` option to `sleuth refresh` (requires `--sleuth`; incompatible with `--all`)
- [ ] 1.2 Validate: error when `--session` used without `--sleuth` or with `--all`
- [ ] 1.3 Filter discovered segments by session identifier before pending-work resolution
- [ ] 1.4 Error when no segments match the session id; stderr message when session has nothing pending

## 2. Orchestration

- [ ] 2.1 Pass session scope through `refresh_sleuth` → `_refresh_sleuth_with_config`
- [ ] 2.2 Confirm collect → finalize and checkpoint behavior unchanged except for filtered segment set
- [ ] 2.3 Ensure subagent jsonl files under the session are included (no change to discovery key semantics)

## 3. Tests

- [ ] 3.1 Unit test: session filter limits segments processed; other sessions' checkpoints untouched
- [ ] 3.2 Unit test: subagent segments share parent session id and are included
- [ ] 3.3 Unit test: unknown session id errors before inference
- [ ] 3.4 Regression: existing sleuth test suite passes

## 4. Documentation

- [ ] 4.1 Document `--session` in `.cursor/skills/sleuths/SKILL.md` with example
- [ ] 4.2 Update `AGENTS.md` conversation sleuths section if refresh invocation is described there
- [ ] 4.3 Rebuild local sleuth CLI via `scripts/build-local-tools.sh`

## Explicitly deferred

- `--reprocess` to ignore checkpoint for a scoped session — out of scope for v1.
- Session-scoped `reset` subcommand — out of scope for v1.
