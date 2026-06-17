## Why

Full sleuth refresh scans every pending transcript segment across all discovered sessions and worktrees, which is slow and expensive when the operator only needs to update the summary from one agent conversation. A session-scoped refresh option lets humans target a single conversation (including its Task subagent transcripts) without reprocessing unrelated sessions.

## What Changes

- Add an optional **session identifier** to sleuth refresh so the operator can limit processing to one agent session.
- When session scope is set, only transcript segments belonging to that session are eligible; all other sessions are ignored for that run.
- Session-scoped refresh still merges new material into the existing sleuth summary at batch finalization using the same collect → finalize pipeline and checkpoint semantics for the segments it touches.
- Document the new option in sleuth skill and agent guidance.

## Capabilities

### New Capabilities

_(none — extends conversation-sleuths)_

### Modified Capabilities

- `conversation-sleuths`: refresh accepts optional session scope; scoped runs process only matching session material and update summary/checkpoint for those segments only.

## Impact

- Sleuth CLI (`refresh` command) and refresh orchestration (segment filtering before pending-work resolution).
- `.cursor/skills/sleuths/SKILL.md` and `AGENTS.md` conversation-sleuths section.
- No checkpoint schema change; no change to reset behavior or query definitions.
