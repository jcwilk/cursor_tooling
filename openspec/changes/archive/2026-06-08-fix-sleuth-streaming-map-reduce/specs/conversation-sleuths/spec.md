## ADDED Requirements

### Requirement: Small granular transcript chunks

When streaming a transcript segment for refresh, the system SHALL divide unprocessed content into small consecutive chunks derived from transcript lines. Each chunk SHALL receive a stable zero-based index for that segment pass, starting at zero for the first chunk of the pass.

#### Scenario: Chunks are indexed in order

- **GIVEN** a transcript segment with unprocessed lines
- **WHEN** chunk streaming begins
- **THEN** the first chunk is index 0
- **AND** each subsequent chunk receives the next consecutive integer index without gaps in ordering

### Requirement: Bounded relevance batches

When running a relevance pass, the system SHALL present chunks to the summarization service in consecutive batches where each batch respects both a configurable context budget and a configurable maximum number of chunks per batch. The default maximum SHALL be small enough that a human operator can reason about the id list without hundreds of entries (approximately twenty chunks).

#### Scenario: Large segment split across relevance batches

- **GIVEN** more chunks than fit in one batch under budget and count limits
- **WHEN** relevance processing runs
- **THEN** the system issues multiple relevance requests
- **AND** each request includes at most the configured maximum chunk count

### Requirement: Relevance filtering pass

Before summarization, the system SHALL request from the summarization service a structured machine-readable list of zero-based chunk indices whose content is relevant to the sleuth lens. Only chunks whose indices are returned SHALL proceed to summarization; all other chunks in that batch SHALL be discarded for summarization purposes.

#### Scenario: Irrelevant chunks excluded

- **GIVEN** a batch of indexed chunks where only some match the sleuth lens
- **WHEN** the relevance pass completes
- **THEN** only chunks with returned indices are eligible for summarization

#### Scenario: No relevant chunks in a batch

- **GIVEN** a batch where the relevance pass returns no indices
- **WHEN** summarization for that segment continues
- **THEN** no summary content is produced from that batch

#### Scenario: Unparseable relevance response

- **GIVEN** a relevance batch where the summarization service returns a response that cannot be parsed as a structured list of indices
- **WHEN** the relevance pass completes
- **THEN** no chunks from that batch proceed to summarization
- **AND** refresh continues with remaining batches without advancing the checkpoint prematurely

### Requirement: Batched summarization of filtered chunks

After relevance filtering, the system SHALL group remaining chunks using the same context-budget and per-batch chunk-count limits, and SHALL produce one pass summary per group. Each pass summary SHALL be bounded to a configurable maximum size (default equivalent to roughly four thousand tokens).

#### Scenario: Filtered chunks summarized in groups

- **GIVEN** several relevant chunks that fit in one summarize batch
- **WHEN** summarization runs
- **THEN** those chunks are summarized together in one pass
- **AND** the result is a single pass summary for that group

#### Scenario: Single pass summary needs no sibling merge

- **GIVEN** a segment where summarization produces exactly one pass summary
- **WHEN** hierarchical reduction runs for that segment
- **THEN** no additional merge step is required solely to combine sibling pass summaries from that segment

### Requirement: Hierarchical bounded summarization

When more than one pass summary exists for a segment or refresh unit, the system SHALL recursively merge pass summaries using the same grouping limits until one summary remains within a configurable final target (default equivalent to roughly four thousand tokens), deduplicating facts across merged summaries.

#### Scenario: Large session reduces to bounded summary

- **GIVEN** many relevant chunks from one session that produce multiple pass summaries
- **WHEN** hierarchical summarization completes
- **THEN** the session contributes one summary intended to fit the final target size
- **AND** duplicate facts from different pass summaries are not repeated verbatim in the merged result

#### Scenario: Per-pass cap enforced

- **GIVEN** a summarize group with substantial matching content
- **WHEN** a summarize pass runs
- **THEN** the produced summary is instructed and bounded to the configured per-pass maximum

### Requirement: Prior summary as merge seed

When a sleuth summary already exists and refresh processes new transcript material, the system SHALL run relevance filtering and batched summarization on new content independently, then merge the result with the existing summary using the same recursive reduction approach, treating the prior summary as the initial aggregate value in that merge only.

#### Scenario: Incremental refresh preserves prior knowledge

- **GIVEN** a sleuth with an existing summary and new unprocessed transcript content
- **WHEN** refresh completes successfully
- **THEN** the updated summary incorporates both prior summary content and newly extracted material
- **AND** the merge step deduplicates overlapping facts between old and new summaries

## MODIFIED Requirements

### Requirement: Lazy incremental summarization

The system SHALL produce and update sleuth summaries only when a human explicitly requests refresh. Refresh SHALL incorporate new conversation material since the last checkpoint without reprocessing already-checkpointed transcript segments. New material SHALL be processed through relevance filtering, batched summarization, and hierarchical reduction before being merged into the existing summary.

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
