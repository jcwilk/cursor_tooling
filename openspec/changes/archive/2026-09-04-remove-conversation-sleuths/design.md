## Context

The OSF reference bundle currently ships a Python sleuth package (`.cursor/skills/sleuths/`), `/sleuths` skill, companion build scripts, and two living specs (`conversation-sleuths`, `context-budget-grouping`). Target-sync docs also describe sleuth-specific propagation exclusions. Partial ad-hoc removal may exist on a working branch; this change formalizes full retirement. See `proposal.md` for motivation.

## Goals / Non-Goals

**Goals:**

- Remove all sleuth code, skills, scripts, and bundle documentation references.
- Retire sleuth living specs via archive deltas.
- Bump `OPENSPEC_FLOW_VERSION` to **1.6.0** with a changelog entry.
- Leave archived sleuth change history under `openspec/changes/archive/` untouched.

**Non-Goals:**

- Deleting or rewriting archived proposals that document sleuth development history.
- Removing operator-local machine state under `.sleuths/` on workstations (gitignored; operator-managed).
- Providing a replacement transcript-archaeology capability in this bundle.

## Decisions

### 1. Retire `context-budget-grouping` with sleuths

**Decision:** Remove the entire `context-budget-grouping` living spec; it has no consumers outside sleuth refresh.

**Rationale:** Keeping an orphaned spec implies bundle behavior that no longer exists.

**Alternative considered:** Keep the spec for potential reuse — rejected because it adds review surface with no current product owner.

### 2. Do not edit archived change folders

**Decision:** Apply removes implementation and living specs only; `openspec/changes/archive/*sleuth*` folders stay as historical record.

**Rationale:** Human explicitly requested archived proposals remain; archive is archaeology, not shipped behavior.

### 3. Bundle version bump to 1.6.0 (minor)

**Decision:** Treat full capability removal as a **minor** semver bump (1.5.0 → 1.6.0), not patch.

**Rationale:** Consumers lose a documented capability and install inventory changes materially.

### 4. Install skill inventory cleanup

**Decision:** Remove sleuth paths and `build-local-tools.sh` from reference-only inventory; keep legacy `.cursor/build-local-tools.sh` cleanup note on consumer upgrade.

**Rationale:** Aligns install guidance with what the reference repo actually ships.

## Risks / Trade-offs

- **[Risk] Operators rely on `/sleuths` in this reference repo** → Document removal in CHANGELOG 1.6.0; no in-bundle replacement.
- **[Risk] Stale sleuth copies on already-synced consumer projects** → Install skill already documents manual cleanup for reference-only paths; note sleuth paths in upgrade guidance.
- **[Risk] Partial ad-hoc edits on branch conflict with tasks** → Apply worker reconciles working tree against tasks checklist before finish.

## Migration Plan

1. Apply deletes sleuth code paths and updates bundle docs per `tasks.md`.
2. Run `openspec validate` and archive via `osf-apply-finish` to reconcile living specs.
3. Operators on reference repo: delete local `.sleuths/` if desired (optional, not committed).
4. Operators on consumers that received sleuth copies: manually remove `.cursor/skills/sleuths/`, `scripts/build-local-tools.sh`, and related paths if present.

## Open Questions

None blocking apply.
