## Context

Finish agent Step 3 merges the working branch into `main` by default; apply-changes documents that as the success path. `persist` already forbids merging into `main` unless the human asks, but finish contradicts that posture. See `proposal.md` for motivation.

## Goals / Non-Goals

**Goals:**

- Default finish ends on the working branch with archive committed and optionally pushed.
- All skill/agent prose consistently treats default-branch merge as **explicit human opt-in**, not silent success criteria.
- Living spec vocabulary: **archive-complete** (reconciled specs on working branch) vs **apply-complete** (archive-complete + task evidence + hygiene).

**Non-Goals:**

- Banning default-branch merge when a human explicitly requests it in the finish Task prompt.
- Changing OpenSpec CLI archive mechanics (still runs on the working branch).
- Rewriting archived change folders under `openspec/changes/archive/`.

## Decisions

### 1. Finish default: push working branch, not merge default branch

**Decision:** After archive commit on the working branch, push `origin/<working-branch>` when push is not waived. Remove default Step 3 merge-to-default.

**Rationale:** Matches user intent; keeps remote backup/review without forcing integration lane choice.

**Alternative considered:** Make push optional always — rejected; push remains default per existing persist hygiene unless `do not push`.

### 2. Opt-in override for default-branch merge

**Decision:** Retain an explicit finish prompt override (e.g. `merge-to-default-branch: yes` naming TBD in tasks) that runs checkout → merge → push default branch **only when the human named it in the same directive**.

**Rationale:** Preserves escape hatch without making it the default agent path.

### 3. Vocabulary shift: merge-complete → archive-complete

**Decision:** Update `openspec-flow-reference` requirement **Apply-complete distinct from merge-complete** to reference **archive-complete** (archive + living spec reconciliation on working branch). Scenarios that said “merges and archives” become “archives while…”.

**Rationale:** “Merge-complete” reads as git merge to main; archive is the meaningful OSF gate.

### 4. Abort agent: checkout default without merging working branch

**Decision:** Keep abort landing on default branch for a clean workspace; reinforce that abort never merges the working branch into default (already stated — ensure no regression).

## Risks / Trade-offs

- **[Risk] Consumers relied on finish to land on main** → Document breaking change in bundle changelog on apply; finish override documented in agent.
- **[Risk] Drift between concepts.md and skills** → Include concepts.md in apply tasks with hand-ported workflow text, not blind upstream clobber.

## Migration Plan

1. Apply updates skills/agents and bundle docs per `tasks.md`.
2. Archive this change via finish on the working branch (dogfooding new default).
3. Operators who want auto-merge-to-main add explicit finish prompt override or merge locally after push.

## Open Questions

None blocking propose.
