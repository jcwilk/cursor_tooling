## Why

External consumers report that OSF apply runs often reach **repository-complete** (tasks checked, validated, archived, merged) while remaining **operationally incomplete** (release not built, not deployed, live acceptance not run). The pipeline narrows scope between approved intent and execution—via pre-checked `tasks.md` rows, orchestrator Task prompts that soften requirements, and finish gates that trust checkboxes without evidence—not because humans waived deploy.

## What Changes

- Tighten **orchestration** so parent Task prompts may add constraints but must not subtract approved `tasks.md` work unless the human explicitly opts out in the same message; clarify that “verify existing work” means complete all non-deferred tasks including release and environment acceptance.
- Define **task classes** and evidence-based completion in the apply worker; abort with blocker when required environment work cannot run instead of checking boxes and finishing.
- Add **finish gates** for release, deploy, and live-environment tasks before archive—checkbox presence alone is insufficient without evidence or authorized override.
- Add **propose discipline**: operational tasks default to unchecked; required ship/verify vs explicitly deferred is structurally unambiguous in `tasks.md`.
- Update **flow narrative** (`OPENSPEC_FLOW.md`, `AGENTS.md`) so merge-complete ≠ apply-complete when tasks name live components.
- Update **debrief rules** (`osf-explain`) so “optional” is reserved for explicitly deferred work, not skipped required tasks.
- **Restructure explain output**: footer skim order **Ambiguities** → **Apply scope at shipping** → **Quick read**, then a minimal **What the human needs to decide** (three action lines only—no restating footer content).
- Add **pre-apply review** norm: before `/osf-apply-changes`, explain must surface what apply will and will not execute operationally so approval matches the task contract.
- Bump **`OPENSPEC_FLOW_VERSION`** and **`CHANGELOG.md`** when the bundle edits land.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `openspec-flow-reference`: Add normative requirements for operational completeness across propose, apply orchestration, apply execution, finish, and human-facing debriefs.

## Impact

- `.cursor/skills/osf-apply-changes/SKILL.md`
- `.cursor/agents/osf-apply-start.md`
- `.cursor/agents/osf-apply-finish.md`
- `.cursor/skills/osf-propose/SKILL.md`
- `.cursor/skills/osf-explain/SKILL.md`
- `OPENSPEC_FLOW.md`
- `AGENTS.md`
- Bundle version metadata (`OPENSPEC_FLOW_VERSION`, `CHANGELOG.md`)

No runtime services; consuming projects inherit updated OSF guidance on install/upgrade.
