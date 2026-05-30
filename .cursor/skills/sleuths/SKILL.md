---
name: sleuths
description: Establish and refresh human-defined lenses over local Cursor agent transcripts. Writes query defs under .sleuths/queries/, runs incremental map/reduce via a configured Ollama-compatible endpoint, and produces agent-readable summaries. Use when the user says /sleuths, wants conversation archaeology, or asks to refresh sleuth summaries.
---

# `/sleuths` — conversation lenses over agent history

**Goal:** Let a human define durable **sleuth** lenses (e.g. “all database modifications”) that lazily summarize local Cursor agent transcripts into `.sleuths/<id>/summary.md`. Agents **read** summaries; humans **refresh** them in v1.

## Privacy

> Sleuth summaries are derived from local agent transcripts and may contain secrets. **`.sleuths/` is gitignored — do not commit it.**

## One-time setup (per machine)

Build the bundled Rust CLI once:

```bash
.cursor/build-local-tools.sh
```

Binary path (gitignored):

```text
.cursor/skills/sleuths/target/release/sleuth
```

Configure summarization in `.sleuths/config.yaml` (**you must create this file before any refresh** — it is not auto-generated, not committed, and sleuth **never** installs or starts Ollama on this machine):

```yaml
ollama:
  base_url: http://<inference-host>:<port>   # required — Ollama-compatible HTTP API you operate
  model: <model-tag>                         # required — model tag on that endpoint
transcripts:
  extra_transcript_slugs: []   # sibling clones, etc.
```

Point `base_url` and `model` at **your** inference server (typically remote). Refresh only sends HTTP requests to that URL; it does not spawn a local daemon or pull models here.

## Establish a new sleuth

When the human describes what to track:

1. Choose a short **sleuth id** (kebab-case), e.g. `database-modifications`.
2. Write `.sleuths/queries/<id>.yaml`:

```yaml
id: database-modifications
description: Database schema and migration work discussed in agent sessions
prompt: |
  Extract every database modification mentioned or performed: migrations,
  schema changes, table/column adds, raw SQL. Quote file paths verbatim.
  If nothing relevant in the chunk, respond with NO_MATCH.
```

3. Run initial refresh:

```bash
.cursor/skills/sleuths/target/release/sleuth refresh \
  --project-root . \
  --sleuth database-modifications
```

4. Show the human `.sleuths/<id>/summary.md` and confirm it looks reasonable.

## Refresh (incremental)

Re-run when new agent sessions have accumulated (human-invoked only in v1):

```bash
# one sleuth
.cursor/skills/sleuths/target/release/sleuth refresh --project-root . --sleuth <id>

# all sleuths under .sleuths/queries/
.cursor/skills/sleuths/target/release/sleuth refresh --project-root . --all
```

Refresh scans local transcripts (primary workspace slug + `git worktree list` + `extra_transcript_slugs`), processes only segments after the checkpoint, and calls the configured Ollama-compatible endpoint for map/reduce. **If the endpoint is unreachable, refresh fails and checkpoints do not advance.**

## Where artifacts live

| Path | Purpose |
|------|---------|
| `.sleuths/config.yaml` | Inference endpoint URL/model, extra transcript slugs |
| `.sleuths/queries/<id>.yaml` | Lens definition (prompt) |
| `.sleuths/<id>/checkpoint.yaml` | Processed transcript cursors |
| `.sleuths/<id>/summary.md` | Agent-readable progressive summary |

Transcripts are read from `~/.cursor/projects/<slug>/agent-transcripts/` (parent JSONL + `subagents/*.jsonl`).

## Agent behavior

- **Read** relevant `.sleuths/*/summary.md` when historical context may help; summaries may be stale (no auto-refresh in v1).
- **Do not** refresh sleuths unless the human asks.
- **Do not** commit `.sleuths/`.

## Reference

- **`AGENTS.md`** — conversation sleuths section for all agents.
- Living spec (after archive): **`openspec/specs/conversation-sleuths/spec.md`**.
