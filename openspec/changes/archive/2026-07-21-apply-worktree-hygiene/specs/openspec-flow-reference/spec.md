## MODIFIED Requirements

### Requirement: Apply-complete distinct from merge-complete

OSF documentation and workers MUST treat merge and archive success as distinct from apply-complete when the approved task list includes operational delivery or live verification obligations, or when uncommitted or untracked worktree changes attributable to the apply unit remain unresolved. Apply-complete REQUIRES merge-complete plus class-appropriate evidence (or authorized override) for every non-deferred task, and REQUIRES that apply-attributable worktree leftovers have been incorporated into the delivered change or discarded. OSF MUST NOT describe an apply unit as apply-complete while those leftovers remain.

#### Scenario: Merge without operational proof
- **WHEN** a change merges and archives while non-deferred operational tasks lack evidence or authorized override
- **THEN** OSF MUST NOT describe the apply unit as apply-complete
- **AND** reviewers relying on the task list and debrief MUST be able to see either execution evidence or an abort blocker

#### Scenario: Merge with unresolved apply-attributable leftovers
- **WHEN** a change merges and archives while uncommitted or untracked worktree changes attributable to the apply unit remain
- **THEN** OSF MUST NOT describe the apply unit as apply-complete
- **AND** the finish debrief MUST surface those leftovers as unresolved hygiene rather than as an authorized success warning alone

#### Scenario: Unrelated concurrent dirt does not deny apply-complete
- **WHEN** the only remaining worktree dirt is attributed to unrelated concurrent work outside the apply unit
- **AND** operational evidence obligations are otherwise satisfied
- **THEN** OSF MAY describe the apply unit as apply-complete
- **AND** the debrief MUST note the excluded paths so humans can see what was left untouched

## ADDED Requirements

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
