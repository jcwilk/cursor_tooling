## Required for this change

## 1. Explain skill rewrite

- [x] 1.1 Rewrite `.cursor/skills/osf-explain/SKILL.md` to the short mandatory template: change metadata; one concise **Spec delta shape** (or equivalent title) section; **Ambiguities**; **Apply scope at shipping**; **Quick read**; **What the human needs to decide**—no Intent/Changelog/Capability impact/Delta details/Spec-quality flags/Design highlights/Tasks/Living-spec impact sections.
- [x] 1.2 Tighten scope resolution (whole change default; single artifact; multiple changes sequentially) without repeating layout essays.
- [x] 1.3 Replace the long CLI ritual with a brief how/why for `openspec status` / `openspec validate` feeding Validation and Status metadata lines.
- [x] 1.4 Remove inlined spec-quality flag definitions and severity legend; add a short pointer to `/osf-propose` (and `OPENSPEC_FLOW.md` “What a spec actually is”) for quality definitions; quality issues that affect approve/apply still surface under **Ambiguities**.
- [x] 1.5 Keep behavior rules but tighten: read-only, no persist, no full requirement paste, CLI truth for status/validate, Decide stays action-lines-only, one canonical template.
- [x] 1.6 Delete repeated fast-pass / don’t-duplicate / omit-empty reminder sprawl; keep only what the short template still needs (e.g. Ambiguities `None` when clean).

## 2. Callers and narrative

- [x] 2.1 Update `.cursor/skills/osf-propose/SKILL.md` debrief handoff so it describes the short explain template (not the old footer-after-drill-down framing).
- [x] 2.2 Update the `/osf-explain` row in `OPENSPEC_FLOW.md` to match the short section set.
- [x] 2.3 Bump `OPENSPEC_FLOW_VERSION` and add a `CHANGELOG.md` entry noting the **BREAKING** shorter explain debrief.

## 3. Validation

- [x] 3.1 Run `npx @fission-ai/openspec@latest validate slim-osf-explain-debrief --type change` and sanity-check that a sample mental render of the new template has exactly the mandatory sections and no resurrected drill-downs.

## Explicitly deferred

- None.
