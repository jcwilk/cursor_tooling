## ADDED Requirements

### Requirement: Bounded parallel inference within pipeline stages

When a sleuth refresh pipeline stage issues multiple summarization service calls for batch groups within that stage, the system SHALL execute those calls with bounded concurrency rather than strictly serial one-at-a-time execution. Parallelism SHALL apply only among batch groups belonging to the same stage invocation (relevance filtering, batched summarization, or one hierarchical merge round). The system SHALL NOT run summarization service calls from different pipeline stages concurrently as part of this behavior. The maximum number of in-flight requests within a stage SHALL be configurable on the local workstation with a default of four.

#### Scenario: Multiple batches in one stage use bounded concurrency

- **GIVEN** a relevance, summarization, or merge stage with more than one batch group eligible for service calls in that stage invocation
- **WHEN** that stage runs
- **THEN** the system may have up to the configured maximum number of summarization service requests in flight at once for that stage
- **AND** the number of service calls issued for that stage equals the number of batch groups (same count as strictly serial execution)

#### Scenario: Single batch remains one call

- **GIVEN** a pipeline stage with exactly one batch group
- **WHEN** that stage runs
- **THEN** the system issues one summarization service call for that stage
- **AND** refresh behavior matches a serial run for that stage

#### Scenario: Operator configures parallel inference limit

- **GIVEN** a workstation with sleuth processing configuration specifying a maximum parallel inference request count
- **WHEN** a human requests sleuth refresh and a stage has multiple batch groups
- **THEN** that stage limits in-flight summarization service requests to the configured maximum

#### Scenario: Stages do not overlap inference

- **GIVEN** sleuth refresh running relevance filtering followed by batched summarization
- **WHEN** both stages execute in the same refresh run
- **THEN** summarization service calls for batched summarization do not begin until relevance filtering for that segment has completed
- **AND** parallel inference applies only within each stage separately

## MODIFIED Requirements

### Requirement: Relevance filtering pass

Before summarization, the system SHALL request from the summarization service a comma-separated list of zero-based chunk indices only (no surrounding prose or structured wrapper) whose content is relevant to the sleuth lens. Only chunks whose indices appear in that list SHALL proceed to summarization; all other chunks in that batch SHALL be discarded for summarization purposes.

#### Scenario: Irrelevant chunks excluded

- **GIVEN** a batch of indexed chunks where only some match the sleuth lens
- **WHEN** the relevance pass completes
- **THEN** only chunks with returned indices are eligible for summarization

#### Scenario: No relevant chunks in a batch

- **GIVEN** a batch where the relevance pass returns no indices
- **WHEN** summarization for that segment continues
- **THEN** no summary content is produced from that batch

#### Scenario: Unparseable relevance response

- **GIVEN** a relevance batch where the summarization service returns a response that cannot be parsed as a comma-separated list of zero-based chunk indices
- **WHEN** the relevance pass completes
- **THEN** no chunks from that batch proceed to summarization
- **AND** refresh continues with remaining batches without advancing the checkpoint prematurely
