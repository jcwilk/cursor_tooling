## Context

The install skill (`.cursor/skills/openspec-flow-install/SKILL.md`) defines a bundle inventory copied to consumer projects. Today that inventory includes:

- `.cursor/skills/openspec-flow-install/` — the install skill itself
- `.cursor/skills/sleuths/` — conversation sleuths (still evolving in this reference repo)
- `scripts/build-local-tools.sh` — one-time setup for sleuths Python tooling

Those paths make sense in **this** reference repository but not on external OSF consumers. Operators running `/openspec-flow-install` may assume everything in the inventory is supported for targets.

Living spec `openspec-flow-target-sync` governs propagation mechanics but does not yet define exclusions for reference-only or in-development bundle members.

## Goals / Non-Goals

**Goals:**

- Make the install skill inventory explicitly **consumer-safe**: only OSF workflow skills, agents, and docs that belong on targets.
- Document **reference-repo-only** status for the install skill in the install skill itself.
- Add **in-development / do-not-deploy** guidance for sleuths in contributor-facing docs (`AGENTS.md`; optional one-line pointer in `OPENSPEC_FLOW.md` capabilities table).
- Encode exclusions as testable behavior in `openspec-flow-target-sync` delta spec.

**Non-Goals:**

- Changing sleuths implementation, specs, or the `/sleuths` skill in this reference repo.
- Removing sleuths from this reference repo.
- Automatically deleting stale install/sleuths copies on already-synced targets (document manual cleanup only).
- Bumping `OPENSPEC_FLOW_VERSION` unless apply tasks decide a semver bump is warranted for this behavioral change (recommend patch bump).

## Decisions

### 1. Exclusion list lives in the install skill inventory

**Decision:** Replace the current flat inventory with two explicit sections: **propagated to targets** and **reference repo only (never propagate)**.

**Rationale:** Operators and agents read the install skill at sync time; duplicating the list only in AGENTS.md would drift. AGENTS.md gets a short policy statement; the authoritative exclusion mechanics stay in the install skill.

**Alternatives considered:**

- Hard-coded exclude filter in a shell script only — rejected; agents often sync file-by-file without scripts.
- New living spec domain for install — rejected; `openspec-flow-target-sync` already covers propagation.

### 2. Exclude sleuths companion tooling from target sync

**Decision:** Remove `scripts/build-local-tools.sh` from the consumer inventory and drop post-sync reminders to run it for sleuths.

**Rationale:** That script exists solely to install sleuths local Python deps; without sleuths on targets, it has no purpose there.

### 3. Contributor guidance placement

**Decision:**

- **`AGENTS.md`** — add a prominent note at the start of the Conversation sleuths section: in development, reference-repo-only, MUST NOT be deployed to external projects via install/sync.
- **`OPENSPEC_FLOW.md`** — add a brief note on the `/sleuths` row in the capabilities table (e.g. "reference repo only; not propagated to consumers").
- **Install skill** — state it is reference-repo-only and never copied to targets.

**Rationale:** AGENTS.md is the operator contract for this bundle; OPENSPEC_FLOW.md is the first doc consumers read. Both improve discoverability without duplicating full runbooks.

### 4. Upgrade behavior for stale copies

**Decision:** On upgrade, sync **does not** push updates to excluded paths and **does not** delete existing copies on targets unless the operator opts into cleanup manually.

**Rationale:** Aligns with existing "coexistence companions" behavior in `openspec-flow-target-sync`; avoids surprise deletions.

## Risks / Trade-offs

- **[Risk] Targets already have sleuths/install from prior syncs** → Mitigation: document in install skill upgrade section; mention in tasks for operator communication; breaking note in proposal.
- **[Risk] Future local tools bundled with OSF** → Mitigation: inventory sections make it obvious which category new skills belong in.
- **[Risk] AGENTS.md merge on install omits sleuth dev notice** → Mitigation: sleuth dev notice lives in reference AGENTS.md; install skill merge instructions call out preserving the new bullet when merging.

## Migration Plan

1. Apply skill and doc edits on reference repo.
2. Operators upgrading consumers get updated OSF bundle without install/sleuths paths in sync scope.
3. Optional manual cleanup on targets: remove `.cursor/skills/openspec-flow-install/`, `.cursor/skills/sleuths/`, and `scripts/build-local-tools.sh` if present and unused.

## Open Questions

- None blocking apply; semver bump left to apply worker per bundle release convention.
