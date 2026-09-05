## REMOVED Requirements

### Requirement: In-development conversation sleuths excluded from consumer propagation
**Reason**: Conversation sleuths are no longer part of the OSF reference bundle; sleuth-specific propagation rules are obsolete.
**Migration**: Operators upgrading consumers need not exclude sleuth assets from sync — they are no longer shipped from the reference bundle.

## MODIFIED Requirements

### Requirement: Operator documentation states propagation exclusions

OSF documentation used when performing target synchronization MUST state that reference-only install-or-upgrade tooling and reference-bundle release history are excluded from consumer propagation, including the rationale that install tooling is reference-repository-only and release history documents the reference bundle—not the consumer project.

#### Scenario: Operator reviews sync scope
- **WHEN** an operator consults OSF install-or-upgrade guidance before synchronizing to a consumer
- **THEN** documentation MUST explain that install-or-upgrade tooling and reference-bundle release history are excluded from default consumer propagation and why
