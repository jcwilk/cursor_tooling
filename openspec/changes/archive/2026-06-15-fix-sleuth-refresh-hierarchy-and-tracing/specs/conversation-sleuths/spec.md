## ADDED Requirements

### Requirement: Cross-segment reduction at refresh boundary

The system SHALL collect exactly one segment summary per processed transcript segment during a refresh batch. Cross-segment reduction of those segment summaries into the sleuth summary body SHALL run once per refresh batch after all pending segments in that batch have been processed, using hierarchical bounded summarization with the same grouping limits as within-segment reduction. The system SHALL NOT run cross-segment reduction after each individual segment within the same refresh batch.

#### Scenario: Full reset refresh merges once at batch end

- **GIVEN** a sleuth whose summary and checkpoint were reset
- **AND** multiple transcript segments are pending in one refresh batch
- **WHEN** refresh completes successfully
- **THEN** each pending segment contributes at most one segment summary to the batch collection
- **AND** cross-segment reduction runs once to produce the final summary body
- **AND** the number of cross-segment reduction inference calls is less than the number of summarize inference calls in that batch

#### Scenario: Incremental batch merges only new segment summaries

- **GIVEN** a sleuth with an existing summary body and new pending transcript segments in one refresh batch
- **WHEN** refresh completes successfully
- **THEN** cross-segment reduction runs once using the prior summary body as the merge seed
- **AND** only segment summaries produced from the current batch are combined with that seed
- **AND** segment summaries already represented in the prior summary are not re-supplied as separate merge inputs

#### Scenario: Mid-batch failure does not partially rewrite summary body

- **GIVEN** a refresh batch where some but not all pending segments are processed before failure
- **WHEN** the refresh operation fails before batch finalization
- **THEN** checkpoints reflect only successfully processed segments
- **AND** the summary body is not updated by cross-segment reduction from a partial batch

### Requirement: Structured refresh observability hierarchy

When cloud tracing credentials are configured, each sleuth refresh operation SHALL export exactly one root observability trace for that operation. All pipeline steps for that refresh, including per-segment processing and individual summarization service calls, SHALL appear as descendant spans of that root trace rather than as unrelated root traces.

Each observability span SHALL use a descriptive name that remains understandable when viewed in isolation without surrounding context. Names MAY be several words long when needed for clarity.

#### Scenario: Single root trace per refresh

- **GIVEN** valid cloud tracing credentials are configured locally
- **WHEN** a human requests sleuth refresh for one sleuth lens
- **AND** refresh performs multiple summarization service calls across several transcript segments
- **THEN** the observability service receives one root trace representing the entire refresh operation
- **AND** every summarization service call from that refresh appears as a descendant of that root trace

#### Scenario: Named spans for conceptual pipeline phases

- **GIVEN** valid cloud tracing credentials are configured locally
- **WHEN** a sleuth refresh runs the relevance, summarization, and merge phases
- **THEN** the observability export includes distinctly named spans for the refresh operation, per-segment processing, and the cross-segment merge phase
- **AND** span names describe the phase in plain language rather than opaque generated identifiers alone

## MODIFIED Requirements

### Requirement: Prior summary as merge seed

When a sleuth summary already exists and refresh processes new transcript material, the system SHALL run relevance filtering and batched summarization on new content independently during segment processing, collecting new segment summaries during the refresh batch. The system SHALL merge the prior summary body with those new segment summaries exactly once at refresh batch finalization using hierarchical bounded summarization, treating the prior summary body as the merge seed and not as a duplicate merge input.

#### Scenario: Incremental refresh preserves prior knowledge

- **GIVEN** a sleuth with an existing summary and new unprocessed transcript content
- **WHEN** refresh completes successfully
- **THEN** the updated summary incorporates both prior summary content and newly extracted material
- **AND** the merge step deduplicates overlapping facts between old and new summaries
- **AND** cross-segment merge runs once at batch finalization rather than after each new segment

### Requirement: Optional cloud run observability

When the operator configures cloud tracing credentials on the local workstation, sleuth refresh runs SHALL export run and step metadata for the refresh pipeline to the configured cloud observability service in a single hierarchical trace tree rooted at the refresh operation. When tracing credentials are not configured, refresh SHALL complete without requiring cloud connectivity and SHALL NOT export run metadata externally.

#### Scenario: Operator enables cloud tracing

- **GIVEN** valid cloud tracing credentials are configured locally for the workstation
- **WHEN** a human requests sleuth refresh
- **THEN** the refresh run exports one root observability trace for the operation with descendant spans for pipeline steps and summarization service calls

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
