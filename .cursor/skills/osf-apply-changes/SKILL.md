---
name: osf-apply-changes
description: Start implementation for one or more approved OpenSpec changes in isolated git branches or worktrees, using Task subagents. Use when the user says `/osf-apply-changes`, wants parallel workers, or is ready to execute after `/osf-propose`. Orchestrates `osf-apply-start`, `osf-apply-finish`, and `osf-apply-abort`; does not duplicate per-change apply mechanics.
disable-model-invocation: true
---

# `/osf-apply-changes` — implementation orchestration

This skill is **just orchestration**. Per-change implementation (branch setup, work queue, validation, finish/abort delegation) lives entirely inside the **`osf-apply-start`** agent.

## Non-negotiable: real subagents

Read **`.cursor/skills/spawn-subagent/SKILL.md`**.

### `osf-apply-start` is **Task-only** — **never** inline

- **`osf-apply-start` MUST be invoked only via the Task tool** (`subagent_type: osf-apply-start`, filename stem under **`.cursor/agents/`**).  
- **Never** re-execute the apply workflow **in the orchestrating (parent) thread**: no inline branch setup, no manual `tasks.md` / `openspec archive` / merge / push for the same change **as a substitute for** the subagent.  
- **Do not** open **`.cursor/agents/osf-apply-start.md`** and **replay** its steps in the parent thread — that **collapses isolation and duplicates ownership** and is **forbidden.**

### Wait for the subagent — **no silent takeover**

- After spawning **`osf-apply-start`**, the parent **must wait until that Task completes** (success or failure) before treating the apply as done or before doing **any** follow-up that **re-implements the same change**.  
- **Do not** continue in the parent with “I’ll finish the apply myself” because the Task is slow, quiet, or backgrounded. **The subagent owns the apply until it returns**; the parent does **not** pick up the work in parallel.  
- If the Task **blocks or appears hung**, **diagnose or escalate** (including checking subprocess/interactive prompts) — **do not** duplicate the **`osf-apply-start`** work stream in the foreground.  
- On **failure** or **abort** delegated from the worker, the path is **`osf-apply-abort`** / **`/osf-propose`** — **not** unilateral parent completion of the same intent.

### One change, one worker

Until the **`osf-apply-start`** Task returns, that run is the **sole** implementation lane for that change name. **No parallel implementation** of the same **`openspec/changes/<name>/`** in the parent thread.

## Single change

1. Confirm the change name and that intent is approved under `openspec/changes/<name>/`.
2. Spawn **one** Task with `subagent_type: osf-apply-start`. The prompt must be **self-contained**: repository root, change name, branch/worktree naming the human requested (or sensible defaults like `apply/<name>`), constraints from **`AGENTS.md`** (project safety boundaries, living-spec discipline), any validation expectations.
3. **Wait for that Task to finish**; then relay the worker’s debrief to the human (**see “Wait for the subagent”** above). **Do not** implement the same change in the parent while the Task runs.

## Multiple changes in parallel

**Only** when the user explicitly asks for parallel execution (or it is clearly intended): issue **multiple Task calls in one parent turn**, one **`osf-apply-start`** per change. Each gets an isolated branch/worktree and a self-contained prompt.

If intent is ambiguous, default to serial and say so.

## What the worker owns

The **`osf-apply-start`** agent does the entire apply pipeline for one change:

- Branch/worktree setup
- `openspec status` / `instructions apply` orientation
- Reading context artifacts and living specs
- Running the task work-queue and flipping `tasks.md` checkboxes
- Validating per `tasks.md`
- **Delegating finish or abort** before returning to you

This skill does **not** duplicate any of that.

## Finish and abort outcomes

The worker terminates by spawning one of these:

| Outcome | Subagent |
|---------|----------|
| Tasks complete and verified | **`osf-apply-finish`** — verifies, archives on the branch, merges into `main`, pushes |
| Approved change cannot continue as written | **`osf-apply-abort`** — rolls back, checks out `main`, returns extensive debrief; does **not** edit the change folder or merge unapproved work |

The worker returns the finish/abort debrief to **you** (the orchestrator). Pass it to the human verbatim.

After abort, intent fixes happen **only** through **`/osf-propose`** (`osf-propose`)—then a fresh **`/osf-apply-changes`** run.

## Reference

- Flow narrative: **`OPENSPEC_FLOW.md`**.
- Living vs change specs and `openspec/` discipline: **`AGENTS.md`**.
- Worker agent: **`.cursor/agents/osf-apply-start.md`**.
- Terminal agents: **`.cursor/agents/osf-apply-finish.md`**, **`.cursor/agents/osf-apply-abort.md`**.
- Upstream intent shaping: **`.cursor/skills/osf-propose/SKILL.md`** (and **`/osf-explore`** for thinking-first mode).
