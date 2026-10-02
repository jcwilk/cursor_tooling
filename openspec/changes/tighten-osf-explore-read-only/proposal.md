# Proposal

## Why

Agents invoked under `/osf-explore` have edited OpenSpec change artifacts (for example aligning `proposal.md` after a schema decision) even though explore is meant to be a read-only thinking partner. The prior explore skill text allowed change-folder writes when the user explicitly asked to capture thinking, and later sections treated artifact updates as a normal successful outcome—so settled decisions were mistaken for permission to edit. Bundle narrative (`AGENTS.md`, `OPENSPEC_FLOW.md`) already describes explore as read-only, but living specs do not yet normatively separate the explore lane from proposal capture.

## What Changes

- **BREAKING (explore lane):** `/osf-explore` becomes conversation-only: no create, edit, move, or delete of any file, including everything under `openspec/changes/`. No exception for settled decisions, proposal mismatches, or explicit “just update the proposal” requests; hand off to `/osf-propose` instead.
- Rewrite `.cursor/skills/osf-explore/SKILL.md` to remove the capture table, “artifact updates” success outcome, and conditional permission to revise change artifacts.
- Add a living-spec requirement that OSF explore shaping MUST NOT mutate repository files and MUST route durable capture to proposal shaping.
- Align `OPENSPEC_FLOW.md` capability-table wording so “read-only” clearly includes change artifacts (not only application implementation).
- Bump `OPENSPEC_FLOW_VERSION` and record the release in `CHANGELOG.md` when bundle edits land via apply.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `openspec-flow-reference`: Add requirement that OSF explore intent shaping is conversation-only and does not write change or living spec files; durable capture belongs to proposal shaping.

## Impact

- `.cursor/skills/osf-explore/SKILL.md` (primary)
- `openspec/specs/openspec-flow-reference/spec.md` (via archive)
- `OPENSPEC_FLOW.md` (explore row + optional forbidden-transition clarity)
- `OPENSPEC_FLOW_VERSION`, `CHANGELOG.md`
- Bundle consumers upgrading via `/openspec-flow-install` receive stricter explore behavior on sync
