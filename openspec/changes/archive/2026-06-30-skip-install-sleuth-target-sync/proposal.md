## Why

The OpenSpec Flow install skill currently lists both itself and the sleuths skill in the bundle inventory copied to external target projects. The install skill is reference-repo-only tooling (it exists to propagate OSF *from* this bundle *to* consumers) and has no purpose on a target. Sleuths remain in active development and are not yet suitable for distribution to external projects. Copying either skill creates confusion, unnecessary drift surface, and implies capabilities consumers should not rely on.

## What Changes

- Update the install skill so its bundle inventory **explicitly excludes** the install skill and the sleuths skill when propagating to targets.
- Document in the install skill that it is **reference-repository-only** and MUST NOT be copied to consumer projects.
- Add contributor guidance (AGENTS.md and/or OPENSPEC_FLOW.md) that sleuths are **in development** and MUST NOT be deployed to external projects via install/sync.
- Remove sleuths-related install reminders (e.g. build-local-tools for sleuths) from the default target sync path; sleuths remain available in this reference repo only.
- **BREAKING (behavioral):** Existing targets that received sleuths or the install skill via prior sync will no longer receive updates to those paths on upgrade; operators may manually remove stale copies.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `openspec-flow-target-sync`: Add requirements that target synchronization excludes reference-only install tooling and in-development sleuths from the propagated bundle inventory.

## Impact

- **`.cursor/skills/openspec-flow-install/SKILL.md`** — inventory list, install/upgrade steps, optional rsync helpers, post-sync reminders.
- **`AGENTS.md`** — sleuths section: development status and external-deployment prohibition.
- **`OPENSPEC_FLOW.md`** — optional cross-link in capabilities table or install section if a short pointer helps discoverability.
- **Living spec delta:** `openspec/specs/openspec-flow-target-sync/spec.md` (via archive after apply).
- **No change** to sleuths implementation, osf-* skills, or apply agents beyond what install propagates.
