# Tasks

## 1. Explore skill

- [x] 1.1 Update `.cursor/skills/osf-explore/SKILL.md` so explore is conversation-only (no file writes, including `openspec/changes/`); remove capture table, conditional change-folder permission, and “artifact updates” as a success outcome; verify the hard rule and guardrails match the new living requirement.

## 2. Bundle narrative alignment

- [x] 2.1 Update the `/osf-explore` row in `OPENSPEC_FLOW.md` so read-only explicitly includes change artifacts and durable capture via `/osf-propose`; verify wording matches `AGENTS.md` shape-phase entry points.

## 3. Release metadata

- [x] 3.1 Bump `OPENSPEC_FLOW_VERSION` to **1.7.1** in `OPENSPEC_FLOW.md` front matter and add a `CHANGELOG.md` entry describing the explore lane guardrail (note **BREAKING** for teams that used explore to patch change artifacts); verify the version string appears exactly once in front matter.

## 4. Validation

- [x] 4.1 Run `npx @fission-ai/openspec@latest validate tighten-osf-explore-read-only --type change` and verify it passes with zero errors.

## Explicitly deferred

- Forbidden-transitions table row for explore → file writes (optional follow-up if reviewers want it in a later change).
