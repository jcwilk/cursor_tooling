# Design

## Context

See `proposal.md` — Why. The explore skill previously mixed read-only thinking with optional change-folder capture; agents treated alignment work as in-lane. Proposal shaping already has a normative writable-scope rule; explore did not.

## Goals / Non-Goals

**Goals:**

- One unambiguous explore lane: read and discuss; all writes go through `/osf-propose` or later apply/finish paths.
- Skill text that cannot be overridden by downstream “capture” tables or success outcomes.
- Living spec language that matches `AGENTS.md` and survives archive as behavioral truth.

**Non-Goals:**

- Changing `/osf-propose` lane lock or apply orchestration.
- Forbidding humans from editing change files manually.
- Adding explore-specific CLI commands or OpenSpec schema changes.

## Decisions

1. **Conversation-only explore (no file writes at all)**  
   - *Rationale:* “No implementation” was interpreted as application code only; explicit-ask capture still caused proposal edits during explore.  
   - *Alternative:* Keep explicit-ask exception — rejected; investigation showed it loses to capture guidance later in the skill.

2. **ADDED living requirement rather than MODIFIED proposal-shaping rule**  
   - *Rationale:* Proposal shaping’s writable scope applies when the worker is in the propose lane; explore is a separate entry point with zero writes.  
   - *Alternative:* Extend the existing proposal-shaping requirement — rejected; conflates two lanes.

3. **Bundle release as patch/minor with changelog**  
   - *Rationale:* Consumers compare `OPENSPEC_FLOW_VERSION`; skill-only delivery without bump is invisible on upgrade.  
   - *Version:* **1.7.1** (behavioral guardrail fix within explore lane; note breaking explore capture habit in changelog).

4. **`OPENSPEC_FLOW.md` table tweak only**  
   - *Rationale:* Clarify read-only includes change artifacts; avoid duplicating full lane matrix unless a single forbidden row for explore → writes is enough.

## Risks / Trade-offs

- **[Risk] Teams used explore + explicit capture as a shortcut** → Mitigation: changelog “Notes for consumers”; explore offers `/osf-propose` handoff with proposed wording in chat.
- **[Risk] Skill says “only propose writes artifacts” while apply updates `tasks.md`** → Mitigation: skill reference already points at propose for capture; apply checkbox updates remain apply-lane (unchanged).

## Migration Plan

1. Land skill + docs + version via apply on working branch.  
2. Consumers run `/openspec-flow-install` or rsync `osf-explore` when version ≥ 1.7.1.  
3. No rollback of living specs without a follow-on OSF change; skill revert alone would drift from spec post-archive.
