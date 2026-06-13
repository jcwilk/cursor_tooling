## 1. CLI reset operation

- [x] 1.1 Add `reset` subcommand to sleuth CLI with `--sleuth <id>` and `--all` selection (same mutual-exclusion rules as refresh)
- [x] 1.2 Implement reset handler that validates the sleuth id against the query definition, removes summary and checkpoint artifacts, and reports what was removed
- [x] 1.3 Ensure reset does not call the inference client
- [x] 1.4 Add unit tests for single-sleuth reset, reset-all, and idempotent reset when artifacts are absent

## 2. Documentation

- [x] 2.1 Document reset + refresh workflow in `.cursor/skills/sleuths/SKILL.md`

## 3. Verification

- [x] 3.1 Build release binary via `scripts/build-local-tools.sh`
- [x] 3.2 Smoke test: reset a sleuth with existing summary/checkpoint, then refresh; confirm full reprocessing (checkpoint starts empty, new summary produced)

## Explicitly deferred

- (none)
