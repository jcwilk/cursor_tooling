## ADDED Requirements

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

## MODIFIED Requirements

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
