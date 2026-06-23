## Why

OSF apply skills currently prescribe branch/worktree isolation and parallel orchestration that humans now handle before invoking apply, making the skills longer and duplicative. Separately, agents have jumped from `/osf-propose` straight into editing bundle files (skills, agents, flow docs) because the propose lane lacks an upfront writable-scope lock and the flow narrative does not state forbidden lane transitions.

## What Changes

- **Simplify apply orchestration:** `osf-apply-changes` and `osf-apply-start` work on the **current branch** only; remove branch/worktree setup and parallel-multi-change guidance; tighten token count and reduce duplication with the worker agent while keeping Task-only delegation and the task-prompt contract handoff.
- **Align finish/abort terminology:** Rename “execution branch” to **working branch** where apply no longer creates branches; drop worktree-path inputs that implied apply-time isolation.
- **Propose lane lock (1A):** Add an upfront **Lane lock** section to `osf-propose` stating writable scope is only the active change folder and the healthy end state is validated artifacts—not edited skills or bundle docs.
- **Flow forbidden transitions (3):** Document in `OPENSPEC_FLOW.md` which lane transitions are forbidden (e.g. `/osf-propose` → direct `.cursor/**` or bundle doc edits).
- **Normative guard (4):** Add a living-spec delta requiring proposal shaping not mutate OSF implementation surfaces until an approved apply run executes tasks.
- Bump **`OPENSPEC_FLOW_VERSION`** and **`CHANGELOG.md`** when bundle edits land.

**Explicitly out of scope for this change** (human declined): expanded do-not-implement path lists in `osf-propose`, not-a-bypass table, combined propose+apply clarification, turn success criterion block, `AGENTS.md` slash-command section, `osf-apply-changes` anti-propose guard, `osf-propose` frontmatter description edit.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `openspec-flow-reference`: Add requirement that proposal shaping must not mutate OSF implementation surfaces before apply; add requirement that apply workers use current-branch context without creating isolation or parallel apply lanes in OSF apply skills.

## Impact

- `.cursor/skills/osf-apply-changes/SKILL.md`
- `.cursor/agents/osf-apply-start.md`
- `.cursor/agents/osf-apply-finish.md` (terminology alignment)
- `.cursor/agents/osf-apply-abort.md` (terminology alignment)
- `.cursor/skills/osf-propose/SKILL.md` (lane lock section only)
- `OPENSPEC_FLOW.md` (forbidden transitions + apply flow wording)
- `OPENSPEC_FLOW_VERSION`, `CHANGELOG.md`

No runtime services; bundle consumers inherit on install/upgrade.
