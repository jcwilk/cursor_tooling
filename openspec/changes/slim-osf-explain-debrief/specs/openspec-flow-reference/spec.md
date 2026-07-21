## MODIFIED Requirements

### Requirement: Change debrief places skim sections at document end

Human-facing whole-change debriefs MUST use a short fixed section set with no separate long-form drill-down body. After change metadata, the debrief MUST present, in order: a concise characterization of specification-delta shape; ambiguities with significance; operational apply scope; a narrative quick read; and approve-or-refine guidance. Every section in that set MUST appear on every whole-change debrief.

#### Scenario: Whole-change debrief layout
- **WHEN** a whole-change debrief is rendered for human review
- **THEN** the body after change metadata MUST consist of the specification-delta-shape section, then ambiguities, operational apply scope, narrative quick read, and approve-or-refine guidance in that order
- **AND** MUST NOT insert separate long-form sections that inventory intent, requirement-by-requirement deltas, capability tables, design highlights, task groups, or post-archive living-spec path lists

#### Scenario: Ambiguities when none
- **WHEN** a whole-change debrief has no material ambiguity for approve or apply
- **THEN** the ambiguities section MUST state that none exist rather than omitting the section

#### Scenario: All sections always present
- **WHEN** a whole-change debrief is rendered
- **THEN** each required section in the fixed set MUST appear even when its content is a short empty-state line

### Requirement: Approve-or-refine action lines stay minimal

Human-facing whole-change debriefs MUST keep approve-or-refine guidance to brief action lines without restating content from preceding sections.

#### Scenario: Standard decide block
- **WHEN** a whole-change debrief includes ambiguities, operational apply scope, and quick read sections
- **THEN** the approve-or-refine block MUST limit itself to concise Approve, Refine, and Abort lines
- **AND** MUST NOT cross-reference or duplicate those preceding sections

## ADDED Requirements

### Requirement: Change debrief characterizes specification delta shape

Human-facing whole-change debriefs MUST include a concise characterization of what kind of specification change the folder contains and a subjective sense of scale, without enumerating individual requirements or pasting delta inventories. The characterization MUST name the affected capability or domain when deltas exist, and MUST state when the change is process or documentation oriented without requirement deltas.

#### Scenario: Additive scenario-focused delta
- **WHEN** a change mainly adds scenarios under an existing capability
- **THEN** the delta-shape section MUST say that the change is primarily new scenarios on that capability and give a rough sense of quantity or thematic focus
- **AND** MUST NOT list each scenario or requirement by name as the main content of that section

#### Scenario: Mixed or structural delta
- **WHEN** a change modifies, removes, or splits requirements across capabilities
- **THEN** the delta-shape section MUST describe that structural kind of change at a summary level
- **AND** MUST remain short enough that a reviewer can absorb it in a glance before reading ambiguities and apply scope

#### Scenario: No requirement deltas
- **WHEN** a change updates process or bundle guidance without specification requirement deltas
- **THEN** the delta-shape section MUST say so explicitly rather than omitting the section
