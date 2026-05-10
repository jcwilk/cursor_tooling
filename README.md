# OpenSpec Flow — Cursor reference bundle

This repository is a **small, portable reference** for running [OpenSpec](https://github.com/Fission-AI/OpenSpec) with **Cursor** skills and **Task** subagents: propose → apply on isolated branches → finish (archive + merge) or abort.

## Contents

| Path | Role |
|------|------|
| **`OPENSPEC_FLOW.md`** | Workflow overview and **`OPENSPEC_FLOW_VERSION`** (bundle version). |
| **`CHANGELOG.md`** | Human-readable history of bundle releases (keep aligned with **`OPENSPEC_FLOW_VERSION`**). |
| **`AGENTS.md`** | Agent rules: `openspec/` discipline, Task-only apply agents, git posture. |
| **`.cursor/skills/osf-*/`** | Slash-driven skills (`/osf-propose`, `/osf-explore`, …). |
| **`.cursor/agents/osf-*.md`** | Task definitions for apply/finish/abort. |
| **`.cursor/skills/persist/`** | Commit/push hygiene used by propose/finish flows. |
| **`.cursor/skills/spawn-subagent/`** | Required for real Task delegation. |
| **`.cursor/skills/openspec-flow-install/`** | **Install or upgrade** this bundle into another repo (compare versions, copy files). |

Your **application** code and **`openspec/`** tree live in whatever project you attach this bundle to; initialize OpenSpec in that project with the upstream CLI when you are ready.

## Prerequisites

- Node.js **20.19+** (for `npx @fission-ai/openspec@latest …`).
- Cursor with **Task** subagents enabled.

## Quick start (in a consumer project)

1. Follow **`/openspec-flow-install`** (skill **`openspec-flow-install`**) to copy or refresh files from this reference into your project’s tree.
2. Ensure **`OPENSPEC_FLOW.md`** at the project root records the **`OPENSPEC_FLOW_VERSION`** you installed (the install skill explains how to compare and detect drift).
3. Use **`/osf-explore`** and **`/osf-propose`** with your project’s **`openspec/`** layout.

## Versioning

The integration is versioned as a **single bundle** via **`OPENSPEC_FLOW_VERSION`** in the YAML front matter of **`OPENSPEC_FLOW.md`**. Bump that field when you change any shipped skill, agent, or the normative workflow text so consumers can detect upgrades.

**`CHANGELOG.md`** records notable bundle changes in prose; for automation and drift checks, compare **`OPENSPEC_FLOW_VERSION`** (and keep the changelog entry aligned when you release).
