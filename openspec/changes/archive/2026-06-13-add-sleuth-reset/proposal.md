## Why

Sleuth refresh is incremental: it only processes transcript segments after the checkpoint. When a human changes the inference model, revises a lens prompt, or wants to discard a bad summary, there is no supported way to force a full rebuild without manually deleting local artifacts. That gap makes model and prompt experiments awkward and error-prone.

## What Changes

- Add a human-invoked **reset** operation that clears a sleuth's summary and checkpoint while preserving the lens definition.
- Extend the bundled sleuth CLI with a `reset` subcommand (single sleuth or all).
- Document reset in the sleuths skill as the supported path before a full refresh.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `conversation-sleuths`: add requirement for human-initiated reset that discards summary/checkpoint state without deleting the lens, enabling full reprocessing on the next refresh.

## Impact

- **Rust CLI** (`.cursor/skills/sleuths/sleuth/`): new reset handler; no inference calls during reset.
- **Cursor skill** (`.cursor/skills/sleuths/SKILL.md`): document reset + refresh workflow.
- **Living spec** (`conversation-sleuths`): one new requirement on archive.
- **No breaking changes** to refresh, config, or query formats.
