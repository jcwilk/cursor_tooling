## 1. Remove sleuth implementation

- [x] 1.1 Delete `.cursor/skills/sleuths/` entirely and verify `test ! -d .cursor/skills/sleuths`
- [x] 1.2 Delete `scripts/build-local-tools.sh` and `scripts/debug-sleuth-refresh-probe.sh` and verify `test ! -e scripts/build-local-tools.sh && test ! -e scripts/debug-sleuth-refresh-probe.sh`

## 2. Update bundle documentation

- [x] 2.1 Remove the Conversation sleuths section from `AGENTS.md` and verify `! rg -qi sleuth AGENTS.md`
- [x] 2.2 Remove sleuth rows and prerequisites from `README.md` and verify `! rg -qi sleuth README.md`
- [x] 2.3 Remove `/sleuths` from the capability table in `OPENSPEC_FLOW.md` and verify `! rg -qi sleuth OPENSPEC_FLOW.md`
- [x] 2.4 Update `.cursor/skills/openspec-flow-install/SKILL.md` to drop sleuth and `build-local-tools.sh` from reference-only inventory and verify `! rg -qi sleuth .cursor/skills/openspec-flow-install/SKILL.md`

## 3. Repo hygiene and versioning

- [x] 3.1 Remove `.sleuths/` from `.gitignore` and remove `.sleuths` from `.cursor/setup-worktree-unix.sh` copy paths; verify `! rg -q '\\.sleuths' .gitignore .cursor/setup-worktree-unix.sh`
- [x] 3.2 Set `OPENSPEC_FLOW_VERSION` to `1.6.0` in `OPENSPEC_FLOW.md` and add a `1.6.0` removal entry to `CHANGELOG.md`; verify `grep 'OPENSPEC_FLOW_VERSION: "1.6.0"' OPENSPEC_FLOW.md`

## 4. Verification

- [x] 4.1 Run `rg -il sleuth --glob '!.sleuths/**' --glob '!.git/**' --glob 'openspec/changes/archive/**'` and confirm matches are limited to archived history and this change folder only
- [x] 4.2 Run `npx @fission-ai/openspec@latest validate remove-conversation-sleuths --type change` and confirm it passes

## Explicitly deferred

- Editing or deleting sleuth-related folders under `openspec/changes/archive/` (historical record; out of scope per design.md).
