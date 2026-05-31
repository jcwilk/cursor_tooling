## 1. Orchestration (`osf-apply-changes`)

- [x] 1.1 Add **Task prompt contract** section: MAY add constraints; MUST NOT subtract approved `tasks.md` work unless same-message human opt-out; define verify-existing-work as complete all non-deferred tasks including ops classes.
- [x] 1.2 Add worked examples of **forbidden** prompt softening (e.g. “local smoke enough,” “may skip environment verification”) vs allowed additions.

## 2. Apply worker (`osf-apply-start`)

- [x] 2.1 Add **Task classes** table (implementation, build/release artifact, environment acceptance, tooling-only) with evidence rules per class.
- [x] 2.2 Replace vague “smoke where safe” with class-based rules: weaker checks not substitutes; required environment task blocked → abort, no `[x]`, no finish.
- [x] 2.3 Require finish handoff **verification notes** to list per-class evidence (commands, artifact ids, URLs) for ops tasks completed this run.
- [x] 2.4 Clarify **`all_done` from CLI**: if `tasks.md` still has required ops rows `[ ]`, continue Step 4; do not skip to finish solely on CLI progress when human-visible ops tasks remain.

## 3. Finish worker (`osf-apply-finish`)

- [x] 3.1 Expand Step 1 **Verify** with ops evidence gate: build/release and environment acceptance require implementer evidence or explicit prompt override; fail closed otherwise.
- [x] 3.2 Extend debrief template fields: **Operational evidence** (succeeded / missing / override) separate from checkbox state.

## 4. Propose (`osf-propose`)

- [x] 4.1 Add **`tasks.md` discipline** section: default ops tasks to `[ ]`; pre-check only with human attestation of named verified environment; required vs `## Explicitly deferred` structure; ban “optional follow-up” section titles for in-scope work; keep migration in `design.md` unless mirrored as tasks.
- [x] 4.2 Add self-check before persist: flag if any build/deploy/acceptance row is `[x]` without attestation in the same turn.

## 5. Explain (`osf-explain`)

- [x] 5.1 **Reorder change-scope template** footer: drill-down first; then **`## Ambiguities`** → **`## Apply scope at shipping`** → **`## Quick read`** → **`## What the human needs to decide`**.
- [x] 5.2 Implement **`## Ambiguities`**: bullets `<Significance> — <issue + path hint>`; labels **Blocking before apply** | **Should fix before apply** | **Discuss / may approve**; aggregate from spec-quality flags, tasks, ops scope, proposal/design; single line `None` when clean; section always present.
- [x] 5.3 Implement **Apply scope at shipping** (no ambiguity list here): **In scope for apply**, **Explicitly deferred (by intent)**; heuristics for ops-like tasks; never label skipped required work “optional.”
- [x] 5.4 Update **fast-pass reading order** (front matter + description): metadata → **Ambiguities** → **Apply scope at shipping** → **Quick read** → optionally **What the human needs to decide**.
- [x] 5.5 **What the human needs to decide**: three standard action lines only; add explicit rule—no cross-references to footer sections, no inline flag dumps, no restating apply scope or ambiguities.
- [x] 5.6 Update **single-artifact** table rows and behavior rules for footer order; note post-apply/finish relay still distinguishes incomplete vs deferred (by intent).
- [x] 5.7 Mention end-of-debrief skim path (Ambiguities → Apply scope → Quick read) in `OPENSPEC_FLOW.md` capability table blurb for `/osf-explain` (one line).

## 5b. Propose handoff (`osf-propose`)

- [x] 5b.1 In **osf-propose** debrief handoff: one line that explain footer carries skim/approval context—do not instruct agents to echo footer content in Decide.

## 6. Flow docs (`OPENSPEC_FLOW.md`, `AGENTS.md`)

- [x] 6.1 Add **Apply-complete vs merge-complete** subsection to `OPENSPEC_FLOW.md` (Standard flow + success criterion one-liner from gap analysis).
- [x] 6.2 Mirror terminal-state distinction in `AGENTS.md` OpenSpec-first workflow (apply vs reconcile completeness).
- [x] 6.3 Bump `OPENSPEC_FLOW_VERSION` and add `CHANGELOG.md` entry for normative apply behavior change.

## 7. Validation

- [x] 7.1 Run `npx @fission-ai/openspec@latest validate apply-operational-completeness --type change`.
- [x] 7.2 Re-read all delta requirements against spec quality checklist (no implementation leakage in delta).
