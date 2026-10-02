## ADDED Requirements

### Requirement: Explore intent shaping is conversation-only

When a worker is tasked solely with OSF explore intent shaping, the worker MUST limit durable output to conversation and MUST NOT create, edit, move, or delete any repository file, including OpenSpec change artifacts and authoritative behavioral specifications.

#### Scenario: Decision ready to capture

- **WHEN** a worker completes explore work and the human has settled a decision that should be recorded in change artifacts
- **THEN** the worker MUST describe the decision and any proposed wording in conversation
- **AND** MUST offer handoff to OSF proposal shaping for durable capture
- **AND** MUST NOT write change artifacts during the explore turn

#### Scenario: Artifact mismatch discovered during explore

- **WHEN** during explore the worker finds that an existing change artifact no longer matches settled intent
- **THEN** the worker MUST identify the mismatch and proposed replacement text in conversation
- **AND** MUST NOT edit the artifact to align it during the explore turn

#### Scenario: Human requests file capture during explore

- **WHEN** a human asks the worker to update proposal or other change artifacts while explore shaping is in effect
- **THEN** the worker MUST refuse the write for that turn
- **AND** MUST route capture to OSF proposal shaping or a combined directive that explicitly invokes proposal shaping in the same message
