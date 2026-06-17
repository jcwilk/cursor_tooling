## ADDED Requirements

### Requirement: Session-scoped sleuth refresh

The system SHALL allow a human to request sleuth refresh limited to a single agent session identifier. When session scope is specified, only transcript segments belonging to that session — including Task subagent transcripts associated with that session — SHALL be eligible for processing in that refresh run. Segments from other sessions SHALL NOT be processed, and checkpoint state for unprocessed sessions SHALL remain unchanged.

#### Scenario: Refresh one session only

- **GIVEN** a sleuth with pending transcript material in multiple agent sessions
- **WHEN** a human requests refresh for that sleuth with a specific session identifier
- **THEN** the system processes only segments belonging to that session
- **AND** does not invoke the refresh pipeline for segments from other sessions in the same run

#### Scenario: Session scope includes subagent transcripts

- **GIVEN** a parent agent session with recorded Task subagent transcripts
- **WHEN** a human requests session-scoped refresh for that session's identifier
- **THEN** both the parent session transcript and associated subagent transcripts for that session are eligible for processing

#### Scenario: Scoped refresh merges into existing summary

- **GIVEN** a sleuth with an existing summary body
- **WHEN** session-scoped refresh completes successfully with new material from the targeted session
- **THEN** the updated summary incorporates the prior summary content merged with newly extracted material from that session
- **AND** checkpoint entries reflect only segments from the targeted session that were processed in that run

#### Scenario: Unknown session identifier

- **GIVEN** a session identifier that does not match any discovered transcript segment for the project
- **WHEN** a human requests session-scoped refresh with that identifier
- **THEN** the refresh operation fails with an explicit error before invoking the summarization service

#### Scenario: Session has no pending material

- **GIVEN** a valid session identifier
- **AND** all transcript segments for that session are already reflected in the checkpoint
- **WHEN** a human requests session-scoped refresh for that session
- **THEN** the refresh operation completes without processing
- **AND** reports that there is nothing new to process

## MODIFIED Requirements

### Requirement: Lazy incremental summarization

The system SHALL produce and update sleuth summaries only when a human explicitly requests refresh. Refresh SHALL incorporate new conversation material since the last checkpoint without reprocessing already-checkpointed transcript segments. New material SHALL be processed through relevance filtering, batched summarization, and hierarchical reduction before being merged into the existing summary. When the human specifies session scope, only pending material from that session SHALL be eligible for that refresh run.

#### Scenario: Initial refresh

- **WHEN** a human requests refresh for a newly defined sleuth and local agent transcripts exist
- **THEN** the system produces an initial summary from eligible transcript content matching the lens via the batched map/reduce pipeline

#### Scenario: Incremental refresh after new sessions

- **GIVEN** a sleuth that has been refreshed at least once
- **WHEN** new local agent sessions have been recorded since the last checkpoint
- **AND** a human requests refresh for that sleuth
- **THEN** the system processes only transcript content not yet reflected in the checkpoint through the batched pipeline
- **AND** merges the result into the existing summary with deduplication

#### Scenario: No refresh without human action

- **WHEN** new agent sessions occur but no human requests sleuth refresh
- **THEN** existing summary artifacts remain unchanged

#### Scenario: Incremental refresh within one session

- **GIVEN** a sleuth with pending transcript content in one agent session and already-checkpointed content in other sessions
- **WHEN** a human requests session-scoped refresh for the session with pending content
- **THEN** only the pending material from that session is processed
- **AND** checkpoint state for other sessions is unchanged
