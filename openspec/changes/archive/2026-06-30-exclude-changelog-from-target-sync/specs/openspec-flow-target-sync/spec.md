## ADDED Requirements

### Requirement: Reference-bundle release history excluded from consumer propagation

OSF target synchronization MUST NOT propagate release-history documentation that records versions of the OSF reference bundle itself when synchronizing to consumer projects.

#### Scenario: Consumer install excludes bundle release history
- **WHEN** an operator performs a first-time OSF synchronization to a consumer project under default scope
- **THEN** release-history documentation attributable solely to the OSF reference bundle MUST NOT be written to the consumer

#### Scenario: Consumer upgrade excludes bundle release history
- **WHEN** an operator upgrades a consumer project under default OSF target synchronization scope
- **THEN** reference-bundle release-history documentation MUST NOT be included in the propagated bundle inventory

## MODIFIED Requirements

### Requirement: Operator documentation states propagation exclusions

OSF documentation used when performing target synchronization MUST state that reference-only install-or-upgrade tooling, in-development conversation sleuths, and reference-bundle release history are excluded from consumer propagation, including the rationale that install tooling is reference-repository-only, sleuths are not yet suitable for external deployment, and release history documents the reference bundle—not the consumer project.

#### Scenario: Operator reviews sync scope
- **WHEN** an operator consults OSF install-or-upgrade guidance before synchronizing to a consumer
- **THEN** documentation MUST explain that install-or-upgrade tooling, conversation sleuths, and reference-bundle release history are excluded from default consumer propagation and why
