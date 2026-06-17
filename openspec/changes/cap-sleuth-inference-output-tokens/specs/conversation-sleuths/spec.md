## ADDED Requirements

### Requirement: Stage-specific inference completion limits

Every summarization service call during sleuth refresh SHALL include a hard completion length limit appropriate to the pipeline stage that issued the call. Relevance filtering calls SHALL use a smaller completion limit than summarization and merge calls. When the operator has not configured stage-specific completion limits, defaults SHALL approximate two hundred tokens for relevance filtering and one thousand tokens for summarization and merge stages.

#### Scenario: Relevance call uses a small completion limit

- **GIVEN** sleuth refresh is processing a relevance filtering batch
- **WHEN** the system invokes the configured summarization service for that batch
- **THEN** the request includes a completion length limit sized for a short structured index response
- **AND** the default limit is approximately two hundred tokens when not configured

#### Scenario: Summarize and merge calls use a larger completion limit

- **GIVEN** sleuth refresh is processing a pass summarization or hierarchical merge step
- **WHEN** the system invokes the configured summarization service for that step
- **THEN** the request includes a completion length limit sized for bounded summary text
- **AND** the default limit is approximately one thousand tokens when not configured

#### Scenario: Operator configures completion limits locally

- **GIVEN** a workstation with sleuth processing configuration specifying custom completion length limits for relevance and summary-producing stages
- **WHEN** a human requests sleuth refresh
- **THEN** each inference call uses the configured limit for its stage instead of the default

## MODIFIED Requirements

### Requirement: Batched summarization of filtered chunks

After relevance filtering, the system SHALL group remaining chunks using a configurable summarize-stage content target (default equivalent to roughly eight thousand tokens) and the configured per-batch chunk-count limit, and SHALL produce one pass summary per group. Each pass summary SHALL be bounded to a configurable maximum size (default equivalent to roughly one thousand tokens).

#### Scenario: Filtered chunks summarized in groups

- **GIVEN** several relevant chunks that fit in one summarize batch under the summarize-stage content target
- **WHEN** summarization runs
- **THEN** those chunks are summarized together in one pass
- **AND** the result is a single pass summary for that group

#### Scenario: Single pass summary needs no sibling merge

- **GIVEN** a segment where summarization produces exactly one pass summary
- **WHEN** hierarchical reduction runs for that segment
- **THEN** no additional merge step is required solely to combine sibling pass summaries from that segment

### Requirement: Hierarchical bounded summarization

When more than one pass summary exists for a segment or refresh unit, the system SHALL recursively merge pass summaries using a configurable merge-stage content target (default equivalent to roughly eight thousand tokens) and a configurable maximum number of summaries per merge group (default two), continuing until one summary remains within a configurable final target (default equivalent to roughly one thousand tokens), deduplicating facts across merged summaries.

#### Scenario: Large session reduces to bounded summary

- **GIVEN** many relevant chunks from one session that produce multiple pass summaries
- **WHEN** hierarchical summarization completes
- **THEN** the session contributes one summary intended to fit the final target size
- **AND** duplicate facts from different pass summaries are not repeated verbatim in the merged result

#### Scenario: Per-pass cap enforced

- **GIVEN** a summarize or merge step with substantial matching content
- **WHEN** the summarization service produces a completion for that step
- **THEN** the completion length is bounded by both prompt instructions and the stage-appropriate hard completion limit on the inference request

#### Scenario: Merge groups prefer pairwise combination

- **GIVEN** multiple pass summaries eligible for merge in one round
- **AND** no explicit merge fan-in override is configured
- **WHEN** hierarchical merge groups summaries
- **THEN** each merge group contains at most two summaries unless operator configuration raises the limit
