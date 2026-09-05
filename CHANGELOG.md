# Changelog

All notable changes to this **OpenSpec Flow reference bundle** (docs under this repo root plus `.cursor/skills/osf-*`, `.cursor/agents/osf-*`, and related companion skills documented in `OPENSPEC_FLOW.md`) are recorded here.

The **canonical bundle version** for install/upgrade checks is **`OPENSPEC_FLOW_VERSION`** in the YAML front matter of **`OPENSPEC_FLOW.md`**. This file is a human-readable history; when you cut a release, **bump `OPENSPEC_FLOW_VERSION` and add an entry below** so consumers can compare versions.

## [1.6.0] — 2026-09-04

### Removed

- **Transcript summarization tooling** — removed the Python skill package, local build script, debug probe script, related living specs, and all bundle documentation references.

## [1.5.0] — 2026-07-21

### Changed

- **BREAKING — `/osf-explain` debrief** — whole-change debriefs drop the long drill-down body (Intent through Living-spec impact). Mandatory short section set after metadata: **Spec delta shape** → **Ambiguities** → **Apply scope at shipping** → **Quick read** → **What the human needs to decide**. Spec-quality flag catalogs move to `/osf-propose` / `OPENSPEC_FLOW.md` pointers; quality issues that affect approve/apply still surface under **Ambiguities**. **`osf-propose`** close-out handoff and the `OPENSPEC_FLOW.md` capability-table row updated to match.

### Notes for consumers

Upgrading from 1.4.x: agents and reviewers expecting the old drill-down-then-footer layout will see a shorter approval skim instead. Open the change folder for requirement-level detail.

## [1.4.0] — 2026-07-21

### Changed

- **Apply worktree hygiene** — **apply-complete** now includes resolving apply-attributable uncommitted/untracked leftovers (incorporate or discard). **`osf-apply-start`** documents scratch placement (project intermediates, else OS temp; no ad-hoc in-repo cache homes), disposable-helper allowance, and exclusion of unrelated concurrent dirt. **`osf-apply-finish`** refuses apply-complete labeling when those leftovers remain unresolved; abort stays reserved for intent/safety blockers, not leftover cleanup. **`osf-apply-changes`** Task prompt contract may add hygiene constraints only.

### Notes for consumers

Upgrading from 1.3.x: expect apply workers to clean or commit their own scratch before finish claims apply-complete; concurrent foreign dirt should be listed in verification notes rather than rewritten.

## [1.3.0] — 2026-06-23

### Changed

- **Apply simplification** — **`osf-apply-changes`** and **`osf-apply-start`** assume the **current branch**; OSF apply no longer prescribes branch/worktree creation, parallel multi-change orchestration, or duplicated worker-ownership lists. Finish/abort agents use **working branch** terminology.
- **`/osf-propose` lane lock** — upfront writable-scope section: only the active change folder is writable during proposal shaping; bundle/integration edits belong in approved **`tasks.md`** and apply.
- **`OPENSPEC_FLOW.md`** — **Forbidden lane transitions** subsection; capability table and standard flow updated for current-branch apply.

### Notes for consumers

Upgrading from 1.2.x: humans must choose branch/worktree **before** invoking apply; OSF skills no longer create `apply/<name>` branches or parallel apply lanes.

## [1.2.0] — 2026-05-31

### Changed

- **Operational completeness** — apply orchestration must not soften approved **`tasks.md`** scope; **`osf-apply-start`** classifies tasks (implementation, build/release, environment acceptance, tooling-only) with evidence rules and aborts when required environment work cannot run; **`osf-apply-finish`** gates archive on ops evidence, not checkboxes alone.
- **`/osf-propose`** — **`tasks.md`** discipline: ops tasks default unchecked; required vs **Explicitly deferred** structure; pre-check only with same-turn human attestation.
- **`/osf-explain`** — footer skim order **Ambiguities** → **Apply scope at shipping** → **Quick read** → minimal **Decide**; fast-pass reading order updated.
- **`OPENSPEC_FLOW.md`** / **`AGENTS.md`** — **apply-complete** vs **merge-complete** vocabulary.

### Notes for consumers

Upgrading from 1.1.x changes **behavioral expectations** for apply: verify-existing-work and narrow Task prompts no longer excuse skipping release or live acceptance tasks. Review in-flight changes for pre-checked ops rows and “optional follow-up” section titles.

## [1.1.1] — 2026-05-30

### Changed

- Legacy build-local-tools path cleanup in install skill and docs.

## [1.1.0] — 2026-05-30

### Added

- Additional OSF bundle documentation and install-skill refinements.

## [1.0.1] — 2026-05-28

### Removed

- **`spawn-subagent`** skill — Task delegation rules remain in **`osf-apply-changes`**, **`AGENTS.md`**, and **`OPENSPEC_FLOW.md`**; Cursor subagents no longer need a separate skill.

## [1.0.0] — 2026-05-10

### Added

- Initial **OpenSpec Flow** reference bundle for Cursor: `OPENSPEC_FLOW.md`, generalized **`AGENTS.md`**, skills `osf-explore`, `osf-propose`, `osf-explain`, `osf-apply-changes`, `openspec-flow-install`, Task agents `osf-apply-start`, `osf-apply-finish`, `osf-apply-abort`, plus companion `persist` as documented in `OPENSPEC_FLOW.md`.
- **`CHANGELOG.md`** to track bundle changes alongside **`OPENSPEC_FLOW_VERSION`**.
