# Agents and OpenSpec Flow

This file is the **operational contract** for agents working in a repository that ships or consumes the OpenSpec Flow bundle. Project owners may extend it with domain rules (security, environments, release process).

## OpenSpec directory discipline

- **Living specs** under **`openspec/specs/`** change **only** through the OpenSpec **archive** path driven by **`osf-apply-finish`** (or an equivalent explicit human-run archive with the same outcome). Do not hand-edit living specs to “catch up” implementation.
- **Intent** during apply lives under **`openspec/changes/<name>/`**. During **`osf-apply-start`**, routine edits there are **`tasks.md` checkboxes** only unless the human explicitly widens scope.
- Skills **`/osf-propose`** and **`/osf-explore`** must not merge to the default branch or archive changes **unless** the human clearly asked for apply/finish in the same turn.

## Task delegation

- **Chat skills** live under **`.cursor/skills/*/SKILL.md`** — they steer the conversational agent’s procedure.
- **Task agents** live under **`.cursor/agents/<name>.md`** — Cursor runs them via the **Task** tool with **`subagent_type`** equal to **`name`**. Opening an agent definition and replaying its steps in the chat **breaks isolation**; see **`.cursor/skills/spawn-subagent/SKILL.md`**.

OSF apply workers MUST use Tasks:

- **`osf-apply-start`**, **`osf-apply-finish`**, and **`osf-apply-abort`** MUST be invoked via the **Task** tool with the matching **`subagent_type`**. Do not read **`.cursor/agents/osf-*.md`** and replay them in the parent thread.
- Follow **`.cursor/skills/spawn-subagent/SKILL.md`** and **`.cursor/skills/osf-apply-changes/SKILL.md`**.

## Git branches and default branch

Unless the user explicitly asks otherwise: **commit and push on the current working branch** for day-to-day work. **`osf-apply-finish`** merges the execution branch into the repository’s **default branch** when completing a change—only do that within that finish workflow or when the user explicitly requests it.

## Safety and environments

- No destructive actions on machines, data, or shared infrastructure **unless** the human named the target and risk is acceptable.
- Honor project-specific allowlists, staging requirements, and secrets handling; when in doubt, stop and ask.

## Environment

Use **`.env`** for local secrets (API keys for optional tools). **`.env`** should remain gitignored in consuming projects.

## Reference

- **`OPENSPEC_FLOW.md`** — narrative, vocabulary, and **`OPENSPEC_FLOW_VERSION`** for the bundle.
- **`.cursor/skills/openspec-flow-install/SKILL.md`** — install or upgrade this bundle into another project.
