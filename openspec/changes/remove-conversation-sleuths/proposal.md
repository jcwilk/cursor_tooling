## Why

Conversation sleuths (transcript summarization lenses, local CLI, and `/sleuths` skill) are no longer part of the OSF reference bundle scope. Keeping the code, skills, living specs, and bundle documentation creates maintenance burden and confuses operators about what OSF ships to consumer projects.

## What Changes

- **BREAKING** — Remove the conversation-sleuths capability entirely: Python package, `/sleuths` skill, companion scripts, and all bundle references.
- **BREAKING** — Retire the `context-budget-grouping` living spec (only consumed by sleuth refresh; no remaining bundle behavior).
- Update `openspec-flow-target-sync` to drop sleuth-specific propagation exclusions and narrow operator-documentation requirements accordingly.
- Remove sleuth guidance from `AGENTS.md`, `README.md`, `OPENSPEC_FLOW.md`, `CHANGELOG.md`, and the install skill.
- Bump `OPENSPEC_FLOW_VERSION` to **1.6.0**.
- **Out of scope:** archived change folders under `openspec/changes/archive/` that document sleuth history remain untouched.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `conversation-sleuths`: Retire the entire capability — all requirements removed.
- `context-budget-grouping`: Retire the entire capability — all requirements removed.
- `openspec-flow-target-sync`: Remove sleuth propagation exclusions; update operator-documentation requirement to cover only install tooling and bundle release history.

## Impact

- **Removed paths:** `.cursor/skills/sleuths/`, `scripts/build-local-tools.sh`, `scripts/debug-sleuth-refresh-probe.sh`
- **Edited bundle docs:** `AGENTS.md`, `README.md`, `OPENSPEC_FLOW.md`, `CHANGELOG.md`, `.cursor/skills/openspec-flow-install/SKILL.md`
- **Edited repo hygiene:** `.gitignore` (drop machine-local sleuth state path), `.cursor/setup-worktree-unix.sh` (stop copying sleuth config between worktrees)
- **Living specs retired on archive:** `openspec/specs/conversation-sleuths/`, `openspec/specs/context-budget-grouping/`
- **Dependencies removed:** Python sleuth package (LangGraph, requests, etc.); no replacement tooling in bundle
