## ADDED Requirements

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

OSF documentation used when performing target synchronization MUST state that reference-only install-or-upgrade tooling and in-development conversation sleuths are excluded from consumer propagation, including the rationale that install tooling is reference-repository-only and sleuths are not yet suitable for external deployment.

#### Scenario: Operator reviews sync scope
- **WHEN** an operator consults OSF install-or-upgrade guidance before synchronizing to a consumer
- **THEN** documentation MUST explain that install-or-upgrade tooling and conversation sleuths are excluded from default consumer propagation and why
