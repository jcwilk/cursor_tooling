## ADDED Requirements

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
