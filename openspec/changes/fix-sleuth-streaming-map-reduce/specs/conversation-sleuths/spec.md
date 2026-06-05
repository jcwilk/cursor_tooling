## ADDED Requirements

### Requirement: Streaming session consumption

When processing a transcript segment during sleuth refresh, the system SHALL consume content from the beginning of the unprocessed portion as an ordered stream of chunks and SHALL process chunks in sequence without skipping ahead of earlier unprocessed content.

#### Scenario: Session processed from checkpoint forward

- **GIVEN** a transcript segment partially processed through a checkpoint line
- **WHEN** refresh continues that segment
- **THEN** chunk streaming begins at the first unprocessed line
- **AND** proceeds forward to the end of the segment

### Requirement: Relevance filtering pass

Before summarization, the system SHALL group streamed chunks using context-budget grouping, present each chunk with a stable index within the segment pass, and request from the summarization service a comma-separated list of indices whose content is relevant to the sleuth lens topic. Only chunks whose indices are returned SHALL proceed to summarization.

#### Scenario: Irrelevant chunks excluded

- **GIVEN** a group of indexed chunks where only some match the sleuth lens
- **WHEN** the relevance pass completes
- **THEN** only chunks with returned indices are included in the summarization input

#### Scenario: No relevant chunks in a group

- **GIVEN** a group where the relevance pass returns no indices
- **WHEN** summarization for that segment continues
- **THEN** no summary content is produced from that group

### Requirement: Hierarchical bounded summarization

The system SHALL summarize relevant chunks in context-budget-sized groups, cap each pass summary to a configurable maximum (default 4000 tokens), recursively merge pass summaries using the same context-budget grouping until a single summary remains within a configurable final target (default 4000 tokens), and deduplicate facts across merged summaries.

#### Scenario: Large session reduces to bounded summary

- **GIVEN** many relevant chunks from one session
- **WHEN** hierarchical summarization completes
- **THEN** the session contributes one summary intended to fit the final target size
- **AND** duplicate facts from different pass summaries are not repeated verbatim in the merged result

#### Scenario: Per-pass cap enforced

- **GIVEN** a relevance group with substantial matching content
- **WHEN** a summarize pass runs
- **THEN** the produced summary is instructed and bounded to the configured per-pass maximum

### Requirement: Prior summary as merge seed

When a sleuth summary already exists and refresh processes new transcript material, the system SHALL run the streaming relevance and summarization pipeline on new content independently, then merge the result with the existing summary using the same recursive reduction approach, treating the prior summary as the initial aggregate value in that merge.

#### Scenario: Incremental refresh preserves prior knowledge

- **GIVEN** a sleuth with an existing summary and new unprocessed transcript content
- **WHEN** refresh completes successfully
- **THEN** the updated summary incorporates both prior summary content and newly extracted material
- **AND** the merge step deduplicates overlapping facts between old and new summaries

## MODIFIED Requirements

### Requirement: Lazy incremental summarization

The system SHALL produce and update sleuth summaries only when a human explicitly requests refresh. Refresh SHALL incorporate new conversation material since the last checkpoint without reprocessing already-checkpointed transcript segments. New material SHALL be processed through streaming relevance filtering and hierarchical summarization before being merged into the existing summary.

#### Scenario: Initial refresh

- **WHEN** a human requests refresh for a newly defined sleuth and local agent transcripts exist
- **THEN** the system produces an initial summary from eligible transcript content matching the lens via the streaming map/reduce pipeline

#### Scenario: Incremental refresh after new sessions

- **GIVEN** a sleuth that has been refreshed at least once
- **WHEN** new local agent sessions have been recorded since the last checkpoint
- **AND** a human requests refresh for that sleuth
- **THEN** the system processes only transcript content not yet reflected in the checkpoint through the streaming pipeline
- **AND** merges the result into the existing summary with deduplication

#### Scenario: No refresh without human action

- **WHEN** new agent sessions occur but no human requests sleuth refresh
- **THEN** existing summary artifacts remain unchanged
