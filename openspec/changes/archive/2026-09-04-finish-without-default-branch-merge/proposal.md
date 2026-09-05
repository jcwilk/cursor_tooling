## Why

OSF finish and related skills currently treat **merge into the default branch** as the normal successful outcome (`osf-apply-finish` Step 3, `osf-apply-changes` outcome table, `AGENTS.md`, `OPENSPEC_FLOW.md`). That pushes agents toward cross-branch merges many teams do not want automated. Remote **push of the working branch** is desirable; **default-branch merge** should be opt-in only when the human explicitly requests it.

## What Changes

- **BREAKING (behavioral)** — Redefine successful OSF finish as: verify → archive on the **working branch** → commit → **push the working branch** (when push is not waived). Default finish **does not** check out, merge into, or push the default branch.
- Update **`osf-apply-finish`**, **`osf-apply-start`**, **`osf-apply-changes`**, **`persist`**, and **`osf-propose`** skill text so none imply automatic default-branch merge.
- Update bundle docs **`AGENTS.md`** and **`OPENSPEC_FLOW.md`** (capability table, apply-complete vocabulary, standard flow).
- Refresh **`osf-propose/reference/concepts.md`** workflow substitution text where it still describes atomic merge into `main`.
- Replace **merge-complete** vocabulary with **archive-complete** where it meant “living specs reconciled on the working branch,” distinct from optional human-directed default-branch integration.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `openspec-flow-reference`: Finish and apply-complete contracts no longer require default-branch merge; push-on-working-branch is the default remote sync; default-branch merge is explicit opt-in only.

## Impact

- **Skills/agents:** `.cursor/skills/osf-apply-changes/SKILL.md`, `.cursor/skills/persist/SKILL.md`, `.cursor/skills/osf-propose/SKILL.md`, `.cursor/agents/osf-apply-finish.md`, `.cursor/agents/osf-apply-start.md`, `.cursor/agents/osf-apply-abort.md` (abort: clarify checkout-to-default is cleanup only, not merging working branch)
- **Bundle docs:** `AGENTS.md`, `OPENSPEC_FLOW.md`
- **Reference:** `.cursor/skills/osf-propose/reference/concepts.md` (workflow narrative only; not a living spec)
- **Consumers:** Teams using finish as implicit “merge to main” must pass an explicit override (documented in finish agent) or merge manually after push
