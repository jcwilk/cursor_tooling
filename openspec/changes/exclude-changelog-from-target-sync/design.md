## Context

Prior change `skip-install-sleuth-target-sync` split install inventory into propagated vs reference-only paths but left `CHANGELOG.md` in the propagated list. A direct edit during install to `i2s_synths` corrected the install skill and removed the mistaken copy on the target; this change formalizes that behavior in specs and ensures the install skill is complete and consistent.

## Goals / Non-Goals

**Goals:**

- Exclude reference-bundle release history from default consumer propagation.
- Extend living spec and install skill consistently with install/sleuths exclusions.
- Update operator-documentation requirement to mention all three exclusion classes.

**Non-Goals:**

- Changing how this reference repo maintains its own `CHANGELOG.md`.
- Auto-deleting stale `CHANGELOG.md` on already-synced consumers.
- Bumping `OPENSPEC_FLOW_VERSION` unless apply decides a patch bump is warranted for the behavioral fix.

## Decisions

### 1. ADD + MOD rather than new capability

**Decision:** Add one requirement for bundle-release-history exclusion; MODIFY the existing operator-documentation requirement to include it.

**Rationale:** Same bounded context (`openspec-flow-target-sync`); avoids fragmenting propagation rules.

### 2. Install skill is authoritative inventory

**Decision:** Reconcile `.cursor/skills/openspec-flow-install/SKILL.md` on apply — verify the direct edit matches spec scenarios.

**Rationale:** Partial work already landed in working tree; apply completes and validates alignment.

## Risks / Trade-offs

- **[Risk] Stale CHANGELOG.md on prior consumers** → Document manual removal; default sync does not delete.
- **[Risk] Operator docs requirement becomes a laundry list** → Keep spec behavioral ("release history attributable to reference bundle"); file names stay in install skill only.

## Migration Plan

1. Apply install skill edits (reconcile if needed).
2. Archive delta into living spec.
3. Operators who received `CHANGELOG.md` from old sync may delete it from targets.

## Open Questions

None blocking apply.
