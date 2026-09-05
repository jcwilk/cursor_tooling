## 1. Update finish and apply agents

- [ ] 1.1 Rewrite `.cursor/agents/osf-apply-finish.md` so default success is verify → archive on working branch → commit → push working branch; move default-branch merge to explicit opt-in override only; verify agent description and debrief sections contain no default merge-to-main language
- [ ] 1.2 Update `.cursor/agents/osf-apply-start.md` finish delegation prompt to default push working branch only (no merge-to-main unless human override in same directive); verify `! rg -q 'merge into .main' .cursor/agents/osf-apply-start.md` or equivalent default-merge phrasing removed
- [ ] 1.3 Review `.cursor/agents/osf-apply-abort.md` so default-branch checkout remains cleanup-only and debrief still forbids merging working branch into default; verify no new merge-on-abort language

## 2. Update orchestration and persist skills

- [ ] 2.1 Update `.cursor/skills/osf-apply-changes/SKILL.md` finish outcome row and any merge-to-main wording to match working-branch finish default; verify `! rg -qi 'merges into .main' .cursor/skills/osf-apply-changes/SKILL.md`
- [ ] 2.2 Strengthen `.cursor/skills/persist/SKILL.md` to state persist pushes current branch only and never implies default-branch merge or finish; verify persist rules remain consistent with finish agent
- [ ] 2.3 Update `.cursor/skills/osf-propose/SKILL.md` persist/debrief references so propose-time push guidance does not imply finish will merge to default branch; verify hard-stop list still forbids propose from archiving/merging without explicit human ask

## 3. Update bundle documentation

- [ ] 3.1 Update `AGENTS.md` reconcile section and git posture to describe finish as archive-on-working-branch with optional explicit default-branch integration, not automatic default-branch merge; verify `! rg -q 'merges the execution branch into the .default branch' AGENTS.md` for the old automatic wording
- [ ] 3.2 Update `OPENSPEC_FLOW.md` capability table, apply-complete vocabulary (archive-complete vs apply-complete), and standard flow to remove default-branch merge as default finish outcome; verify table row for `/osf-apply-finish` no longer says merge default branch by default
- [ ] 3.3 Hand-update `.cursor/skills/osf-propose/reference/concepts.md` workflow substitution paragraphs that describe atomic merge into `main` so they match working-branch finish default (do not blind-clobber from upstream)

## 4. Verification

- [ ] 4.1 Run `rg -n 'merge.*main|main.*merge|default branch' .cursor/skills/osf-apply-changes .cursor/skills/persist .cursor/skills/osf-propose .cursor/agents/osf-apply-finish.md .cursor/agents/osf-apply-start.md AGENTS.md OPENSPEC_FLOW.md` and confirm remaining hits are opt-in override docs or propose-lane prohibitions only
- [ ] 4.2 Run `npx @fission-ai/openspec@latest validate finish-without-default-branch-merge --type change` and confirm it passes

## Explicitly deferred

- Bumping `OPENSPEC_FLOW_VERSION` / `CHANGELOG.md` (bundle semver entry can ride with apply commit or a follow-up human request).
