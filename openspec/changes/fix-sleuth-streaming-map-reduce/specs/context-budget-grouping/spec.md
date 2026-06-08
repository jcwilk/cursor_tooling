## ADDED Requirements

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

Context-budget grouping SHALL support configurable total context budget and response headroom. When not configured, the system SHALL use defaults of 16384 tokens for context budget and 1000 tokens for response headroom.

#### Scenario: Defaults apply

- **GIVEN** no explicit budget configuration
- **WHEN** grouping runs
- **THEN** available space for content equals context budget minus prompt overhead minus 1000 tokens reserved for response

#### Scenario: Custom budget honored

- **GIVEN** explicit context budget and response headroom values
- **WHEN** grouping runs
- **THEN** available space reflects those configured values
