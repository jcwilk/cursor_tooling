# openspec-flow-reference Specification

## Purpose
TBD - created by archiving change init-normative-openspec-flow-specs. Update Purpose after archive.

## Requirements

### Requirement: Cohesive Semantic Version identity

OSF reference bundles MUST expose exactly one Semantic Version identifying the interoperability level of every OSF integration component intentionally distributed as a singular upgrade atom.

#### Scenario: Precedence-ready identification
- **WHEN** a consumer inspects OSF reference distribution metadata declaring release identity
- **THEN** exactly one Semantic Version suitable for pairwise ordering is plainly discoverable without reconciling contradictory version claims across OSF integration components bundled for that release

### Requirement: Isolation between proposal shaping and archival reconciliation

OSF workflows MUST distinguish behavioral-intent shaping from reconciling authoritative behavioral specification content unless the initiating human expressly combines those scopes in the same directive.

#### Scenario: Proposal shaping without silent reconciliation
- **WHEN** a worker is tasked solely with shaping or validating OSF behavioral intent artifacts that precede archival
- **THEN** reconciling deltas into OSF authoritative behavioral specifications MUST NOT occur without an explicit archival or finishing directive attributable to OSF apply lifecycle guidance

### Requirement: Dedicated execution modality for OSF apply lifecycle

OSF MUST designate a delegated execution pathway for OSF apply-related lifecycle roles so high-impact repository operations prescribed by OSF are not satisfied by conversational replay alone.

#### Scenario: Mandatory delegation documentation
- **WHEN** OSF documentation assigns apply, reconciliation, finish, or abort responsibilities that may alter repository-wide state
- **THEN** those responsibilities MUST mandate execution through OSF’s delegated Task-compatible pathway rather than direct conversational emulation of OSF agent-definition narratives

### Requirement: Behavioral specification supremacy post-archival

When OSF authoritative behavioral specifications have been reconciled through archival for a merged change, OSF MUST treat reconciled authoritative behavioral specification statements as authoritative over OSF narrative prose when enforcing behaviors they both describe.

#### Scenario: Narrative divergence after archival
- **WHEN** reconciled OSF authoritative behavioral specification content conflicts with OSF narrative descriptions covering the same responsibility
- **THEN** reconciled OSF authoritative behavioral specification content governs conformance until superseded via a subsequent OSF change that archives replacements

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
- **AND** MUST report the gap to the parent without reconciling living specifications while operational obligations remain unmet

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

OSF documentation and workers MUST treat archival reconciliation success as distinct from apply-complete when the approved task list includes operational delivery or live verification obligations, or when uncommitted or untracked worktree changes attributable to the apply unit remain unresolved. Apply-complete REQUIRES archive-complete plus class-appropriate evidence (or authorized override) for every non-deferred task, and REQUIRES that apply-attributable worktree leftovers have been incorporated into the delivered change or discarded. OSF MUST NOT describe an apply unit as apply-complete while those leftovers remain. Archive-complete means living behavioral specifications are reconciled on the working branch through OSF archival; it does not require integration into the repository default branch.

#### Scenario: Merge without operational proof
- **WHEN** a change archives while non-deferred operational tasks lack evidence or authorized override
- **THEN** OSF MUST NOT describe the apply unit as apply-complete
- **AND** reviewers relying on the task list and debrief MUST be able to see either execution evidence or an abort blocker

#### Scenario: Merge with unresolved apply-attributable leftovers
- **WHEN** a change archives while uncommitted or untracked worktree changes attributable to the apply unit remain
- **THEN** OSF MUST NOT describe the apply unit as apply-complete
- **AND** the finish debrief MUST surface those leftovers as unresolved hygiene rather than as an authorized success warning alone

#### Scenario: Unrelated concurrent dirt does not deny apply-complete
- **WHEN** the only remaining worktree dirt is attributed to unrelated concurrent work outside the apply unit
- **AND** operational evidence obligations are otherwise satisfied
- **THEN** OSF MAY describe the apply unit as apply-complete
- **AND** the debrief MUST note the excluded paths so humans can see what was left untouched

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
- **AND** MUST record such issues in the debrief ambiguities section when they affect approval or apply

#### Scenario: Approve implies execution contract
- **WHEN** a human is prompted to approve an apply run after review
- **THEN** the approval guidance MUST state that apply will execute in-scope tasks or abort rather than archive with silent operational gaps

### Requirement: Change debrief places skim sections at document end

Human-facing whole-change debriefs MUST use a short fixed section set with no separate long-form drill-down body. After change metadata, the debrief MUST present, in order: a concise characterization of specification-delta shape; ambiguities with significance; operational apply scope; a narrative quick read; and approve-or-refine guidance. Every section in that set MUST appear on every whole-change debrief.

#### Scenario: Whole-change debrief layout
- **WHEN** a whole-change debrief is rendered for human review
- **THEN** the body after change metadata MUST consist of the specification-delta-shape section, then ambiguities, operational apply scope, narrative quick read, and approve-or-refine guidance in that order
- **AND** MUST NOT insert separate long-form sections that inventory intent, requirement-by-requirement deltas, capability tables, design highlights, task groups, or post-archive living-spec path lists

#### Scenario: Ambiguities when none
- **WHEN** a whole-change debrief has no material ambiguity for approve or apply
- **THEN** the ambiguities section MUST state that none exist rather than omitting the section

#### Scenario: Fast review path
- **WHEN** a reviewer skims a whole-change debrief for approve-or-refine
- **THEN** change metadata plus the fixed short section set MUST be sufficient without separate long-form drill-down sections

#### Scenario: All sections always present
- **WHEN** a whole-change debrief is rendered
- **THEN** each required section in the fixed set MUST appear even when its content is a short empty-state line

### Requirement: Change debrief ambiguities carry significance

Human-facing whole-change debriefs MUST summarize material ambiguities in a dedicated closing section with concise bullets that each state how significant the ambiguity is for approval or apply.

#### Scenario: Material ambiguity exists
- **WHEN** review detects unclear task wording, conflicting scope, spec-quality concerns, or operational preconditions that are not explicit
- **THEN** the debrief MUST list each issue as a short bullet with a significance indicator
- **AND** MUST NOT list those issues only in the approve-or-refine action lines while omitting the ambiguities section

#### Scenario: No material ambiguity
- **WHEN** review finds no ambiguity that affects approval or apply scope
- **THEN** the ambiguities section MUST explicitly state that none exist

### Requirement: Approve-or-refine action lines stay minimal

Human-facing whole-change debriefs MUST keep approve-or-refine guidance to brief action lines without restating content from preceding sections.

#### Scenario: Standard decide block
- **WHEN** a whole-change debrief includes ambiguities, operational apply scope, and quick read sections
- **THEN** the approve-or-refine block MUST limit itself to concise Approve, Refine, and Abort lines
- **AND** MUST NOT cross-reference or duplicate those preceding sections

### Requirement: Proposal shaping confines writable scope to active change artifacts

When a worker is tasked solely with OSF proposal shaping, the worker MUST treat only the active change folder under OSF changes as writable for that turn and MUST NOT mutate OSF implementation surfaces until an approved apply run executes the change task list.

#### Scenario: Propose turn with concrete bundle targets named
- **WHEN** a worker receives OSF proposal shaping work that names integration skills, Task agents, or bundle operational documentation as eventual edit targets
- **THEN** the worker MUST record those targets in change artifacts for human review
- **AND** MUST NOT edit those surfaces during the proposal shaping turn

#### Scenario: Healthy propose end state
- **WHEN** a worker completes OSF proposal shaping for a change
- **THEN** the durable output MUST be validated artifacts under that change folder
- **AND** implementation surfaces outside that folder MUST remain unchanged by that turn

### Requirement: Apply workers use pre-established branch context

OSF apply orchestration and apply workers MUST execute on the repository branch and worktree context already established when apply is invoked and MUST NOT create branches, add worktrees, or spawn parallel apply lanes as part of OSF apply skill or agent guidance.

#### Scenario: Apply invoked after human branch setup
- **WHEN** a human invokes OSF apply after choosing a branch or worktree
- **THEN** the apply worker MUST perform task execution on that context without OSF apply instructions mandating new isolation setup

#### Scenario: Multiple changes desired
- **WHEN** a human wants concurrent work on multiple OSF changes
- **THEN** concurrency MUST be arranged outside OSF apply orchestration
- **AND** OSF apply skills MUST NOT prescribe issuing parallel apply workers for multiple changes in one orchestration turn

### Requirement: Apply workers resolve apply-attributable worktree leftovers by incorporate or discard

OSF apply workers MUST resolve uncommitted and untracked worktree changes attributable to the apply unit by incorporating them into the delivered change or discarding them before handing off for apply-complete. Workers MUST NOT treat such leftovers as a reason to abort when incorporate or discard remains available.

#### Scenario: Agent-created scratch after tasks
- **WHEN** an apply unit created ephemeral files or caches that are not part of the delivered change
- **THEN** the apply worker MUST discard them before finish claims apply-complete
- **AND** MUST NOT abort solely because those leftovers existed

#### Scenario: Agent changes that belong to the change
- **WHEN** an apply unit produced uncommitted edits that implement approved tasks
- **THEN** the apply worker MUST incorporate them into the delivered change before finish claims apply-complete

### Requirement: Apply scratch and ephemeral helpers stay out of ad-hoc repository locations

OSF apply workers MUST place tool caches and disposable helpers in project-documented intermediate locations when those exist, otherwise in the operating system's temporary area, and MUST NOT invent ad-hoc repository locations for caches or throwaway drivers. Disposable live-acceptance helpers MAY be used when a one-off is the proportionate approach; such helpers MUST be discarded before apply-complete unless the approved change intentionally delivers them as lasting project assets.

#### Scenario: No project intermediate location documented
- **WHEN** an apply worker needs a temporary directory for caches or a disposable helper and the project does not document an intermediate location
- **THEN** the worker MUST use the operating system's temporary area
- **AND** MUST NOT create a new ad-hoc directory inside the repository worktree for that purpose

#### Scenario: Proportionate disposable helper
- **WHEN** live acceptance needs a one-off helper that is not worth promoting to a lasting project asset
- **THEN** the worker MAY create that helper outside the lasting source layout
- **AND** MUST discard it before apply-complete

### Requirement: Unrelated concurrent worktree changes are excluded from apply hygiene

When an OSF apply worker's best understanding is that a worktree change originated from unrelated concurrent work by another agent, user, or process, the worker MUST exclude that change from apply hygiene obligations and MUST NOT commit, discard, or rewrite it as part of apply cleanup. Exclusions MUST be stated in finish verification notes or the debrief.

#### Scenario: Foreign untracked path during apply
- **WHEN** an unexplained path appears that the apply worker did not create and attributes to unrelated concurrent work
- **THEN** the worker MUST leave that path untouched for hygiene purposes
- **AND** MUST record the exclusion in verification notes or the debrief
- **AND** MUST NOT abort or rewrite the apply unit solely to manage that path

#### Scenario: Uncertainty favors exclusion
- **WHEN** the apply worker cannot confidently attribute a leftover path to the apply unit
- **THEN** the worker MUST treat it as excluded concurrent dirt rather than discarding it
- **AND** MUST call out the uncertainty in the debrief

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

### Requirement: Finish completes on working branch by default

When OSF finish succeeds under default guidance, the finish worker MUST verify the approved change, archive it on the working branch so living behavioral specifications reconcile on that branch, commit the archival result on the working branch, and MAY push that working branch to its remote tracking branch when push is not waived. Default finish MUST NOT check out the repository default branch, MUST NOT merge the working branch into the default branch, and MUST NOT push the default branch unless the initiating human explicitly authorized default-branch integration in the same finish directive.

#### Scenario: Default successful finish
- **WHEN** finish runs without an explicit default-branch integration override
- **AND** verification and archival succeed on the working branch
- **THEN** living behavioral specifications are reconciled on the working branch
- **AND** the finish worker pushes only the working branch when remote push is part of the finish directive and not waived

#### Scenario: Explicit default-branch integration
- **WHEN** the initiating human explicitly authorizes default-branch integration in the same finish directive
- **THEN** the finish worker MAY merge the working branch into the default branch and push the default branch
- **AND** MUST record that override in the finish debrief

#### Scenario: Finish without remote push
- **WHEN** the finish directive waives remote push
- **THEN** finish MUST still complete archival reconciliation on the working branch
- **AND** MUST NOT treat absence of remote push as failure when archival succeeded locally
