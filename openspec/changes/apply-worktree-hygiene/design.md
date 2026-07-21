## Context

Apply finish already fails closed on missing operational evidence and reports leftover `git status` paths as warnings. That still allows “Apply Complete” while agent-created scratch (in-repo tool homes, `./tmp` drivers) remains. Humans asked for hygiene inside **apply-complete**—no new completion mechanism—and for cleanup that **commits or reverts** agent work rather than aborting on dirt.

## Goals / Non-Goals

**Goals:**

- Fold “left the worktree no dirtier from this apply unit” into **apply-complete**.
- Put portable scratch/cleanup guidance in apply agent/skill surfaces (start owns prevention + cleanup; finish owns verification before labeling apply-complete).
- Resolve apply-attributable leftovers by **incorporate (commit) or discard**—not abort-as-default.
- Ignore unrelated concurrent worktree changes from other agents/users/processes.

**Non-Goals:**

- A separate “workspace-complete” signal or new OSF lifecycle role.
- Failing closed on every dirty tree (pre-existing or foreign dirt).
- Forcing every disposable live-acceptance helper into checked-in reusable harnesses.
- Automated worktree inventory tooling or snapshot files as a required mechanism (agent judgment + git status is enough unless apply invents something lighter later).
- Project-specific allowlist registries in living specs (guidance lives in skills/agents; projects may still document their own intermediate dirs).

## Decisions

1. **Apply-complete owns hygiene**  
   Extend the existing apply-complete vs merge-complete contract. Merge/archive may still succeed in edge cases, but workers MUST NOT describe the unit as apply-complete while apply-attributable leftovers remain.  
   *Alternatives considered:* separate workspace-complete vocabulary (rejected—new mechanism); warn-only (status quo; rejected).

2. **Guidance home = apply agents/skills**  
   Primary text in `osf-apply-start` (prevention, classify dirt, commit-or-discard, handoff notes). Finish verifies hygiene and refuses apply-complete labeling when unresolved apply-attributable leftovers remain. Orchestrator skill may pass a one-line reminder in the Task prompt contract. Narrative touch in `OPENSPEC_FLOW.md`.  
   *Alternatives considered:* normative allowlists only in `AGENTS.md` (projects vary; portable defaults belong in the bundle apply surfaces).

3. **Commit or discard, do not abort for leftovers**  
   Abort remains for intent/safety blockers. Leftover agent scratch is a cleanup duty: keep and commit if it belongs to the change; otherwise delete/revert.  
   *Alternatives considered:* finish fail-closed that forces abort (rejected—disappointing and unnecessary when discard works).

4. **Scratch placement**  
   Prefer project-documented intermediate/build locations; if none, use OS temporary directories (e.g. under the system temp area). Never invent new top-level or ad-hoc repo-relative cache homes for package-manager registries.  
   *Alternatives considered:* hard empty allowlist with inventory gate (heavier than needed given commit-or-discard).

5. **Disposable helpers allowed**  
   Prefer reusable harnesses when investment pays off; ephemeral drivers are fine when one-off. Ephemeral means outside lasting source layout and discarded before apply-complete—not “leave `./tmp` for the human.”

6. **Attribution for concurrent dirt**  
   If the worker’s best understanding is that a path change came from unrelated concurrent work, exclude it from cleanup (do not commit, discard, or “fix” it). Document the exclusion in finish verification notes / debrief warnings so humans see it.

## Risks / Trade-offs

- **[Mis-attribution]** Agent wrongly treats foreign dirt as its own and discards it → Mitigation: bias toward exclusion when uncertain; never discard paths the unit did not create/touch unless clearly apply scratch from this run.
- **[Mis-attribution opposite]** Agent leaves its own scratch claiming “foreign” → Mitigation: finish checks unexplained new untracked/uncommitted paths against verification notes; require explicit exclusion rationale for leftovers left in place.
- **[Root-owned caches]** Discard may need elevated permissions → Mitigation: placement rule avoids in-repo caches; if stuck, surface in debrief (still not “success with silence”).
- **[Judgment load]** No mechanical pre/post inventory → Mitigation: acceptable per non-goals; keep guidance short and fail-closed on unlabeled leftovers at finish.

## Migration Plan

- Documentation/agent edits only; no data migration.
- Bump `OPENSPEC_FLOW_VERSION` and `CHANGELOG.md` when apply lands.
- Consumers pick up via `/openspec-flow-install` upgrade.

## Open Questions

- None blocking; apply may tighten finish wording if warn-vs-refuse phrasing needs one more pass during implementation.
