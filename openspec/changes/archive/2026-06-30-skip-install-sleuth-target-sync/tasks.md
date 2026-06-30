## Required for this change

## 1. Install skill inventory and sync behavior

- [x] 1.1 Restructure `.cursor/skills/openspec-flow-install/SKILL.md` bundle inventory into **Propagated to consumer targets** vs **Reference repository only (never propagate)** sections.
- [x] 1.2 Move `openspec-flow-install` and `sleuths` skills (and `scripts/build-local-tools.sh`) into the reference-only section with explicit rationale.
- [x] 1.3 Add a clear statement that the install skill itself is reference-repository-only and MUST NOT be copied to consumer projects.
- [x] 1.4 Update install, upgrade, and optional rsync helper sections so default sync excludes reference-only paths.
- [x] 1.5 Remove post-sync reminders to run `build-local-tools.sh` for sleuths on consumer targets.

## 2. Contributor documentation

- [x] 2.1 Add in-development / do-not-deploy-to-external-projects guidance to the Conversation sleuths section of `AGENTS.md`.
- [x] 2.2 Add a brief reference-repo-only note for `/sleuths` in the `OPENSPEC_FLOW.md` capabilities table (if not already present after 1.x edits).

## 3. Verification

- [x] 3.1 Re-read install skill inventory against delta spec scenarios: default install/upgrade must not list excluded paths as propagated.
- [x] 3.2 Run `npx @fission-ai/openspec@latest validate skip-install-sleuth-target-sync --type change` and fix any issues.

## Explicitly deferred

- Manual cleanup guidance for consumer projects that already received install/sleuths copies (documented in design.md; no automated deletion task).
