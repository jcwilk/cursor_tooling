## Why

Whole-change `/osf-explain` debriefs grew into a long, overlapping template (intent, changelog, capability table, delta details, flags, design, tasks, living-spec impact, then footer). Reviewers mostly need a short approval skim; the skillfile itself became hard to maintain because the same guidance was repeated in prose, template comments, and duplicated quality-flag definitions.

## What Changes

- **BREAKING (debrief shape):** Replace drill-down sections (Intent through Living-spec impact) with **one** mandatory concise **spec delta shape** section (kind + subjective scale of specification changes—not a requirement inventory).
- Keep change **metadata** and the four footer sections (**Ambiguities**, **Apply scope at shipping**, **Quick read**, **What the human needs to decide**); make **every** remaining section mandatory.
- Slim `.cursor/skills/osf-explain/SKILL.md`: tighten scope resolution (including multi-change), brief CLI status/validate note, point at `/osf-propose` for spec-quality definitions instead of inlining them, keep trimmed behavior rules, drop repeated fast-pass/omit/duplicate reminders.
- Align living-spec debrief layout requirements and the one-line `/osf-explain` blurb in `OPENSPEC_FLOW.md`; touch `osf-propose` handoff wording only as needed for the shorter template.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `openspec-flow-reference`: Replace “drill-down then skim footer” debrief layout with a short fixed mandatory section set including a concise spec-delta-shape characterization.

## Impact

- `.cursor/skills/osf-explain/SKILL.md` (primary)
- `openspec/specs/openspec-flow-reference/spec.md` (via archive)
- `OPENSPEC_FLOW.md` capability table line for `/osf-explain`
- Possibly one paragraph in `.cursor/skills/osf-propose/SKILL.md` debrief handoff
- Bundle version / `CHANGELOG.md` on apply
