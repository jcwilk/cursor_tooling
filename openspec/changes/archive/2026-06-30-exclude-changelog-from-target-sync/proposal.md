## Why

The install skill still listed `CHANGELOG.md` among paths propagated to consumer targets. That file records **OSF reference bundle** release history for this repository, not the consumer project's own changelog. Copying it misleads operators and pollutes target repos with irrelevant version notes.

## What Changes

- Move bundle release history out of the consumer propagation inventory in the install skill (align with install skill and sleuths exclusions).
- Add a living-spec requirement that OSF target sync must not propagate reference-bundle release history to consumers.
- Extend operator-documentation requirement to cover this exclusion alongside install tooling and sleuths.
- **BREAKING (behavioral):** Consumers that received `CHANGELOG.md` from prior sync will no longer get updates; operators may remove stale copies manually.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `openspec-flow-target-sync`: Add bundle-release-history exclusion; extend operator-documentation requirement.

## Impact

- **`.cursor/skills/openspec-flow-install/SKILL.md`** — inventory, rationale, rsync helper (partial direct edit exists; reconcile on apply).
- **`openspec/specs/openspec-flow-target-sync/spec.md`** — via archive after apply.
- No change to consumer `AGENTS.md` beyond what install already copies; reference `CHANGELOG.md` stays in this repo only.
