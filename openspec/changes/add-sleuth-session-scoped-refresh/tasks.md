## 1. CLI options

- [ ] 1.1 Add `--session <transcript_id>` to `sleuth refresh` (requires `--sleuth`; incompatible with `--all`)
- [ ] 1.2 Add `--dry-run` to `sleuth refresh` only (not reset or other subcommands)
- [ ] 1.3 Validate CLI combinations: `--session` without `--sleuth`, `--session` with `--all` → error

## 2. Session-scoped refresh and reprocess

- [ ] 2.1 Filter discovered segments by session identifier before pending-work resolution
- [ ] 2.2 When session scope is set, treat all segments in that session as pending from line 1 (ignore checkpoint line_count for those segments)
- [ ] 2.3 Error when no segments match session id (before inference)
- [ ] 2.4 Non-dry-run: update checkpoint only for reprocessed session segments; merge into existing summary at finalize

## 3. Dry-run orchestration

- [ ] 3.1 Thread dry-run flag through refresh orchestration; guard all checkpoint and summary writes
- [ ] 3.2 On successful finalize in dry-run, print full summary document (header + body) to stdout
- [ ] 3.3 Keep progress and inference call counts on stderr in dry-run
- [ ] 3.4 Verify dry-run suppresses disk writes even when combined with `--session`

## 4. Tests

- [ ] 4.1 Unit test: session filter limits segments; other sessions' checkpoints untouched (non-dry-run)
- [ ] 4.2 Unit test: session scope reprocesses from line 1 when checkpoint shows complete
- [ ] 4.3 Unit test: dry-run does not write checkpoint or summary; stdout contains summary body
- [ ] 4.4 Unit test: dry-run + session scope reprocesses without persistence
- [ ] 4.5 Unit test: unknown session id errors before inference
- [ ] 4.6 Regression: existing sleuth test suite passes

## 5. Documentation

- [ ] 5.1 Document `--session`, implicit reprocess, and `--dry-run` in `.cursor/skills/sleuths/SKILL.md`
- [ ] 5.2 Update `AGENTS.md` conversation sleuths section if refresh invocation is described there
- [ ] 5.3 Rebuild local sleuth CLI via `scripts/build-local-tools.sh`

## Explicitly deferred

- Session-scoped `reset` subcommand — out of scope for v1.
- Multiple `--session` values in one command — out of scope for v1.
