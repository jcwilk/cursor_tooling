## Why

Cursor already stores agent conversation history locally, but agents working in a project have no durable, queryable memory of prior sessions unless a human manually re-explains context. Progressive summarization over that history — driven by human-defined lenses and refreshed only on demand — gives agents cheap access to past decisions and work without adding per-conversation human overhead.

## What Changes

- Add a **conversation sleuths** capability: human-defined live queries that lazily map/reduce local agent transcripts into incremental summaries.
- Add a Cursor skill for establishing sleuths and triggering refresh (human-invoked in v1).
- Add a local summarization runner (Rust) that calls a configurable Ollama endpoint.
- Store all sleuth state (query definitions, checkpoints, summaries, local config) under a gitignored project-local directory.
- Extend bundle install surfaces (`AGENTS.md`, gitignore patterns, optional central local-tools build script) so agents know where summaries live and how to refresh them.
- Include Task subagent transcripts when scanning conversation history.

## Capabilities

### New Capabilities

- `conversation-sleuths`: Human-defined lenses over local Cursor agent transcripts; incremental summarization, lazy refresh, and agent-readable summary artifacts scoped to the workstation.

### Modified Capabilities

- (none)

## Impact

- **Cursor bundle**: new skill, local Rust tool source, AGENTS.md section, gitignore entries, install inventory updates.
- **Consumer projects**: optional `.sleuths/` directory (gitignored, machine-local); one-time local build of bundled tools.
- **External dependency**: Ollama (or compatible HTTP endpoint) for summarization — configured locally, not shipped.
- **Privacy**: summaries derive from transcripts that may contain secrets; must remain gitignored.
