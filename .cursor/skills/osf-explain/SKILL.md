---
name: osf-explain
description: Renders a structured, consistent human-review summary of an OpenSpec change under `openspec/changes/<name>/`. Fast pass: **Intent** → structured **Changelog summary** (added/changed/removed/moved/explicitly unchanged) → narrative **Quick read**; then capability table, requirement-level deltas, flags, and apply hints. Use for `/osf-explain`, attached skill, explain/summarize/debrief/review requests, or when `/osf-propose` closes out via this template.
disable-model-invocation: true
---

# `/osf-explain` — structured OpenSpec change debrief

Produces a fixed-template explanation of an OpenSpec change so a human can review intent and spec operations quickly and reliably. **The point of this skill is consistency**: same shape, same headings, same flags, every time. Refine the template *here* when reviewer needs change; do not freelance the format inside other skills.

**Fast-pass reading order** (whole change): after the **`## Change:`** metadata block, render **`## Intent`** → **`## Changelog summary`** → **`## Quick read`**. Those three are the “front page”; everything after is drill-down (tables, requirement names, flags, apply hints).

This skill is **read-only**: it never edits the change folder, never persists, never runs `apply`/`archive`. If review surfaces a fix, route the user back to **`/osf-propose`**.

## When this skill runs

- User says **`/osf-explain`**, attaches this skill, or asks to "explain / summarize / debrief / review" a specific OpenSpec change or artifact.
- Another skill — typically **`/osf-propose`** — calls into this skill at the end of its turn to render its closing debrief. **All `osf-propose` debriefs go through this skill, not freeform.**

## Resolve scope before reading anything

Decide the subject, then read every artifact in scope before drafting output.

1. **Whole change** (default): one folder under `openspec/changes/<name>/`. Pull the name from the user, the calling skill, or — if neither is provided — pick the most recently modified non-archived change folder under `openspec/changes/` and confirm the choice in chat.
2. **Single artifact**: when the user names one (`proposal`, `design`, `specs`, `specs/<capability>`, or `tasks`).
3. **Multiple changes**: render the change-scope template once per change in sequence; do not interleave.

For change-scope, read the change's `proposal.md`, `design.md` (if present), every `specs/<capability>/spec.md`, and `tasks.md`. Also run:

```bash
npx @fission-ai/openspec@latest status --change "<name>" --json
npx @fission-ai/openspec@latest validate "<name>" --type change
```

so the **Validation** and **Status** lines come from the CLI, not from a guess. If validation fails, surface the exact CLI output — do not paraphrase it away.

## Output template — do not improvise

Render the template below verbatim (Markdown headings, table headers, bullet labels). Fill bracketed slots from the artifacts. **Quick read** = **3–7** short narrative bullets (or, rarely, **2** very tight paragraphs if the story resists bullets); plain language only; no changelog or Intent duplication; capability names OK, requirement names sparse.

Omit a section only when the artifact is genuinely absent (e.g. `design.md` was skipped in Lite mode); never collapse two sections into one. Keep bullets short — reviewer fatigue is the failure mode, not under-explaining.

### Change-scope template

```markdown
## Change: `<change-name>`

- **Path**: `openspec/changes/<change-name>/`
- **Validation**: `<pass | fail — exact CLI excerpt>`
- **Status**: `<artifact ids that are done / ready / blocked, from openspec status>`
- **Branch & commits**: `<branch>` — `<short SHAs touching this change folder, or "uncommitted">`

## Intent (from `proposal.md`)

- **Why**: <one or two sentences, tight paraphrase of the proposal's "Why">
- **What changes**: <one bullet per item from the proposal's "What Changes">

## Changelog summary

Structured **release-notes rollup** from the delta `spec.md` files plus explicit **non-goals / stability** from `proposal.md` or `design.md`. **Do not paste full requirement bodies** — capability grouping + one-line behavior hints only. **Derive from the artifacts you read**; this section appears **before** **Delta details** in output, but must stay **consistent** with those deltas.

Use the subheadings below **in this order**. **Omit a subheading entirely** when it would be empty (do not write `None`, `(n/a)`, or filler).

### Added

- <NEW capabilities: behavior bullets grouped under each capability; include net-new `ADDED` requirements under a MODIFIED capability; optional cross-cutting bullets from `proposal.md` / `tasks.md` when *material* — e.g. planned doc/process moves to `AGENTS.md` / `OPENSPEC_FLOW.md`>

### Changed

- <`MODIFIED` requirements: which capability + one line on what shifted>

### Removed

- <`REMOVED` requirements: name + after archive either **where it migrated** (target capability from the delta’s Reason/Migration) or **dropped** if the change truly retires behavior; a small Markdown table is fine when many rows leave one capability>

### Moved / relocated

- <Cross-capability moves: “from `capability-a` → `capability-b`” in plain language; process or authoring rules lifted out of `spec.md` into repo docs per proposal/tasks>

### Explicitly unchanged

- <Only when `proposal.md` or `design.md` states non-goals, explicit stability, or “no runtime/API change”; one tight bullet each>

## Quick read

- <plain-language bullet: what is different after archive — capabilities, boundaries, “artifacts in the world”; avoid requirement names unless one is unavoidable>
- <plain-language bullet: why it matters — operators, humans, agents; clarity, safety, scope, risk>
- <optional bullet: explicit non-goals / out-of-scope from proposal or design>
- <add bullets until **3–7** substantive lines total; omit empty bullets>

## Capability impact

| Capability | Operation | Notes |
|---|---|---|
| `<capability-a>` | NEW | <one-line scope> |
| `<capability-b>` | MODIFIED | <one-line summary of what shifts> |
| `<capability-c>` | REMOVED-FROM | <which requirements leave this living spec> |

## Delta details

### `<capability>` — <NEW | MODIFIED | REMOVED-FROM>

- **ADDED Requirements**:
  - `<Requirement Name>` — <one-line behavior summary>
- **MODIFIED Requirements**:
  - `<Requirement Name>` — <plain-language description of what shifted; do not paste full text>
- **REMOVED Requirements**:
  - `<Requirement Name>` — **Reason:** <…>; **Migration:** <…>
- **RENAMED Requirements**:
  - `<FROM>` → `<TO>`

(Repeat per capability touched. Skip subsections that are empty for a given capability.)

## Spec-quality flags

For each delta `spec.md`, run the OpenSpec quick test (implementation can change without changing externally visible behavior). List **only flags raised**, not all checks performed. If none, write a single line: `No flags raised.`

- 🔴 **Implementation leakage** — <which requirement, which leak: script name / file path / shell command / library / schema key>
- 🟡 **Process or workflow rule in `spec.md`** — <which requirement>
- 🟡 **Self-referential requirement** (about how the spec file itself looks) — <which requirement>
- 🟡 **Mixed bounded contexts** in one capability — <which capability, which requirements>
- 🟡 **Requirement missing a `#### Scenario:`** — <which requirement>
- 🟡 **Other** — <short label, requirement reference>

## Design highlights (from `design.md`)

- **Decisions that matter for review**: <2–4 bullets, each one line>
- **Risks / trade-offs**: <if listed in design.md>
- **Migration / rollback**: <if listed in design.md>

## Tasks (from `tasks.md`)

- **Groups**: <`## 1. <name>`, `## 2. <name>`, …>
- **Touchpoints outside the change folder**: <files/dirs the apply phase will edit, e.g. `README.md`, source trees, `scripts/**`, config — infer from `tasks.md`>

## Living-spec impact at archive

After **`/osf-apply-finish`**:

- `openspec/specs/<capability>/spec.md` — <CREATED | UPDATED: requirement names added/modified/removed>
- (one bullet per affected living spec)

## What the human needs to decide

- **Approve** → run `/osf-apply-changes` to spawn an apply worker.
- **Refine** → cite a spec-quality flag or section above and re-enter via `/osf-propose`.
- **Abort** → say so; the change folder stays for revision and no implementation runs.
```

### Single-artifact templates

Render only the relevant subset of the change-scope template. Keep the section headings unchanged so reviewers recognize the shape.

| Subject | Sections to render |
|---|---|
| `proposal` | **Intent**, **Changelog summary** (intent-level only — from proposal’s capability / “What Changes”; skip requirement-level unless delta specs are in scope), **Quick read** (from proposal / design only; do not invent requirement detail), **Capability impact** (from proposal if deltas not in scope), **What the human needs to decide** |
| `design` | **Design highlights** |
| `specs` (all) or `specs/<capability>` | **Changelog summary** (capabilities in scope), **Quick read** (qualitative; scoped to those capabilities), **Capability impact**, **Delta details** (for the requested capability or all of them), **Spec-quality flags**, **Living-spec impact at archive** |
| `tasks` | **Tasks**, **What the human needs to decide** |

Always lead with the `## Change: <change-name>` block and the path/validation/status/branch lines so the artifact stays anchored to its change.

## Spec-quality flag rules

These are the rules `osf-propose` writes against; this skill is the place reviewers see them surface. Apply them to every delta `spec.md` you summarise.

- **Implementation leakage** (🔴): a requirement names a specific script, file path, shell command, library, or YAML/JSON key. **Quick test**: would renaming the script or swapping the command force a `MODIFIED` requirement with no behavioral consequence? If yes → flag.
- **Process / workflow rule in `spec.md`** (🟡): e.g. "doing X SHALL NOT require an OpenSpec change" or anything about authoring discipline. Belongs in `AGENTS.md` / `OPENSPEC_FLOW.md`.
- **Self-referential requirement** (🟡): requirements describing how `spec.md` itself looks (no markdown table here, etc.).
- **Mixed bounded contexts** (🟡): a single capability spec carries requirements that belong to two or more independently-testable domains.
- **Missing scenario** (🟡): every requirement should have at least one `#### Scenario:` with `GIVEN` / `WHEN` / `THEN` bullets.
- **Other** (🟡): anything that fails the OpenSpec "behavior contract, not implementation plan" rule but doesn't fit the categories above; explain in one line.

Severity legend (use exactly these):

- 🔴 **blocking** — should be fixed before approve.
- 🟡 **discuss** — reviewer may still approve; should be acknowledged.

## Behavior rules

- **No implementation, no editing artifacts.** This skill is read-only on the change folder.
- **No persist commit from this skill.** Other skills (notably `osf-propose`) call this skill *after* their persist step and pass the change name; `osf-explain` itself never stages or commits files.
- **Do not paste full requirement text** unless the user explicitly asks for it. Names plus one-liners only.
- **Cite paths inline** so the reviewer can jump straight to the artifact (`openspec/changes/<name>/specs/<capability>/spec.md`).
- **CLI is the source of truth for status and validation.** Use `openspec status` / `openspec validate`; never invent a result.
- **Changelog summary** + **Quick read** are the fast front page after **Intent**: changelog = structured Added/Changed/Removed/Moved/Unchanged; **Quick read** = short qualitative story **without** repeating either changelog or intent verbatim. Both must stay consistent with **Delta details** below.
- **One template, every time.** If the canonical template needs to evolve, edit *this* file rather than diverging in callers.

## Reference

- `OPENSPEC_FLOW.md` → "What a spec actually is" — the rules powering the spec-quality flags.
- `.cursor/skills/osf-propose/reference/concepts.md` — vendored OpenSpec concepts doc.
- `AGENTS.md` — `openspec/` workflow discipline (read-only living specs, archive-only merges).
- `.cursor/skills/osf-propose/SKILL.md` — primary caller of this skill for closing debriefs.
