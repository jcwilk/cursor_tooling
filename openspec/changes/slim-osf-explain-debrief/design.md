## Context

`osf-explain` was expanded (notably under apply-operational-completeness) into a dual-path document: long spec-reviewer drill-down, then a footer skim. In practice the full dump is noisy, and the skillfile repeats layout rules many times while also re-hosting spec-quality flag definitions that already live under `/osf-propose`.

## Goals / Non-Goals

**Goals:**

- Fixed short whole-change debrief: metadata → spec delta shape → Ambiguities → Apply scope → Quick read → Decide; **all mandatory**.
- Spec delta shape answers “what kind of spec change, roughly how much?” in a sentence or two—not a catalog of requirements.
- Skillfile becomes short and readable; quality definitions deferred to propose; CLI ritual stated once briefly.
- Multi-change / single-artifact scope resolution kept, tightened.

**Non-Goals:**

- Changing Ambiguities significance labels or Apply scope semantics.
- Removing operational apply-scope surfacing before approve.
- Building a new debrief tool or CLI formatter.
- Rewriting propose’s spec-quality bar (only cross-link from explain).

## Decisions

1. **One shape section replaces eight drill-downs**  
   Drop Intent, Changelog summary, Capability impact, Delta details, Spec-quality flags, Design highlights, Tasks, Living-spec impact as separate rendered sections. Their useful residue for approval is: delta-shape blurb + Ambiguities (including quality concerns) + Apply scope + Quick read + Decide.  
   *Example voice:* “Strictly new scenarios on factory-builder-thing—about three, OSHA-compliance flavored.”  
   *Alternatives considered:* keep Intent + footer only (still duplicates Quick read); keep Changelog table (still inventory-like).

2. **All remaining sections mandatory**  
   No “omit when empty” for structural sections; Ambiguities still uses `None` when clean; Apply scope still has the existing empty-state sentences; Spec delta shape always states kind/scale (including “docs/process only, no requirement deltas” when true).

3. **Skillfile structure (apply target)**  
   Keep: when-to-run, tightened scope resolution, short CLI how/why, verbatim short template, slim behavior rules, reference to propose for quality definitions. Cut: duplicated flag catalog, repeated fast-pass essays, long single-artifact matrices reduced to a small table pointing at the same section set (subset rules only where a named artifact cannot supply a section—e.g. design-only may still need the mandatory shells filled from available context or `None`/N/A-style honesty without inventing deltas).

4. **Living-spec update**  
   MODIFY the layout requirement that currently mandates drill-down-before-footer; ADDED (or folded) requirement for the delta-shape characterization. Ambiguities / approve-or-refine requirements stay; adjust scenarios that assume intermediate drill-down.

5. **Propose handoff**  
   One-line update: explain close-out uses the short template; do not tell agents to dump removed sections.

## Risks / Trade-offs

- **[Less detail for deep spec review]** Reviewers who relied on Delta details in chat must open the change folder → Mitigation: metadata Path + delta-shape points them there; artifacts remain source of truth.
- **[Vague delta-shape]** Agents write fluffy blurbs → Mitigation: skill examples of good vs bad shape lines; Ambiguities if shape is unclear.
- **[Single-artifact mode]** Subsets vs “all mandatory” tension → Mitigation: whole-change is primary; artifact-scoped runs still lead with metadata and fill every section from available evidence or an explicit unavailable note—do not resurrect long drill-downs.

## Migration Plan

- Rewrite `osf-explain` skill in place; bump bundle version; update `OPENSPEC_FLOW.md` one-liner.
- No artifact migration for in-flight changes; next explain/propose close-out uses the new shape after apply.

## Open Questions

- None blocking; section title string (`## Spec delta shape` vs similar) can be chosen at apply for readability.
