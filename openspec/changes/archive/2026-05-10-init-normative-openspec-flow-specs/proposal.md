## Why

This repository’s reason to exist is to be **both** the authoritative description of OpenSpec Flow (OSF) for Cursor-based work **and** the mechanism by which downstream projects adopt that flow. Until those roles are encoded as reconciled behavioral specifications, reviewers and tooling lack a durable contract that survives doc drift and incidental refactors—only narrative docs and incidental structure.

## What Changes

- Introduce reconciled (**living**) behavioral specifications that state, in RFC 2119 terms, what the OSF **reference artifact** owes its consumers.
- Introduce reconciled (**living**) behavioral specifications for **target-repository synchronization**: what “bring this reference into another project” means in terms observable to a reviewer, without baking file-path inventory into specs (inventory stays in `design.md`).
- Establish the OpenSpec **`openspec/`** tree here so `/osf-propose`, validate, archive, and future deltas follow normal OSF discipline.

## Capabilities

### New Capabilities

- `openspec-flow-reference`: Contract for the OSF reference artifact as a cohesive, versioned Cursor integration layered on upstream OpenSpec (what it MUST communicate about workflow stages, authority between intent and reconciliation, and how consumers detect releases).
- `openspec-flow-target-sync`: Contract for aligning a consumer project’s copy of OSF with a chosen reference snapshot (comparison, propagation rules, protections for unrelated project policy).

### Modified Capabilities

- *(none)*

## Impact

- **Specifications:** New normative statements under **`openspec/specs/`** after archive (currently introduced as validated deltas under this change folder).
- **Documentation:** Narrative **`README.md`**, **`OPENSPEC_FLOW.md`**, **`AGENTS.md`**, skills, and agent definitions SHOULD remain aligned with—but not duplicate verbatim—the reconciled behavioral specs after archive.
- **Tooling installs:** Operators using **`openspec-flow-install`** (or-equivalent workflows) SHOULD treat archived specs plus existing bundle inventory together as “what OSF means” for conformance checks.
