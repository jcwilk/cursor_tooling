## 1. Orchestration (`osf-apply-changes`)

- [ ] 1.1 Add **Task prompt contract** section: MAY add constraints; MUST NOT subtract approved `tasks.md` work unless same-message human opt-out; define verify-existing-work as complete all non-deferred tasks including ops classes.
- [ ] 1.2 Add worked examples of **forbidden** prompt softening (e.g. “local smoke enough,” “may skip environment verification”) vs allowed additions.

## 2. Apply worker (`osf-apply-start`)

- [ ] 2.1 Add **Task classes** table (implementation, build/release artifact, environment acceptance, tooling-only) with evidence rules per class.
- [ ] 2.2 Replace vague “smoke where safe” with class-based rules: weaker checks not substitutes; required environment task blocked → abort, no `[x]`, no finish.
- [ ] 2.3 Require finish handoff **verification notes** to list per-class evidence (commands, artifact ids, URLs) for ops tasks completed this run.
- [ ] 2.4 Clarify **`all_done` from CLI**: if `tasks.md` still has required ops rows `[ ]`, continue Step 4; do not skip to finish solely on CLI progress when human-visible ops tasks remain.

## 3. Finish worker (`osf-apply-finish`)

- [ ] 3.1 Expand Step 1 **Verify** with ops evidence gate: build/release and environment acceptance require implementer evidence or explicit prompt override; fail closed otherwise.
- [ ] 3.2 Extend debrief template fields: **Operational evidence** (succeeded / missing / override) separate from checkbox state.

## 4. Propose (`osf-propose`)

- [ ] 4.1 Add **`tasks.md` discipline** section: default ops tasks to `[ ]`; pre-check only with human attestation of named verified environment; required vs `## Explicitly deferred` structure; ban “optional follow-up” section titles for in-scope work; keep migration in `design.md` unless mirrored as tasks.
- [ ] 4.2 Add self-check before persist: flag if any build/deploy/acceptance row is `[x]` without attestation in the same turn.

## 5. Explain (`osf-explain`)

- [ ] 5.1 **Reorder change-scope template**: move **Quick read** to the end; place new **`## Apply scope at shipping`** immediately before Quick read (after drill-down: Intent, Changelog, Capability impact, Delta details, Spec-quality flags, Design highlights, Tasks, Living-spec impact).
- [ ] 5.2 Implement **Apply scope at shipping** (short bullets): **In scope for apply**, **Explicitly deferred (by intent)**, **Flags**; heuristics for ops-like tasks; single-line when none; never label skipped required work “optional.”
- [ ] 5.3 Update **fast-pass reading order** in skill front matter and description: metadata → **Apply scope at shipping** → **Quick read** → optionally **What the human needs to decide** (not Intent/Changelog first).
- [ ] 5.4 Update **What the human needs to decide**: Approve text states accepting apply = in-scope tasks run or abort; Refine cites Apply scope flags or spec-quality flags.
- [ ] 5.5 Update **single-artifact** table rows and behavior rules for new section order; note post-apply/finish relay still distinguishes incomplete vs deferred (by intent).
- [ ] 5.6 Mention end-of-debrief skim path in `OPENSPEC_FLOW.md` capability table blurb for `/osf-explain` (one line).

## 5b. Propose handoff (`osf-propose`)

- [ ] 5b.1 In **Debrief — hand off to `/osf-explain`**, note that propose close-out uses the end-of-document skim sections as the primary human approval surface for operational scope.

## 6. Flow docs (`OPENSPEC_FLOW.md`, `AGENTS.md`)

- [ ] 6.1 Add **Apply-complete vs merge-complete** subsection to `OPENSPEC_FLOW.md` (Standard flow + success criterion one-liner from gap analysis).
- [ ] 6.2 Mirror terminal-state distinction in `AGENTS.md` OpenSpec-first workflow (apply vs reconcile completeness).
- [ ] 6.3 Bump `OPENSPEC_FLOW_VERSION` and add `CHANGELOG.md` entry for normative apply behavior change.

## 7. Validation

- [ ] 7.1 Run `npx @fission-ai/openspec@latest validate apply-operational-completeness --type change`.
- [ ] 7.2 Re-read all delta requirements against spec quality checklist (no implementation leakage in delta).
