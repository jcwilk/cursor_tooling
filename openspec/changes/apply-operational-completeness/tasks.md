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

- [ ] 5.1 Extend change-scope template: **Operational completeness** subsection under **Tasks** — required ops tasks, deferred-by-intent only, forbidden “optional” for skipped required work.
- [ ] 5.2 Add behavior rule: after apply/finish debrief relay, distinguish **incomplete** vs **deferred (by intent)**.

## 6. Flow docs (`OPENSPEC_FLOW.md`, `AGENTS.md`)

- [ ] 6.1 Add **Apply-complete vs merge-complete** subsection to `OPENSPEC_FLOW.md` (Standard flow + success criterion one-liner from gap analysis).
- [ ] 6.2 Mirror terminal-state distinction in `AGENTS.md` OpenSpec-first workflow (apply vs reconcile completeness).
- [ ] 6.3 Bump `OPENSPEC_FLOW_VERSION` and add `CHANGELOG.md` entry for normative apply behavior change.

## 7. Validation

- [ ] 7.1 Run `npx @fission-ai/openspec@latest validate apply-operational-completeness --type change`.
- [ ] 7.2 Re-read all delta requirements against spec quality checklist (no implementation leakage in delta).
