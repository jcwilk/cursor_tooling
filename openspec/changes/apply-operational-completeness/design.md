## Context

OSF separates **intent** (`/osf-propose` → `openspec/changes/<name>/`) from **execution** (`/osf-apply-changes` → `osf-apply-start` → `osf-apply-finish`). Today, “done” is effectively **all `tasks.md` checkboxes are `[x]` plus validate + archive + merge**. That conflates repository hygiene with operational outcomes (build artifacts, deploy, acceptance on live targets).

The gap analysis identifies a causal chain: mixed implementation + ops tasks → propose may pre-check environment rows → user or orchestrator narrows scope → apply downgrades verification → finish trusts `[x]` → humans inherit “optional” ops that were required in `tasks.md`.

This change updates **documentation and agent/skill contracts** in the reference bundle so each lane fails closed on operational gaps.

## Goals / Non-Goals

**Goals:**

- Make **apply-complete** mean every non-deferred task in approved `tasks.md` was executed with class-appropriate evidence, or the run **aborted** with a recorded blocker.
- Prevent orchestrators from **subtracting** approved task scope in Task prompts.
- Prevent propose from treating **branch catch-up** as proof of deploy/acceptance.
- Structure `tasks.md` so **required for this change** vs **explicitly deferred** is unambiguous.
- Align finish verification with **evidence**, not checkbox state alone, for operational task classes.
- Align debrief vocabulary: **optional** = explicitly deferred in proposal/tasks, not “we skipped it.”

**Non-Goals:**

- Automating deploy or live acceptance in every consumer repo (environments remain project-specific per `AGENTS.md`).
- Changing OpenSpec CLI behavior or schema.
- Retroactively fixing in-flight changes in other repositories (consumers upgrade the bundle and refine their own active changes).

## Decisions

### D1 — Task classes with evidence rules (apply worker)

Introduce four classes referenced in `osf-apply-start` (and mirrored in finish):

| Class | Examples | Complete when |
|-------|----------|----------------|
| **implementation** | code, config, docs in repo | change landed on execution branch; task-directed validation passes |
| **build/release artifact** | images, packages, tagged releases | artifact exists at stated location/version; build command output captured in finish handoff |
| **environment acceptance** | smoke on staging/prod, E2E against live URL | task-directed check ran against named environment; evidence in handoff (command, URL, outcome)—not “local only” unless `tasks.md` explicitly allows |
| **tooling-only** | CLI validate, lint | command succeeded on execution branch |

Weaker checks (e.g. local unit tests) **do not** satisfy **environment acceptance** unless the task text explicitly permits it.

If a required **environment acceptance** task cannot run (no credentials, no target, policy block): **abort** via `osf-apply-abort`; do **not** check the box and delegate finish.

### D2 — Orchestrator prompt contract

`osf-apply-changes` MUST state that the Task prompt:

- **MAY** add: branch name, worktree path, validation commands, safety constraints from `AGENTS.md`.
- **MUST NOT** subtract, downgrade, or waive any `- [ ]` task in approved `tasks.md` unless the **same user message** explicitly opts out of that task or class.
- **MUST** treat phrases like “mostly verify,” “just merge,” or “commit what’s on the branch” as **verify-and-complete remaining tasks**, not “tests then merge.”

### D3 — Propose checkbox and section discipline

`osf-propose` MUST default operational tasks (build, release, deploy, live acceptance) to `- [ ]` even when implementation already exists on a branch. Pre-checking is allowed only when the human states the environment is **already verified** for this change (named target + what was run).

`tasks.md` structure:

- **`## Required for this change`** (or numbered groups without “optional” in the title) — in-scope for apply; all must complete or abort.
- **`## Explicitly deferred`** — out of scope for this apply run; items here MUST NOT be labeled “optional follow-up” elsewhere; explain uses “deferred by intent.”
- Avoid section titles like “optional follow-up” for in-scope production work.
- Migration narrative stays in `design.md`; anything apply must execute appears as checkable tasks.

### D4 — Finish evidence gate

`osf-apply-finish` Step 1 expands: for each task class **build/release artifact** and **environment acceptance**, require **verification notes** from the implementer to cite evidence (command, artifact id, URL, timestamp) or an **explicit user override** in the Task prompt. If implementation is done but operational tasks lack proof, **fail closed** (no archive).

### D5 — Terminal state vocabulary (flow + AGENTS)

Add a short subsection: **Apply-complete vs merge-complete**. Merge-complete = archive + default branch merge (+ push). Apply-complete = merge-complete **and** every non-deferred task has evidence or authorized override; otherwise the run should have aborted.

### D6 — Explain debrief rules

`osf-explain` adds **Apply scope at shipping** (footer): **In scope for apply**, **Explicitly deferred (by intent)** only—no ambiguity list here. Never call skipped required work “optional.”

### D7 — Explain template order (skim at bottom)

**Problem:** Reviewers (including the bundle maintainer) often read only **Quick read**; it currently sits early, before spec minutia, but operational scope was not co-located and approve-time shipping scope was easy to miss.

**New change-scope order:**

1. `## Change:` metadata  
2. **Intent** → **Changelog summary** (drill-down for spec reviewers)  
3. **Capability impact** → **Delta details** → **Spec-quality flags** → **Design highlights** → **Tasks** (groups/touchpoints) → **Living-spec impact at archive**  
4. **End block (skim path, in order):**  
   - **`## Ambiguities`** — short bullets with significance, or a single line `None` when nothing material is uncertain  
   - **`## Apply scope at shipping`** — what apply will attempt vs deferred (operational scope only)  
   - **`## Quick read`** — 3–7 narrative bullets (unchanged role, new position)  
   - **`## What the human needs to decide`** — Approve / Refine / Abort; Refine points to **Ambiguities** (and spec-quality flags in drill-down), not a long inline flag list

**Fast-pass reading order** (skill front matter): metadata → **Ambiguities** → **Apply scope at shipping** → **Quick read** → optionally **What the human needs to decide**. Intent/changelog remain for deep review only.

**Ambiguities** content rules (keep short):

- Pull from: spec-quality flags (🔴/🟡), unclear or conflicting `tasks.md` wording, unnamed environments, pre-checked ops without attestation, misleading section titles, proposal/design vs tasks mismatch, missing non-goals when scope is fuzzy.
- **One bullet per issue**, format: `<Significance> — <what is unclear and where>` (e.g. `Blocking before apply — task 3.2 names "staging" but no URL or host`).
- **Significance labels** (use exactly one per bullet): **Blocking before apply** | **Should fix before apply** | **Discuss / may approve** (map 🔴 blocking flags to first; 🟡 discuss flags to last unless ops-blocking).
- When nothing material: single line `None` (do not omit the section; do not use empty bullet lists).
- Do **not** duplicate the full **Spec-quality flags** drill-down—summarize only what matters for approve/apply; link paths inline when helpful.

**Apply scope at shipping** content rules (keep short):

- **In scope for apply:** unchecked required tasks that imply build, release, deploy, or live verification (one line each; no requirement names unless unavoidable).
- **Explicitly deferred:** items under `## Explicitly deferred` (or equivalent); note owner/follow-up if stated in tasks.
- If no operational tasks: one line `No build, release, or live-environment tasks in scope for apply.`

### D8 — Pre-apply approval contract (via explain)

Approval before apply means resolving **Ambiguities** (or accepting **Discuss** items consciously) and accepting **Apply scope at shipping** as the execution contract—not only delta requirements. `osf-propose` handoff: debrief MUST include the footer block; **Refine** bullet is one line pointing to **Ambiguities** and drill-down **Spec-quality flags**.

### D9 — Version bump

Bump `OPENSPEC_FLOW_VERSION` (e.g. 1.1.1 → 1.2.0) because normative requirements and explain layout change.

**Alternatives considered:**

- **CLI-enforced task classes** — rejected; out of scope; bundle docs/agents are the delivery vehicle.
- **Single “ops” task per change** — rejected; loses granularity; class tags per task line are lighter (optional `(class: environment)` suffix in tasks.md guidance).

## Risks / Trade-offs

- **[Risk] Stricter finish blocks merges when agents lack environment access** → Mitigation: abort path is explicit; human can defer tasks to `## Explicitly deferred` in propose or authorize override in the same message as apply.
- **[Risk] Longer Task prompts** → Mitigation: prompt carries class summary + “do not subtract tasks.md”; worker reads full `tasks.md` anyway.
- **[Risk] Existing active changes with pre-checked ops tasks** → Mitigation: propose refinement pass documented in tasks; not auto-fixed by bundle upgrade.

## Migration Plan

1. Land bundle edits on a branch via `/osf-apply-changes`.
2. Bump `OPENSPEC_FLOW_VERSION`; note breaking *behavioral* expectation for apply consumers in `CHANGELOG.md`.
3. Consuming repos: `/openspec-flow-install` or manual sync; review in-flight `openspec/changes/*` for pre-checked ops tasks and misleading section titles.

## Open Questions

- Whether to add optional `(class: …)` suffix convention to OpenSpec `tasks` artifact template upstream, or keep class inference from section headings only in this bundle.
- Whether `openspec status` `all_done` should warn when ops tasks are `[x]` without evidence (future CLI; not in this change).
