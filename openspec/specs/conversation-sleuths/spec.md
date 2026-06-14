# conversation-sleuths Specification

## Purpose
TBD - created by archiving change add-conversation-sleuths. Update Purpose after archive.
## Requirements
### Requirement: Human-defined sleuth lenses

The system SHALL allow a human to define one or more named sleuth lenses for a project. Each lens SHALL describe what to extract from agent conversation history (for example, database modifications, authentication decisions, or deployment incidents). Lens definitions SHALL persist on the local workstation for reuse across refresh operations.

#### Scenario: Human establishes a new sleuth

- **WHEN** a human invokes the sleuth setup workflow and describes what to track
- **THEN** the system persists a new lens definition scoped to that project on the local machine
- **AND** the lens remains available for subsequent refresh operations without re-entering the description

#### Scenario: Multiple independent sleuths

- **WHEN** a human defines more than one sleuth lens for the same project
- **THEN** each lens maintains its own summary and processing checkpoint independently

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

### Requirement: Local agent transcript discovery

The system SHALL discover agent conversation transcripts stored locally by Cursor for the current project. Discovery SHALL include conversations recorded from the primary workspace for the project root and, when the project is a git repository, conversations recorded from other git worktrees linked to the same repository. Discovery MAY include additional transcript locations explicitly configured for the local workstation.

#### Scenario: Git worktree conversations included

- **GIVEN** a git project where agent sessions occurred on an linked worktree checkout
- **WHEN** a human requests sleuth refresh from the main project root
- **THEN** transcript content from that worktree's sessions is eligible for summarization

#### Scenario: Non-git project uses primary workspace only

- **GIVEN** a project that is not a git repository
- **WHEN** a human requests sleuth refresh
- **THEN** the system discovers transcripts for the workspace path corresponding to the project root
- **AND** does not assume access to unrelated workspace slugs unless locally configured

### Requirement: Task subagent transcript inclusion

The system SHALL include Task subagent conversation transcripts associated with a parent agent session when summarizing that session's history.

#### Scenario: Subagent output appears in summary scope

- **GIVEN** a parent agent session with recorded Task subagent transcripts
- **WHEN** a sleuth refresh processes that session
- **THEN** content from those subagent transcripts is eligible for extraction under the sleuth lens

### Requirement: Agent-readable summary artifacts

The system SHALL maintain a human- and agent-readable summary artifact per sleuth that distills matching content from processed transcripts. Summaries SHALL identify source sessions in a way that allows tracing back to original conversations. Summaries SHALL preserve concrete references (such as file paths) from source material where present rather than replacing them with vague paraphrase alone.

#### Scenario: Agent consults summary during unrelated work

- **WHEN** an agent is performing a task that may depend on prior project conversations
- **AND** a relevant sleuth summary exists locally
- **THEN** the agent can read that summary to inform its work without re-scanning raw transcript files

#### Scenario: Summary cites session provenance

- **WHEN** a sleuth summary includes an extracted item
- **THEN** the item is associated with the agent session (or subagent session) it was drawn from

### Requirement: Local-only sleuth state

All sleuth configuration, checkpoints, and summary outputs for a project SHALL remain on the local workstation and SHALL NOT be required for version control or cross-machine synchronization.

#### Scenario: Sleuth state is machine-local

- **WHEN** sleuth lenses and summaries exist for a project on one workstation
- **THEN** another checkout of the same repository on a different machine does not automatically receive those artifacts

### Requirement: Privacy protection for sleuth outputs

The system MUST treat sleuth summaries and their source-derived content as potentially containing secrets or sensitive data from agent transcripts. Sleuth state MUST be excluded from project version control by default.

#### Scenario: Summaries are not publishable artifacts

- **WHEN** sleuth summaries are generated
- **THEN** project guidance makes clear they must not be committed to shared repositories

### Requirement: Externally configured local summarization

Summarization during sleuth refresh SHALL use a summarization service endpoint configured on the local workstation. If that service is unavailable or misconfigured, refresh SHALL fail with an explicit error and SHALL NOT advance checkpoints as if processing succeeded.

#### Scenario: Summarization service unavailable

- **WHEN** a human requests sleuth refresh
- **AND** the configured local summarization service cannot be reached
- **THEN** the refresh operation reports failure
- **AND** the sleuth checkpoint is not advanced beyond successfully processed segments

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

### Requirement: Optional cloud run observability

When the operator configures cloud tracing credentials on the local workstation, sleuth refresh runs SHALL export run and step metadata for the refresh pipeline to the configured cloud observability service. When tracing credentials are not configured, refresh SHALL complete without requiring cloud connectivity and SHALL NOT export run metadata externally.

#### Scenario: Operator enables cloud tracing

- **GIVEN** valid cloud tracing credentials are configured locally for the workstation
- **WHEN** a human requests sleuth refresh
- **THEN** the refresh run exports observability metadata for the pipeline and its steps to the configured cloud service

#### Scenario: Operator has not configured tracing

- **GIVEN** no cloud tracing credentials are configured
- **WHEN** a human requests sleuth refresh
- **THEN** processing remains local to the workstation
- **AND** refresh does not require connectivity to a cloud observability service

#### Scenario: Tracing export fails during refresh

- **GIVEN** cloud tracing credentials are configured
- **AND** the cloud observability service is unreachable or rejects the export
- **WHEN** a human requests sleuth refresh
- **AND** the configured summarization service is available
- **THEN** refresh completes local summarization and artifact updates
- **AND** the operator receives an explicit warning that tracing export failed

