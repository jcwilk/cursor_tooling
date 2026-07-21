## Why

OSF apply can report apply-complete after archive and merge while leaving agent-created scratch (tool caches, one-off drivers) as untracked or uncommitted worktree entropy. Finish already warns on dirty `git status` but does not treat that entropy as part of apply-complete, so humans must clean up after a “successful” run.

## What Changes

- Extend **apply-complete** so it includes resolving **apply-attributable** worktree leftovers (commit what belongs to the change, discard the rest)—no new completion vocabulary.
- Codify scratch location guidance for apply workers in OSF apply agent/skill surfaces (prefer project-documented intermediate dirs; otherwise OS temp), without forcing every disposable helper into the permanent tree.
- Require finish to refuse apply-complete labeling when apply-attributable leftovers remain unresolved.
- Explicitly exclude unrelated concurrent worktree changes (other agents/users/processes) from apply hygiene obligations so parallel workstreams are not derailed.
- **Non-goal:** aborting solely because leftovers exist when incorporate-or-discard remains available.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `openspec-flow-reference`: Expand apply-complete (vs merge-complete) to include worktree hygiene for apply-attributable changes; add worker obligations for scratch placement, leftover resolution, and exclusion of unrelated concurrent dirt.

## Impact

- Bundle docs: `OPENSPEC_FLOW.md` apply-complete narrative.
- Apply agents/skills: `.cursor/agents/osf-apply-start.md`, `.cursor/agents/osf-apply-finish.md`, and apply orchestration guidance as needed for handoff/verification notes.
- Version bump / changelog when apply ships the bundle behavior.
- No runtime product APIs; process-contract only for OSF workers.
