# openspec-flow-target-sync Specification

## Purpose
TBD - created by archiving change init-normative-openspec-flow-specs. Update Purpose after archive.
## Requirements
### Requirement: Version relationship assessment prior to propagation

OSF target synchronization tooling MUST summarize the ordering relationship between a chosen OSF reference Semantic Version and a consumer’s readable OSF Semantic Version marker when both are available.

#### Scenario: Known consumer baseline
- **WHEN** synchronization tooling parses both the reference OSF Semantic Version and a consumer OSF Semantic Version marker at the outset of a synchronization attempt
- **THEN** tooling reports parity, downgrade risk, advancement opportunity, or indeterminate parity in human-readable summaries before invoking destructive merges

### Requirement: Controlled replacement of OSF integration assets

OSF target synchronization MUST update integration assets attributable to OSF reference bundles using explicit propagation mechanics scoped to OSF bundle inventory without implying wholesale deletion of every file under broadened integration prefixes.

#### Scenario: Retaining coexistence companions
- **WHEN** the target retains additional operator-managed files neighboring OSF-managed integration artifacts under the same subtree
- **THEN** default OSF synchronization avoids deleting those coexistence companions unless synchronization documentation records an explicit destructive option selected by the operator

### Requirement: Semantic Version marker parity upon successful deliberate upgrade

When OSF target synchronization declares success aligning a consumer to reference version R absent reported blocking conflicts reported by tooling, OSF target synchronization MUST update or create consumer-readable OSF Semantic Version markers so they reflect reference version R consistently with OSF synchronization conventions.

#### Scenario: Successful parity upgrade completes
- **WHEN** an operator-directed synchronization concludes without conflict and aligns the consumer to reference Semantic Version `R`
- **THEN** consumer-maintained OSF Semantic Version markers authoritative for drift detection report `R` until superseded by a later synchronization invocation

### Requirement: Reference-only install tooling excluded from consumer propagation

OSF target synchronization MUST NOT propagate install-or-upgrade tooling that exists solely to copy OSF integration assets from a reference repository into consumer projects.

#### Scenario: Default consumer install
- **WHEN** an operator synchronizes OSF integration assets from a reference bundle to a consumer project using default propagation scope
- **THEN** install-or-upgrade tooling intended only for the reference repository MUST NOT appear among assets written to the consumer

#### Scenario: Default consumer upgrade
- **WHEN** an operator upgrades an existing consumer using default OSF target synchronization scope
- **THEN** install-or-upgrade tooling intended only for the reference repository MUST NOT receive updates as part of the synchronized bundle inventory

### Requirement: In-development conversation sleuths excluded from consumer propagation

While conversation sleuths remain designated in-development reference-only capabilities, OSF target synchronization MUST NOT propagate conversation-sleuth integration assets to consumer projects.

#### Scenario: Consumer install excludes sleuths
- **WHEN** an operator performs a first-time OSF synchronization to a consumer project under default scope
- **THEN** conversation-sleuth skills, agents, or companion local-tooling attributable solely to sleuths MUST NOT be written to the consumer

#### Scenario: Consumer upgrade excludes sleuths
- **WHEN** an operator upgrades a consumer project under default OSF target synchronization scope
- **THEN** conversation-sleuth integration assets MUST NOT be included in the propagated bundle inventory

### Requirement: Operator documentation states propagation exclusions

OSF documentation used when performing target synchronization MUST state that reference-only install-or-upgrade tooling, in-development conversation sleuths, and reference-bundle release history are excluded from consumer propagation, including the rationale that install tooling is reference-repository-only, sleuths are not yet suitable for external deployment, and release history documents the reference bundle—not the consumer project.

#### Scenario: Operator reviews sync scope
- **WHEN** an operator consults OSF install-or-upgrade guidance before synchronizing to a consumer
- **THEN** documentation MUST explain that install-or-upgrade tooling, conversation sleuths, and reference-bundle release history are excluded from default consumer propagation and why

### Requirement: Reference-bundle release history excluded from consumer propagation

OSF target synchronization MUST NOT propagate release-history documentation that records versions of the OSF reference bundle itself when synchronizing to consumer projects.

#### Scenario: Consumer install excludes bundle release history
- **WHEN** an operator performs a first-time OSF synchronization to a consumer project under default scope
- **THEN** release-history documentation attributable solely to the OSF reference bundle MUST NOT be written to the consumer

#### Scenario: Consumer upgrade excludes bundle release history
- **WHEN** an operator upgrades a consumer project under default OSF target synchronization scope
- **THEN** reference-bundle release-history documentation MUST NOT be included in the propagated bundle inventory

