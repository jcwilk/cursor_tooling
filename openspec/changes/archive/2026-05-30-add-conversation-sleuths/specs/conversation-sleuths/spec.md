## ADDED Requirements

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

The system SHALL produce and update sleuth summaries only when a human explicitly requests refresh. Refresh SHALL incorporate new conversation material since the last checkpoint without reprocessing already-checkpointed transcript segments.

#### Scenario: Initial refresh

- **WHEN** a human requests refresh for a newly defined sleuth and local agent transcripts exist
- **THEN** the system produces an initial summary from eligible transcript content matching the lens

#### Scenario: Incremental refresh after new sessions

- **GIVEN** a sleuth that has been refreshed at least once
- **WHEN** new local agent sessions have been recorded since the last checkpoint
- **AND** a human requests refresh for that sleuth
- **THEN** the system extends the existing summary using only transcript content not yet reflected in the checkpoint
- **AND** prior summary content is preserved unless superseded by the merge step

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
