## ADDED Requirements

### Requirement: Stage-specific inference batch sizing

The system SHALL support independently configurable content sizing parameters for relevance filtering, batched summarization, and hierarchical merge stages during sleuth refresh. Relevance filtering SHALL use a minimum content target and maximum content ceiling. Summarization SHALL use a target content size larger than the relevance minimum. Merge stages SHALL use a target content size and a configurable maximum number of summaries combined per merge group. When not configured, defaults SHALL favor smaller relevance batches and moderate summarize and merge batches aligned with typical prefill performance for locally configured models.

#### Scenario: Operator tunes stage budgets locally

- **GIVEN** a workstation with sleuth processing configuration specifying stage-specific content sizing values
- **WHEN** a human requests sleuth refresh
- **THEN** relevance, summarization, and merge stages each form batches according to their respective configured sizing parameters

#### Scenario: Defaults apply without explicit stage tuning

- **GIVEN** no stage-specific content sizing configuration beyond global processing defaults
- **WHEN** sleuth refresh runs
- **THEN** relevance batches target a smaller content size than summarization or merge batches
- **AND** merge groups combine at most two summaries by default

## MODIFIED Requirements

### Requirement: Bounded relevance batches

When running a relevance pass, the system SHALL present chunks to the summarization service in consecutive batches formed by minimum-target growth: each batch SHALL accumulate consecutive chunks until estimated content reaches a configurable minimum target (default equivalent to roughly two thousand tokens), subject to a configurable maximum content ceiling (default equivalent to roughly fourteen thousand tokens) and a configurable maximum number of chunks per batch. The default maximum chunk count SHALL remain small enough that a human operator can reason about the id list without hundreds of entries (approximately twenty chunks).

#### Scenario: Large segment split across relevance batches

- **GIVEN** more chunks than fit in one batch under minimum-target, maximum-ceiling, and count limits
- **WHEN** relevance processing runs
- **THEN** the system issues multiple relevance requests
- **AND** each request includes at most the configured maximum chunk count
- **AND** each batch's estimated content meets the minimum target when enough chunks remain, except for a final short tail

#### Scenario: Relevance batches stay within ceiling

- **GIVEN** chunks being accumulated for a relevance batch
- **WHEN** adding the next chunk would exceed the configured maximum content ceiling and the current batch already meets the minimum target
- **THEN** the system finalizes the current batch without the overflowing chunk

### Requirement: Batched summarization of filtered chunks

After relevance filtering, the system SHALL group remaining chunks using a configurable summarize-stage content target (default equivalent to roughly eight thousand tokens) and the configured per-batch chunk-count limit, and SHALL produce one pass summary per group. Each pass summary SHALL be bounded to a configurable maximum size (default equivalent to roughly four thousand tokens).

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

When more than one pass summary exists for a segment or refresh unit, the system SHALL recursively merge pass summaries using a configurable merge-stage content target (default equivalent to roughly eight thousand tokens) and a configurable maximum number of summaries per merge group (default two), continuing until one summary remains within a configurable final target (default equivalent to roughly four thousand tokens), deduplicating facts across merged summaries.

#### Scenario: Large session reduces to bounded summary

- **GIVEN** many relevant chunks from one session that produce multiple pass summaries
- **WHEN** hierarchical summarization completes
- **THEN** the session contributes one summary intended to fit the final target size
- **AND** duplicate facts from different pass summaries are not repeated verbatim in the merged result

#### Scenario: Per-pass cap enforced

- **GIVEN** a summarize group with substantial matching content
- **WHEN** a summarize pass runs
- **THEN** the produced summary is instructed and bounded to the configured per-pass maximum

#### Scenario: Merge groups prefer pairwise combination

- **GIVEN** multiple pass summaries eligible for merge in one round
- **AND** no explicit merge fan-in override is configured
- **WHEN** hierarchical merge groups summaries
- **THEN** each merge group contains at most two summaries unless operator configuration raises the limit
