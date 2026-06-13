## ADDED Requirements

### Requirement: Human-initiated sleuth reset

The system SHALL allow a human to discard a sleuth's summary and processing checkpoint without deleting the lens definition, so a subsequent refresh reprocesses all eligible transcript content as if no prior refresh had occurred for that sleuth.

#### Scenario: Reset clears progress but preserves the lens

- **GIVEN** a sleuth with an existing summary, checkpoint, and lens definition
- **WHEN** a human requests reset for that sleuth
- **THEN** the summary and checkpoint for that sleuth are removed
- **AND** the lens definition remains available for future refresh operations

#### Scenario: Reset does not invoke summarization

- **WHEN** a human requests reset for a sleuth
- **THEN** the reset operation completes without calling the configured summarization service
- **AND** no new summary content is produced until a separate refresh is requested

#### Scenario: Reset is safe when nothing exists yet

- **GIVEN** a sleuth with a lens definition but no summary or checkpoint
- **WHEN** a human requests reset for that sleuth
- **THEN** the operation completes successfully without error

#### Scenario: Full rebuild after reset

- **GIVEN** a sleuth whose summary and checkpoint were reset
- **WHEN** a human requests refresh for that sleuth and eligible transcripts exist
- **THEN** the system processes eligible transcript content from the beginning through the standard refresh pipeline
- **AND** produces a new summary without merging against the previously discarded summary

#### Scenario: Reset all sleuths independently

- **WHEN** a human requests reset for every defined sleuth in the project
- **THEN** each sleuth's summary and checkpoint are cleared independently
- **AND** each lens definition remains intact
