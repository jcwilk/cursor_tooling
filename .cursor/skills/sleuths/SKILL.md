---
name: sleuths
description: Establish and refresh human-defined lenses over local Cursor agent transcripts. Writes query defs under .sleuths/queries/, runs incremental relevance filter → batched summarize → recursive reduce via a configured inference endpoint (Ollama or llama.cpp OpenAI chat), and produces agent-readable summaries. Use when the user says /sleuths, wants conversation archaeology, or asks to refresh sleuth summaries.
---

# `/sleuths` — conversation lenses over agent history

**Goal:** Let a human define durable **sleuth** lenses (e.g. “all database modifications”) that lazily summarize local Cursor agent transcripts into `.sleuths/<id>/summary.md`. Agents **read** summaries; humans **refresh** them in v1.

## Privacy

> Sleuth summaries are derived from local agent transcripts and may contain secrets. **`.sleuths/` is gitignored — do not commit it.**

## One-time setup (per machine)

Build the bundled Rust CLI once:

```bash
scripts/build-local-tools.sh
```

Binary path (gitignored):

```text
.cursor/skills/sleuths/target/release/sleuth
```

Configure summarization in `.sleuths/config.yaml` (**you must create this file before any refresh** — it is not auto-generated, not committed, and sleuth **never** installs or starts a local inference daemon):

```yaml
ollama:
  base_url: http://<inference-host>:<port>   # required
  model: <model-tag>                         # required
  api: ollama                                # optional — default; see below
transcripts:
  extra_transcript_slugs: []   # sibling clones, etc.
processing:                    # optional — defaults shown
  context_budget_tokens: 16384
  response_headroom_tokens: 1000
  pass_summary_cap_tokens: 4000
  final_summary_target_tokens: 4000
  chunk_lines: 1               # lines merged per indexed chunk (default 1)
  max_chunks_per_batch: 20     # max chunks per relevance/summarize/merge group
```

**`api`** selects the HTTP protocol (defaults to `ollama` when omitted):

| `api` value | Server | Endpoint used |
|-------------|--------|---------------|
| `ollama` (default) | Ollama, or Ollama-compatible proxies | `POST {base_url}/api/generate` |
| `openai-chat`, `llama-cpp`, or `llama.cpp` | llama.cpp server, inference gateways | `POST {base_url}/v1/chat/completions` |

**Ollama example:**

```yaml
ollama:
  base_url: http://127.0.0.1:11434
  model: llama3.2
```

**llama.cpp / OpenAI-chat example** (e.g. inference gateway text listener):

```yaml
ollama:
  base_url: http://192.168.1.110:11435
  model: fast-text-qwen3-8b
  api: llama-cpp
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
  Irrelevant material is filtered automatically during refresh; focus the lens on what to keep.
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

Refresh scans local transcripts (primary workspace slug + `git worktree list` + `extra_transcript_slugs`), processes only segments after the checkpoint, and calls the configured inference endpoint. **If the endpoint is unreachable, refresh fails and checkpoints do not advance.**

### Refresh pipeline (per segment)

1. **Chunk** — stream small indexed chunks from the checkpoint tail (default: one transcript line per chunk).
2. **Relevance** — batch chunks (token budget + max ~20 per batch); model returns JSON `relevant_ids`; non-selected chunks are dropped.
3. **Summarize** — batch filtered chunks; one pass summary per group.
4. **Reduce** — recursively merge pass summaries until one bounded result remains (skipped when only one pass summary).

On incremental refresh, an existing `summary.md` is used as a **merge seed** only in the final recursive reduce across new segment output — not during per-chunk steps.

## Reset (full rebuild)

To regenerate a summary from scratch (e.g. after changing the inference model), reset clears the checkpoint and summary without touching the query definition:

```bash
# one sleuth
.cursor/skills/sleuths/target/release/sleuth reset --project-root . --sleuth <id>

# all sleuths
.cursor/skills/sleuths/target/release/sleuth reset --project-root . --all
```

Then run `refresh` as usual. Reset does not call the inference endpoint.

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
