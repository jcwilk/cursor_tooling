# Changelog

All notable changes to this **OpenSpec Flow reference bundle** (docs under this repo root plus `.cursor/skills/osf-*`, `.cursor/agents/osf-*`, and related companion skills documented in `OPENSPEC_FLOW.md`) are recorded here.

The **canonical bundle version** for install/upgrade checks is **`OPENSPEC_FLOW_VERSION`** in the YAML front matter of **`OPENSPEC_FLOW.md`**. This file is a human-readable history; when you cut a release, **bump `OPENSPEC_FLOW_VERSION` and add an entry below** so consumers can compare versions.

## [1.1.0] — 2026-05-30

### Added

- **Conversation sleuths** — skill **`/sleuths`**, Rust **`sleuth`** CLI (`.cursor/skills/sleuths/`), **`.cursor/build-local-tools.sh`**, **`AGENTS.md`** guidance, gitignore for **`.sleuths/`** and build artifacts.

## [1.0.1] — 2026-05-28

### Removed

- **`spawn-subagent`** skill — Task delegation rules remain in **`osf-apply-changes`**, **`AGENTS.md`**, and **`OPENSPEC_FLOW.md`**; Cursor subagents no longer need a separate skill.

## [1.0.0] — 2026-05-10

### Added

- Initial **OpenSpec Flow** reference bundle for Cursor: `OPENSPEC_FLOW.md`, generalized **`AGENTS.md`**, skills `osf-explore`, `osf-propose`, `osf-explain`, `osf-apply-changes`, `openspec-flow-install`, Task agents `osf-apply-start`, `osf-apply-finish`, `osf-apply-abort`, plus companion `persist` as documented in `OPENSPEC_FLOW.md`.
- **`CHANGELOG.md`** to track bundle changes alongside **`OPENSPEC_FLOW_VERSION`**.
