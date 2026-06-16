# context-budget-grouping Specification

## Purpose
TBD - created by archiving change fix-sleuth-streaming-map-reduce. Update Purpose after archive.
## Requirements
### Requirement: Ordered context-budget grouping

Given an ordered sequence of text items and a context budget, the system SHALL partition the sequence into consecutive groups such that each group's estimated token total, plus reserved space for prompt overhead and response generation, does not exceed the configured context budget. Grouping SHALL proceed in order from first item to last without reordering items.

#### Scenario: Items fit within one group

- **GIVEN** three items whose combined estimated size fits within the available budget after overhead
- **WHEN** grouping is applied
- **THEN** all three items appear in a single group in their original order

#### Scenario: Items split across multiple groups

- **GIVEN** items whose cumulative size exceeds the available budget
- **WHEN** grouping is applied
- **THEN** items are divided into consecutive groups
- **AND** each group fits within the available budget except where a single item requires truncation

### Requirement: Maximum items per group

Grouping SHALL support a configurable maximum number of items per group. When adding the next item would exceed that maximum and the current group is non-empty, the system SHALL finalize the current group and begin a new group with the next item.

#### Scenario: Count cap splits a token-fitting group

- **GIVEN** items that would fit together by token estimate alone
- **AND** adding one more item would exceed the configured maximum item count
- **WHEN** grouping is applied
- **THEN** the finalized group contains at most the configured maximum number of items
- **AND** remaining items continue in the next group in order

#### Scenario: Default maximum supports short id lists

- **GIVEN** no explicit maximum item count configuration
- **WHEN** grouping runs for relevance or summarization stages
- **THEN** each group contains at most approximately twenty items

### Requirement: Overflow back-off

When adding the next item would exceed the available token budget and the current group already contains at least one item, the system SHALL remove the most recently added item from the current group, finalize that group, and begin the next group starting with the removed item.

#### Scenario: Back-off produces a fitting group

- **GIVEN** a partially filled group where the next item would cause token overflow
- **WHEN** overflow back-off runs
- **THEN** the finalized group excludes the overflowing item
- **AND** the overflowing item opens the next group

### Requirement: Leading item truncation

When the first item alone exceeds the available token budget, the system SHALL truncate that item to the largest prefix that fits, emit the prefix as a group member, and carry the remainder forward as the next item to process in order.

#### Scenario: Oversized leading item is split

- **GIVEN** a single item larger than the available budget
- **WHEN** grouping is applied
- **THEN** the item is split into a fitting prefix and a remainder
- **AND** the remainder is processed in a subsequent group without dropping content

### Requirement: Configurable budget parameters

Context-budget grouping SHALL support configurable total context budget, response headroom, and stage-specific content sizing parameters for relevance filtering, summarization, and merge stages. When not configured, the system SHALL use defaults of 16384 tokens for global context budget, 1000 tokens for response headroom, approximately 2000 tokens minimum and 14000 tokens maximum for relevance batch content, approximately 8000 tokens target for summarization batch content, approximately 8000 tokens target for merge batch content, and a maximum of two summaries per merge group.

#### Scenario: Defaults apply

- **GIVEN** no explicit stage-specific budget configuration
- **WHEN** grouping runs for relevance, summarization, or merge stages
- **THEN** each stage uses the default content sizing parameters for that stage

#### Scenario: Custom budget honored

- **GIVEN** explicit stage-specific content sizing values in local processing configuration
- **WHEN** grouping runs for the corresponding stage
- **THEN** batch formation respects those configured values

### Requirement: Minimum-target batch growth

Given an ordered sequence of text items, a minimum content token target, and a maximum content token ceiling, the system SHALL partition the sequence into consecutive groups by accumulating items until the group's estimated content token total reaches at least the minimum target, then finalizing that group before continuing with remaining items. When adding the next item would cause the group to exceed the maximum ceiling and the current group already meets the minimum target, the system SHALL finalize the current group without the overflowing item. When the current group is below the minimum target and the next item alone exceeds the maximum ceiling, the system SHALL apply leading-item truncation so the emitted prefix fits within the ceiling and SHALL continue processing the remainder in order. When fewer remaining items exist than needed to reach the minimum target, the system SHALL still emit a group containing all remaining items.

#### Scenario: Batch grows until minimum target met

- **GIVEN** consecutive items whose cumulative size crosses the configured minimum content target before reaching the maximum ceiling
- **WHEN** minimum-target grouping runs for relevance filtering
- **THEN** the first group contains enough items that its estimated content total is at least the minimum target
- **AND** the group's estimated content total does not exceed the maximum ceiling

#### Scenario: Batch finalizes before exceeding maximum ceiling

- **GIVEN** a partially filled group that already meets the minimum content target
- **AND** adding the next consecutive item would exceed the maximum ceiling
- **WHEN** minimum-target grouping runs
- **THEN** the current group is finalized without the overflowing item
- **AND** the overflowing item begins the next group

#### Scenario: Short tail below minimum still processes

- **GIVEN** remaining items whose combined estimated size is below the minimum content target
- **AND** no further items remain after them
- **WHEN** minimum-target grouping runs
- **THEN** the system emits one group containing those remaining items

