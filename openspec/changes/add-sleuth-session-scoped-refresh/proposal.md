## Why

Full sleuth refresh scans every pending transcript segment across all discovered sessions and worktrees, which is slow and expensive when the operator only needs to update the summary from one agent conversation. Operators also need a safe way to iterate on refresh tuning (batch sizes, models, lens prompts) against a single session without rewriting checkpoints or summary artifacts on disk.

## What Changes

- Add an optional **session identifier** to sleuth refresh so the operator can limit processing to one agent session (parent + Task subagent transcripts).
- **Session-scoped refresh always reprocesses** all transcript material from that session, even when a checkpoint already records it as fully processed — no separate reprocess flag.
- Add **`--dry-run`** on refresh only: run the full collect → finalize orchestration, emit the resulting summary to stdout, and **persist nothing** to checkpoint or summary artifacts regardless of other options.
- Document session scope, implicit reprocess, and dry-run in sleuth skill and agent guidance.

## Capabilities

### New Capabilities

_(none — extends conversation-sleuths)_

### Modified Capabilities

- `conversation-sleuths`: session-scoped refresh with automatic full reprocess for the targeted session; refresh dry-run mode that emits summary output without persisting local sleuth state.

## Impact

- Sleuth CLI (`refresh` command) and refresh orchestration (segment filtering, checkpoint bypass for scoped session, dry-run persistence guard).
- `.cursor/skills/sleuths/SKILL.md` and `AGENTS.md` conversation-sleuths section.
- No checkpoint schema change; no change to reset behavior or query definitions.
