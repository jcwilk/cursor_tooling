## Context

Apply skills (`osf-apply-changes`, `osf-apply-start`) were authored when OSF owned branch/worktree isolation and optional parallel multi-change orchestration. Humans now set branch/worktree and concurrency **before** invoking apply. The skills are ~160 lines combined with duplicated handoff rules.

A separate failure mode: `/osf-propose` with a concrete bundle-edit brief led an agent to edit `.cursor/**` directly. Existing `osf-propose` rules mention apply vs propose but lack an upfront **lane lock**; `OPENSPEC_FLOW.md` does not list forbidden lane transitions; the living spec covers archival isolation but not implementation-surface isolation.

## Goals / Non-Goals

**Goals:**

- Apply skills assume **current branch**; no branch creation, worktree add, or parallel-change spawning inside OSF apply.
- Shorter `osf-apply-changes` (orchestration + Task prompt contract + handoff only); worker owns orient/loop/evidence/delegate.
- `osf-propose` opens with **Lane lock**: writable = active `openspec/changes/<name>/` only; end state = validated change folder + explain debrief.
- `OPENSPEC_FLOW.md` documents **forbidden transitions** between slash lanes.
- Living spec adds normative requirements for propose writable scope and apply branch context.
- Align finish/abort agents to **working branch** terminology (no apply-time worktree inputs).

**Non-Goals:**

- Expanded do-not-implement path lists, not-a-bypass tables, combined propose+apply phrasing rules, turn success criterion block, `AGENTS.md` slash section, `osf-apply-changes` anti-propose guard, or `osf-propose` frontmatter description changes (human declined).
- Changing Task-only apply delegation, task-class evidence rules, or operational completeness gates.

## Decisions

### Apply simplification shape

Mirror the prior draft structure: ~50-line orchestrator skill, ~100-line worker agent. Remove: Step 1 isolation, parallel section, branch/worktree prompt fields, verbose output templates. Keep: Task-only rules, wait-for-subagent, task prompt contract (parent), task classes + loop (worker), finish/abort delegation.

**Rationale:** Duplication stays only on the critical parent→worker handoff (`tasks.md` floor); worker references parent's contract instead of repeating the full forbidden/allowed table.

### Lane lock placement

Insert **Lane lock** immediately after the opening paragraph in `osf-propose/SKILL.md`, before "Required reading before drafting."

**Rationale:** Agents that skim or stop early must see writable scope before planning edits. Persist-section rules arrive too late.

### Forbidden transitions in OPENSPEC_FLOW

Add a short subsection after **Standard flow** (or within it) listing:

- `/osf-propose` → direct edits outside active change folder ❌
- `/osf-propose` → `openspec/changes/<name>/` artifacts only ✅
- Bundle/integration paths → apply via approved `tasks.md` after review ✅

Update capability table and standard-flow step 3 to say **current branch** (branch/worktree choice is a precondition).

### Living spec: ADDED not MODIFIED

Add two new requirements under `openspec-flow-reference` rather than modifying "Isolation between proposal shaping and archival reconciliation" — that requirement targets `openspec/specs/` reconciliation; the new concern is implementation-surface mutation and apply branch context.

## Risks / Trade-offs

- **[Risk] Agents still bypass propose for "obvious" bundle edits** → Lane lock + forbidden transitions + normative spec; no silver bullet without declined AGENTS.md slash section.
- **[Risk] Consumers relied on apply skills to create `apply/<name>` branches** → Document in design/tasks that precondition is human responsibility; `OPENSPEC_FLOW.md` prerequisites already mention git.
- **[Trade-off] Shorter skills may omit edge-case examples** → Keep compact forbidden/allowed table (3 rows) in orchestrator only.

## Migration Plan

Single bundle release: apply edits land together; bump `OPENSPEC_FLOW_VERSION` and `CHANGELOG.md`. No consumer migration beyond reinstall/upgrade.

## Open Questions

None — declined optional guardrails are explicitly deferred.
