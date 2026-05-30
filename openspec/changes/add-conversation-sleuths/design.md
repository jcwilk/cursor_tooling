## Context

Cursor stores agent session transcripts under a per-workspace slug in the user's local Cursor data directory. Each opened workspace path (main checkout, git worktree, sibling clone) receives its own slug and its own `agent-transcripts/` tree. Parent sessions and Task subagent sessions are stored as JSONL files (subagents under `subagents/`).

This bundle already ships Cursor skills and `AGENTS.md` guidance for OpenSpec workflow. There is no mechanism today for agents to reuse distilled knowledge from prior conversations without a human re-supplying context.

Exploration established these v1 constraints from the human:

- All sleuth artifacts (query definitions, summaries, checkpoints, config) live under a gitignored `.sleuths/` directory — fully local to the workstation.
- Task subagent transcripts are in scope.
- No staleness indicator or automatic freshness tracking in v1.
- Summaries should cite session identifiers and quote paths verbatim where possible to limit hallucination.
- Rust summarization runner built locally; binaries and build output gitignored; central script to build all bundled local tools.
- Human invokes sleuth setup and refresh in v1; no filtering of successful vs failed conversations yet.

## Goals / Non-Goals

**Goals:**

- Let a human define durable "sleuth" lenses (e.g. "all database modifications") once per project/machine.
- Incrementally summarize matching content from local Cursor agent transcripts on explicit refresh only.
- Resume from a checkpoint so new conversations append without full reprocessing.
- Give agents a stable, documented place to read summaries during unrelated future work.
- Keep setup trivial: Cursor already captures transcripts; human overhead scales with number of sleuths, not number of sessions.

**Non-Goals (v1):**

- Team-shared sleuth definitions or summaries via git.
- Automatic background refresh, hooks, or staleness signaling to agents.
- Classifying conversations as successful vs failed/aborted.
- Cloud transcript sync or multi-machine aggregation.
- Replacing OpenSpec living specs — sleuths are conversation archaeology, not behavioral contracts.

## Decisions

### 1. Storage layout — everything under `.sleuths/` (gitignored)

```
.sleuths/
  config.yaml                 # ollama url/model, optional slug overrides
  queries/
    <sleuth-id>.yaml          # lens definition (prompt, metadata)
  <sleuth-id>/
    checkpoint.yaml           # processed transcript cursors
    summary.md                # agent-readable progressive summary
```

**Rationale:** Matches "fully local" decision; one ignore rule; queries and outputs co-located per machine.

**Alternative considered:** Commit `queries/` — rejected for v1 to avoid implying shareable team lenses when summaries cannot be shared.

### 2. Transcript discovery — primary slug + git worktree expansion

1. Derive the Cursor project slug from `--project-root` using observed path normalization (`/home/user/workspace/foo_bar` → `home-user-workspace-foo-bar`; worktrees under `.cursor/worktrees/<repo>/<id>` → `home-user-cursor-worktrees-<repo>-<id>`).
2. For git repositories, run `git worktree list`, compute a slug for each listed path, and scan each corresponding `~/.cursor/projects/<slug>/agent-transcripts/`.
3. Allow manual `extra_transcript_slugs` in `.sleuths/config.yaml` for sibling clones Cursor cannot infer.

**Rationale:** OSF apply flows generate substantial history on worktree slugs; main-slug-only misses Task worker output. `git worktree list` is the most reliable aggregation hook available without a Cursor API.

**Alternative considered:** Slug-prefix glob (`home-user-cursor-worktrees-home-ai-*`) — fragile for renamed repos; kept as fallback only if git unavailable.

Non-git projects: scan only the slug derived from the current project root unless overridden in config.

### 3. Checkpoint model — `(transcript_id, relative_path, line_count)`

Each processed segment records:

- transcript UUID (directory / file stem),
- path relative to `agent-transcripts/` (`.` for parent, `subagents/<uuid>.jsonl` for Task workers),
- number of JSONL lines consumed.

On refresh, skip segments at or below checkpoint; process tail of partially consumed files and any new files. Order discovery by file mtime (oldest first) for stable append semantics.

**Rationale:** File mtime alone fails for in-progress sessions; line count enables incremental tail processing.

### 4. Map/reduce via local Ollama

- **Map:** For each new transcript chunk, extract plain text from JSONL (`text` blocks; condensed representation of tool use), send to configured Ollama model with the sleuth query prompt. Instruct: extract only, omit if not relevant, preserve paths verbatim.
- **Reduce:** Merge map outputs into existing `summary.md` via a second Ollama call (or structured append for v0 fallback). Instruct: preserve prior bullets, dedupe lightly, tag entries with `[session <uuid>]` and `[subagent <uuid>]` when applicable.

Config in `.sleuths/config.yaml`:

```yaml
ollama:
  base_url: http://127.0.0.1:11434
  model: llama3.2
transcripts:
  extra_transcript_slugs: []
```

### 5. Rust runner placement and build

```
.cursor/skills/sleuths/
  SKILL.md
  sleuth/
    Cargo.toml
    src/main.rs
  target/release/sleuth    # gitignored

.cursor/build-local-tools.sh   # builds all skill-local Rust crates
```

Skill invokes `.cursor/skills/sleuths/target/release/sleuth refresh --project-root . [--sleuth <id>|--all]`.

**Rationale:** Rust for a self-contained CLI; source committed, artifacts local; central build script scales if more tools appear.

### 6. Cursor skills (human-gated v1)

- **`/sleuths` (or `sleuths` skill):** Human describes a lens → agent writes `.sleuths/queries/<id>.yaml` → runs initial refresh.
- **`/sleuth-refresh`:** Re-run incremental refresh for one or all sleuths.

Agents read summaries opportunistically; they do not refresh unless the human asks.

### 7. AGENTS.md guidance

Short section:

- Summaries live under `.sleuths/<id>/summary.md` (gitignored, machine-local, may be stale).
- Query definitions under `.sleuths/queries/`.
- Read relevant summaries before guessing about historical decisions.
- Do not commit `.sleuths/` — may contain secrets from transcripts.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Slug derivation breaks on Cursor path rule changes | Document observed rules; allow manual slug overrides in config; log resolved slug set on each run |
| LLM summarization hallucinates | Extraction-first prompts; session UUID tags; verbatim path quoting; human reviews first refresh |
| Transcripts contain secrets | Entire `.sleuths/` gitignored; explicit AGENTS.md / skill warning |
| Moved/renamed project directory orphans old slug history | Document limitation; `extra_transcript_slugs` for manual linking |
| Sibling clones invisible to git worktree list | Manual slug overrides |
| Large projects → long refresh | Incremental checkpoints; chunk map passes; human-triggered only in v1 |
| Ollama unavailable | Runner fails with clear error; no partial checkpoint advance on failed reduce |

## Migration Plan

1. Ship skill + Rust source + build script + gitignore + AGENTS.md section via bundle.
2. Consumer runs `.cursor/build-local-tools.sh` once after install.
3. Human creates first sleuth via skill; `.sleuths/` appears locally.
4. No migration of existing data — greenfield per project.

Rollback: remove skill and AGENTS.md section; delete local `.sleuths/`; no repo state beyond gitignore entry.

## Open Questions

- Exact skill naming (`sleuths` vs `sleuth-new` + `sleuth-refresh`) — resolve at apply time.
- Default Ollama model name in example config — consumer-specific.
- Whether map pass should include tool_use payloads verbatim or one-line summaries — spike during apply on a real transcript corpus.
