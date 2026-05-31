## ADDED Requirements

### Requirement: Apply orchestration preserves approved task scope

When OSF apply orchestration delegates work to an apply worker via a Task prompt, the prompt MUST NOT reduce, downgrade, or waive any unchecked task recorded in the approved change task list unless the initiating human explicitly opts out of that task or task class in the same directive that triggered the apply run.

#### Scenario: Orchestrator adds constraints only
- **WHEN** an apply orchestrator constructs a Task prompt for an approved change whose task list includes release or environment acceptance work still marked incomplete
- **THEN** the prompt MAY add execution constraints such as branch naming, validation commands, and safety boundaries
- **AND** the prompt MUST NOT instruct the worker to skip, soften, or treat as optional any such incomplete task

#### Scenario: Human explicitly narrows scope in the same message
- **WHEN** the initiating human states in the same directive that a specific task or task class is out of scope for this apply run
- **THEN** the orchestrator MAY reflect that opt-out in the Task prompt
- **AND** the approved task list MUST be revised through proposal shaping before a subsequent apply run treats remaining items as required

### Requirement: Verify-existing-work completes non-deferred operational tasks

When a human or orchestrator characterizes an apply run as verifying existing work, merging prior implementation, or similar narrowing language, OSF apply workers MUST still complete every task not recorded as explicitly deferred for that change, including build, release, and environment acceptance tasks.

#### Scenario: Narrow phrasing does not limit to tests-only
- **WHEN** an apply worker receives a directive that emphasizes verification or merge of work already on a branch
- **THEN** the worker MUST execute or obtain evidence for all non-deferred tasks in the approved task list
- **AND** MUST NOT treat repository-level tests alone as sufficient completion when the task list requires operational outcomes

### Requirement: Task-class evidence before completion marking

OSF apply workers MUST classify each task in the approved task list into implementation, build or release artifact, environment acceptance, or tooling-only work, and MUST mark a task complete only when evidence appropriate to that class exists.

#### Scenario: Environment task cannot run
- **WHEN** a required environment acceptance task cannot be executed due to missing access, missing target, or policy constraint
- **THEN** the worker MUST NOT mark that task complete
- **AND** MUST terminate the apply unit through the OSF abort pathway with a recorded blocker

#### Scenario: Weaker checks do not substitute unless authorized in tasks
- **WHEN** a task is environment acceptance class and the approved task list does not explicitly permit local-only verification
- **THEN** local or repository-only checks MUST NOT be treated as completing that task

### Requirement: Finish verification for operational outcomes

Before OSF archives an approved change, the finish worker MUST verify that build, release, and environment acceptance tasks have evidence of execution or an explicit human override authorized in the finish Task prompt, not merely a completed checkbox in the task list.

#### Scenario: Checkboxes without evidence
- **WHEN** all tasks appear checked complete but finish verification notes lack evidence for a build, release, or environment acceptance task
- **THEN** the finish worker MUST NOT archive the change
- **AND** MUST report the gap to the parent without merging operational incompleteness into the default branch

### Requirement: Proposal-time operational tasks stay unchecked by default

During proposal shaping, OSF MUST leave operational tasks—those requiring build artifacts, release publication, or verification against a named live environment—unchecked unless the initiating human attests that the named environment is already verified for this change.

#### Scenario: Implementation exists on a branch
- **WHEN** proposal shaping occurs while implementation already exists on a branch
- **THEN** operational tasks MUST remain unchecked in the task list
- **AND** catch-up on the branch MUST NOT be recorded as proof of deploy or live acceptance

### Requirement: Required versus deferred task structure

Approved task lists MUST distinguish work required for the current change from work explicitly deferred to a later change, using structure that prevents agents from treating in-scope operational work as lower priority.

#### Scenario: In-scope production work
- **WHEN** a change requires deploy or live acceptance for delivery
- **THEN** those items MUST appear under required groupings for the change
- **AND** MUST NOT be placed under headings that imply optional or follow-up status for in-scope work

### Requirement: Apply-complete distinct from merge-complete

OSF documentation and workers MUST treat merge and archive success as distinct from apply-complete when the approved task list includes operational delivery or live verification obligations.

#### Scenario: Merge without operational proof
- **WHEN** a change merges and archives while non-deferred operational tasks lack evidence or authorized override
- **THEN** OSF MUST NOT describe the apply unit as apply-complete
- **AND** reviewers relying on the task list and debrief MUST be able to see either execution evidence or an abort blocker

### Requirement: Debrief vocabulary for incomplete versus deferred work

Human-facing OSF debriefs MUST reserve optional or deferred wording for tasks explicitly recorded as deferred by intent, and MUST NOT label skipped required work as optional follow-up.

#### Scenario: Required task not executed
- **WHEN** a debrief summarizes a change whose required operational tasks were not executed
- **THEN** the debrief MUST characterize those items as incomplete or blocked
- **AND** MUST NOT characterize them as optional follow-up

### Requirement: Pre-apply review surfaces operational apply scope

Before an apply run is invoked for an approved change, human-facing change review MUST summarize which operational delivery and live verification tasks are in scope for that apply run versus explicitly deferred by intent.

#### Scenario: Change includes operational tasks
- **WHEN** a human reviews a change whose task list includes build, release, deploy, or live verification work
- **THEN** the review summary MUST list in-scope apply work separately from explicitly deferred work before apply is recommended
- **AND** MUST surface ambiguity flags when operational tasks lack a named environment or conflict with deferral structure

#### Scenario: Approve implies execution contract
- **WHEN** a human is prompted to approve an apply run after review
- **THEN** the approval guidance MUST state that apply will execute in-scope tasks or abort rather than merge with silent operational gaps

### Requirement: Change debrief places skim sections at document end

Human-facing whole-change debriefs MUST place concise skim-oriented summaries after detailed spec and delta drill-down sections so reviewers can read only the closing summaries when appropriate.

#### Scenario: Whole-change debrief layout
- **WHEN** a whole-change debrief is rendered for human review
- **THEN** detailed intent, changelog, capability, delta, flag, design, and task drill-down sections MUST appear before the closing skim sections
- **AND** the closing skim sections MUST include ambiguities with significance, operational apply scope, and a narrative quick read in that order, followed by approve-or-refine guidance

#### Scenario: Ambiguities when none
- **WHEN** a whole-change debrief has no material ambiguity for approve or apply
- **THEN** the ambiguities section MUST state that none exist rather than omitting the section

#### Scenario: Fast review path
- **WHEN** a reviewer uses the documented fast-pass reading order for a whole-change debrief
- **THEN** they MAY read only the change metadata and the closing ambiguities, operational apply scope, and quick read sections without reading intermediate spec drill-down

### Requirement: Change debrief ambiguities carry significance

Human-facing whole-change debriefs MUST summarize material ambiguities in a dedicated closing section with concise bullets that each state how significant the ambiguity is for approval or apply.

#### Scenario: Material ambiguity exists
- **WHEN** review detects unclear task wording, conflicting scope, spec-quality concerns, or operational preconditions that are not explicit
- **THEN** the debrief MUST list each issue as a short bullet with a significance indicator
- **AND** MUST NOT bury those items only inside approve-or-refine prose

#### Scenario: No material ambiguity
- **WHEN** review finds no ambiguity that affects approval or apply scope
- **THEN** the ambiguities section MUST explicitly state that none exist
