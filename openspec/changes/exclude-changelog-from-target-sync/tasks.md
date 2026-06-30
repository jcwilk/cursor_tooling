## Required for this change

## 1. Install skill

- [x] 1.1 Confirm `.cursor/skills/openspec-flow-install/SKILL.md` lists bundle release history (`CHANGELOG.md`) under **Reference repository only (never propagate)** — not under propagated paths.
- [x] 1.2 Confirm install skill rationale, upgrade stale-copy note, and optional rsync helper exclude release history from default sync.
- [x] 1.3 Reconcile any gaps vs the direct edit already in working tree.

## 2. Verification

- [x] 2.1 Re-read install inventory against delta spec scenarios (default install/upgrade must not propagate reference-bundle release history).
- [x] 2.2 Run `npx @fission-ai/openspec@latest validate exclude-changelog-from-target-sync --type change`.

## Explicitly deferred

- Automated deletion of stale `CHANGELOG.md` on consumer projects synced before this change.
