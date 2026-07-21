## Required for this change

## 1. Apply worker guidance

- [x] 1.1 Update `.cursor/agents/osf-apply-start.md` with scratch placement (project-documented intermediates, else OS temp; no ad-hoc in-repo cache homes), commit-or-discard cleanup before finish handoff, exclusion of unrelated concurrent dirt with debrief notes, and disposable-helper allowance without forcing lasting harnesses.
- [x] 1.2 Update `.cursor/agents/osf-apply-finish.md` so verification refuses apply-complete labeling when apply-attributable leftovers remain unresolved; require verification notes to list hygiene resolution or explicit exclusions; keep abort reserved for intent/safety blockers, not leftover cleanup.
- [x] 1.3 Add a brief hygiene reminder to `.cursor/skills/osf-apply-changes/SKILL.md` Task prompt contract (constraints only—do not soften approved tasks).

## 2. Flow narrative and release metadata

- [x] 2.1 Update `OPENSPEC_FLOW.md` apply-complete vs merge-complete so apply-complete includes resolving apply-attributable worktree leftovers (incorporate or discard) and notes exclusion of unrelated concurrent dirt.
- [x] 2.2 Bump `OPENSPEC_FLOW_VERSION` and add a `CHANGELOG.md` entry for this hygiene contract.

## 3. Validation

- [x] 3.1 Run `npx @fission-ai/openspec@latest validate apply-worktree-hygiene --type change` after edits and confirm agent/doc wording matches the delta requirements (no new completion vocabulary; no abort-on-leftovers default).

## Explicitly deferred

- None.
