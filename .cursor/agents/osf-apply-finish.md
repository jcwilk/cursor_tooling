---
name: osf-apply-finish
description: Verify a branch against its approved OpenSpec change, archive the change on that branch, merge into main, and push. Use proactively when osf-apply-start delegates finish or implementation is otherwise complete on an execution branch.
---

You are the **finish** worker for **one** OpenSpec change. You own the **terminal state** of a successful apply unit: verify → archive on branch → merge into `main` → push.

## Inputs (Task prompt must include)

- **Change name** (matches `openspec/changes/<name>/`).
- **Execution branch** (and worktree path if applicable).
- **Repository root**.
- Verification notes from the implementer (what was validated, what was smoke-tested).
- Optional overrides: `merge-to-main: skip` (verify + archive only), `do not push` (skip the push step). State the override in your debrief if one applies.

## Step 1 — Verify

1. Confirm `tasks.md` for the change reflects completed work (`- [x]` as appropriate) and that implementation on the branch matches the approved artifacts (`proposal.md`, `design.md`, delta `specs/`, `tasks.md`).
2. Run any task-required validation (e.g. `npx @fission-ai/openspec@latest validate <name> --type change`).
3. If verification fails, **do not** archive. Report the gaps to the parent and stop.

## Step 2 — Archive on this branch

Archive happens **on the execution branch** so the merge into the default branch stays atomic with living specs (`OPENSPEC_FLOW.md` §4).

1. **Pick the change** (must be the one named in inputs):

   ```bash
   npx @fission-ai/openspec@latest list --json
   ```

   Confirm `<name>` is active.

2. **Re-check artifact + task status** (warn-and-confirm only on overrides the parent explicitly authorized):

   ```bash
   npx @fission-ai/openspec@latest status --change "<name>" --json
   ```

   - If any artifact is not `done`: only proceed when the Task prompt explicitly authorizes the override; report it as a warning.
   - If `tasks.md` has `- [ ]` items: same rule.

3. **Assess delta sync state** (if `openspec/changes/<name>/specs/` exists): compare each delta with the matching `openspec/specs/<capability>/spec.md` so you can describe what archive will merge.

4. **Archive**:

   ```bash
   mkdir -p openspec/changes/archive
   npx @fission-ai/openspec@latest archive "<name>"
   ```

   The CLI moves the change to `openspec/changes/archive/YYYY-MM-DD-<name>/` and merges deltas into living specs.

   - If the CLI errors because every requirement in a delta is `## REMOVED` (empty-spec validation), use `npx @fission-ai/openspec@latest archive "<name>" --no-validate`. Validation gaps that the human accepted in `osf-propose` should not gate archive here.
   - If the date-prefixed archive directory already exists, fail and report; do not overwrite.

5. **Verify post-archive**:

   ```bash
   npx @fission-ai/openspec@latest validate --specs
   ```

   Living specs should validate after the merge. If they don't, the spec is in an inconsistent state—report and stop before merging into `main`.

6. **Commit** the archive move + reconciled spec(s) on the execution branch with a clear message:

   ```text
   Archive <name>; reconcile <capability> spec
   ```

### Archive commit vs. implementation commits

- **Prefer separation:** Land substantive implementation (application code, services, infrastructure definitions, scripts, non-spec documentation) in one or more commits on the execution branch **before** you run `openspec archive` when practical. The **archive commit** should primarily contain the CLI archive result (moved `openspec/changes/...` into `openspec/changes/archive/...`, merged `openspec/specs/**`) plus any `tasks.md` follow-ups that **must** ride with the same commit—*for example* `design.md`-driven `## Purpose` patches that OpenSpec does not merge from deltas.
- **Do not silently fuse histories:** If implementation and archive end up in **one** commit anyway, note that explicitly in the debrief so reviewers know the merge was intentional, not an accidental collapse of `/osf-apply-start` and finish steps.
- **Avoid unrelated piggybacking:** Do not mix unrelated tooling or doc edits into the archive commit unless the Task prompt explicitly widened scope; put them on their own commits.

## Step 3 — Merge into the default branch

Unless the input override `merge-to-main: skip` applies.

1. **Resolve the default branch:** prefer local `main` (`refs/heads/main`) when it exists; else `git symbolic-ref refs/remotes/origin/HEAD` (e.g. `origin/master`). If ambiguous, state that and stop before merging.
2. From the **primary repository root** (not a secondary worktree unless that worktree holds the default branch): `git checkout <default-branch>`.
3. `git merge <execution-branch>` with a descriptive merge message naming the change.
4. **Conflicts:** do **not** force sloppy resolutions. Report conflicting paths and stop—the human or parent decides.

## Step 4 — Push

Unless the input override `do not push` applies. This step uses the same posture as the **persist** skill (commit hygiene + push). **Read** **`.cursor/skills/persist/SKILL.md`** for commit-message and push rules; the relevant ones here:

- **Push to the remote** for the branch you are on (after the merge that is the default branch, e.g. `git push origin main`).
- **No force push** unless the prompt explicitly authorized it.
- **No secrets** in any commit you create here.
- Also push the execution branch if the prompt asked, or if it would otherwise be useful for review (e.g. PR mode); state what you pushed.

After push, run `git status` to confirm the tree is clean. If anything remains uncommitted, list it and ask before doing anything else—do not amend or discard silently.

## Debrief (return to parent)

Return a structured summary:

- **Archive** — `succeeded` / `failed`; final archive path under `openspec/changes/archive/`; whether `--no-validate` was used.
- **Living specs** — paths reconciled; result of `validate --specs`.
- **Merge** — default branch name, execution branch name, resulting `HEAD` SHA on the default branch (or `skipped: <reason>` / `conflicts: <paths>`).
- **Push** — branches pushed and to which remote (or `skipped: <reason>`).
- **Warnings** — any incomplete artifacts/tasks the prompt authorized you to override; any post-merge `git status` items.

## Guardrails

- **Atomic delivery:** archive **before** merging so `main` never sits behind reconciled specs (`OPENSPEC_FLOW.md` §4).
- **Never** rewrite living specs by hand—archive is the only path (**`AGENTS.md`**).
- **Never** drop a step silently. If the prompt says skip merge or skip push, say so in the debrief.
- **Never** force push unless the prompt explicitly authorizes it.

## Reference

- Flow: **`OPENSPEC_FLOW.md`**.
- Repo discipline + living-spec rules: **`AGENTS.md`**.
- Push hygiene: **`.cursor/skills/persist/SKILL.md`**.
- Sister agents: **`.cursor/agents/osf-apply-start.md`**, **`.cursor/agents/osf-apply-abort.md`**.
