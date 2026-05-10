## Context

OSF ships as prose workflow guides plus Cursor-facing skills/agents/install instructions. Narrative **`README.md`**, **`OPENSPEC_FLOW.md`**, **`AGENTS.md`**, and individual skills already describe conventions, but conformance was implicit. This change introduces behavioral specifications—the durable control plane OSF advertises—which must stay behavior-shaped rather than repeating path catalogs.

Upstream OpenSpec semantics (changes, deltas, archival) remain authoritative for generic OpenSpec mechanics; OSF specs here describe **OSF-specific commitments** atop that substrate.

## Goals / Non-Goals

**Goals:**

- Establish two bounded capabilities: OSF **reference interoperability** (`openspec-flow-reference`) and **target-repository synchronization semantics** (`openspec-flow-target-sync`).
- Preserve file-path inventories inside `design`/tasks/repo docs so `spec.md` stays behavior-first.
- Make `/validate`/`archive`-ready deltas that translate cleanly into living specs upon completion.

**Non-Goals:**

- Specifying unrelated application domains of adopting repositories.
- Specifying internals of upstream OpenSpec engine behavior beyond OSF’s layering expectations.
- Locking OSF to proprietary formats—only interoperability expectations common to OSF bundle consumers.

## Decisions

- **Capability split.** Reference identity/versioning/cohesion differs from synchronization guarantees; separate specs keep review independent and curb mixed bounded contexts.

- **Version discovery channel.** OSF continues to advertise its Semantic Version through workflow documentation front matter (**`OPENSPEC_FLOW_VERSION`**) mirrored in **`CHANGELOG.md`** for humans; synchronization specs refer generically to "consumer-maintained OSF Semantic Version markers."

- **Path inventory localization.** Operational inventory (Cursor skill folders, `.cursor/agents` Task definitions, `openspec/` trees) stays in **`openspec-flow-install`** skill prose, **`README.md`**, and **`OPENSPEC_FLOW.md`**, avoiding duplication inside normative **`spec.md`**.

## Risks / Trade-offs

- **[Risk]** Specs drift from narrative docs despite intent alignment → **Mitigation:** After archive, keep updates coupled through OSF changes; review diffs jointly when bumping **`OPENSPEC_FLOW_VERSION`**.

- **[Risk]** Over-normativity encumbers minor doc edits → **Mitigation:** Default to Lite deltas; escalate rigor via future changes when ambiguity causes rework.

## Migration Plan

Apply path:

1. Land validated change artifacts (`proposal`, `design`, delta **`spec.md`**, `tasks`).
2. On approval, run OpenSpec archival for `init-normative-openspec-flow-specs`, producing living specs under **`openspec/specs/<capability>/spec.md`**.
3. Optionally align narrative headings (no requirement rewrite) pointing readers to authoritative specs—without duplicating verbatim.

Rollback: archival can be superseded via a reversing change with `REMOVED` deltas if OSF maintainers revoke requirements.

## Open Questions

None blocking initial archive; tighten observability wording if conformance checks need automated parsers later.
