## MODIFIED Requirements

### Requirement: Finish verification for operational outcomes

Before OSF archives an approved change, the finish worker MUST verify that build, release, and environment acceptance tasks have evidence of execution or an explicit human override authorized in the finish Task prompt, not merely a completed checkbox in the task list.

#### Scenario: Checkboxes without evidence
- **WHEN** all tasks appear checked complete but finish verification notes lack evidence for a build, release, or environment acceptance task
- **THEN** the finish worker MUST NOT archive the change
- **AND** MUST report the gap to the parent without reconciling living specifications while operational obligations remain unmet

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

### Requirement: Pre-apply review surfaces operational apply scope

Before an apply run is invoked for an approved change, human-facing change review MUST summarize which operational delivery and live verification tasks are in scope for that apply run versus explicitly deferred by intent.

#### Scenario: Change includes operational tasks
- **WHEN** a human reviews a change whose task list includes build, release, deploy, or live verification work
- **THEN** the review summary MUST list in-scope apply work separately from explicitly deferred work before apply is recommended
- **AND** MUST record such issues in the debrief ambiguities section when they affect approval or apply

#### Scenario: Approve implies execution contract
- **WHEN** a human is prompted to approve an apply run after review
- **THEN** the approval guidance MUST state that apply will execute in-scope tasks or abort rather than archive with silent operational gaps

## ADDED Requirements

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
