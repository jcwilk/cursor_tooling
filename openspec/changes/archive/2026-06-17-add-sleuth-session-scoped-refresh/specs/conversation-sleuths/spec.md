## ADDED Requirements

### Requirement: Session-scoped sleuth refresh

The system SHALL allow a human to request sleuth refresh limited to a single agent session identifier. When session scope is specified, only transcript segments belonging to that session — including Task subagent transcripts associated with that session — SHALL be eligible for processing in that refresh run. Segments from other sessions SHALL NOT be processed, and checkpoint state for unprocessed sessions SHALL remain unchanged.

When session scope is specified, the system SHALL reprocess all transcript material from that session from the beginning, regardless of whether a prior refresh already checkpointed that session as fully processed.

#### Scenario: Refresh one session only

- **GIVEN** a sleuth with transcript material in multiple agent sessions
- **WHEN** a human requests refresh for that sleuth with a specific session identifier
- **THEN** the system processes only segments belonging to that session
- **AND** does not invoke the refresh pipeline for segments from other sessions in the same run

#### Scenario: Session scope includes subagent transcripts

- **GIVEN** a parent agent session with recorded Task subagent transcripts
- **WHEN** a human requests session-scoped refresh for that session's identifier
- **THEN** both the parent session transcript and associated subagent transcripts for that session are eligible for processing

#### Scenario: Session scope reprocesses already-checkpointed material

- **GIVEN** a sleuth whose checkpoint records a session as fully processed
- **WHEN** a human requests session-scoped refresh for that session's identifier
- **THEN** the system reprocesses all transcript material from that session from the beginning
- **AND** does not skip that session because the checkpoint marks it complete

#### Scenario: Scoped refresh merges into existing summary

- **GIVEN** a sleuth with an existing summary body
- **WHEN** session-scoped refresh completes successfully with new material from the targeted session
- **THEN** the updated summary incorporates the prior summary content merged with newly extracted material from that session
- **AND** checkpoint entries for the targeted session reflect the reprocessed segments

#### Scenario: Unknown session identifier

- **GIVEN** a session identifier that does not match any discovered transcript segment for the project
- **WHEN** a human requests session-scoped refresh with that identifier
- **THEN** the refresh operation fails with an explicit error before invoking the summarization service

### Requirement: Refresh dry-run without persistence

The system SHALL support a dry-run mode on sleuth refresh that executes the full refresh orchestration — including summarization service calls when configured — and emits the resulting summary output without writing checkpoint or summary artifacts to local sleuth storage. Dry-run SHALL suppress all persistence of sleuth refresh state to disk regardless of any other refresh options specified in the same request. Dry-run SHALL be available only on refresh, not on other sleuth operations.

#### Scenario: Dry-run emits summary without writing artifacts

- **GIVEN** a sleuth with existing local summary and checkpoint artifacts
- **WHEN** a human requests refresh in dry-run mode
- **AND** refresh completes successfully
- **THEN** the system prints the resulting summary document to standard output
- **AND** does not modify the existing summary or checkpoint artifacts on disk

#### Scenario: Dry-run with session scope still reprocesses without persistence

- **GIVEN** a sleuth whose checkpoint records a session as fully processed
- **WHEN** a human requests session-scoped refresh in dry-run mode for that session
- **THEN** the system reprocesses all transcript material from that session
- **AND** emits the merged summary result to standard output
- **AND** does not modify checkpoint or summary artifacts on disk

#### Scenario: Dry-run not available on other operations

- **WHEN** a human invokes sleuth reset or other non-refresh operations
- **THEN** dry-run mode is not offered for those operations

## MODIFIED Requirements

### Requirement: Lazy incremental summarization

The system SHALL produce and update sleuth summaries only when a human explicitly requests refresh. Refresh SHALL incorporate new conversation material since the last checkpoint without reprocessing already-checkpointed transcript segments, except when session scope is specified — in which case all material from the targeted session SHALL be reprocessed from the beginning. New material SHALL be processed through relevance filtering, batched summarization, and hierarchical reduction before being merged into the existing summary. When the human specifies session scope, only material from that session SHALL be eligible for that refresh run. When dry-run mode is specified, refresh SHALL not persist summary or checkpoint updates even on successful completion.

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

#### Scenario: Session-scoped refresh overrides incremental checkpoint for that session

- **GIVEN** a sleuth with fully checkpointed material in one session and pending material in another
- **WHEN** a human requests session-scoped refresh for the fully checkpointed session
- **THEN** the system reprocesses the targeted session from the beginning
- **AND** does not require manual checkpoint clearing for that session
- **AND** leaves checkpoint state for other sessions unchanged until finalize updates the targeted session
