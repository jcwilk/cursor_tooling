## Context

Sleuth refresh discovers all transcript segments under resolved workspace slugs, builds a pending list from checkpoint tails, processes each segment through the LangGraph pipeline, and finalizes into `summary.md`. The CLI today accepts only `--sleuth <id>` or `--all`.

A **session** is identified by `transcript_id` in discovery — the first path component under `agent-transcripts/` (parent `*.jsonl` and `subagents/*.jsonl` share the same id). Checkpoint keys are per `(transcript_id, relative_path)`.

## Goals / Non-Goals

**Goals:**

- `sleuth refresh --sleuth <id> --session <transcript_id>` processes only that session and **reprocesses from line 1** for every segment in that session, ignoring prior checkpoint progress for those segments.
- `sleuth refresh --sleuth <id> --dry-run` (optionally with `--session`) runs collect → finalize, prints the resulting summary document to stdout, and writes **no** checkpoint or summary files.
- Dry-run on refresh suppresses all sleuth artifact persistence even when combined with `--session` or other refresh options.
- Include parent and Task subagent transcript files for the scoped session.
- Non-dry session-scoped refresh merges into existing summary at finalize and updates checkpoint only for reprocessed session segments; other sessions' checkpoint rows untouched.

**Non-Goals:**

- `--dry-run` on `reset` or other subcommands.
- Separate `--reprocess` flag (session scope implies reprocess).
- Multiple `--session` values in one command (v1: one session per run).
- Session-scoped **reset** subcommand.
- Changing transcript discovery slug rules or query schema.

## Decisions

### 1. CLI surface

**Decision:**

```bash
# Reprocess one session and persist
sleuth --project-root . refresh --sleuth tooling --session <transcript_id>

# Iterate on orchestration without touching disk
sleuth --project-root . refresh --sleuth tooling --session <transcript_id> --dry-run

# Dry-run full pending batch (no session filter)
sleuth --project-root . refresh --sleuth tooling --dry-run
```

- `--session` requires `--sleuth`; incompatible with `--all`.
- `--dry-run` only on `refresh`.

### 2. Session scope implies reprocess

**Decision:** When session scope is set, `_pending_work` treats every segment in that session as pending from **line 1**, regardless of checkpoint `line_count`. Checkpoint rows for other sessions are read but not modified until finalize (non-dry-run only).

**Rationale:** Session-scoped refresh is explicitly for “redo this conversation” — incremental tail-only behavior would make `--session` a no-op on already-processed sessions.

**Alternatives considered:**

- *Separate `--reprocess` flag* — rejected; user wants session scope to always reprocess.
- *Incremental session scope* — rejected; contradicts intended use.

### 3. Dry-run persistence guard

**Decision:** Thread a `dry_run: bool` through refresh orchestration. When true:

- Skip `checkpoint.save()` and `summary_path.write_text()` entirely.
- After successful finalize, print the full summary document (header + body) to **stdout**.
- Progress/diagnostics remain on **stderr** (segment count, inference call counts).
- Inference still runs against the configured endpoint (dry-run is not a mock).

**Alternatives considered:**

- *Write to a temp file* — rejected; stdout is the contract for piping/inspection.

### 4. Session-scoped finalize semantics (non-dry-run)

**Decision:** Session-scoped refresh is a partial batch:

- `prior_body` = existing summary body (material from other sessions preserved).
- Collect reprocesses all lines from scoped session segments.
- Finalize merges `prior_body` + new segment summaries once.
- Checkpoint upserts full line counts for reprocessed session segments only.

### 5. Validation

- `--session` without `--sleuth` → CLI error.
- `--session` with `--all` → CLI error.
- Unknown session id → error before inference.
- Session exists with dry-run → always runs (reprocess); never “nothing new”.
- Global refresh (no session) unchanged: incremental from checkpoint; dry-run still skips persistence.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Session reprocess duplicates facts in summary if prior session content not stripped | Merge step deduplicates; operator may full-reset sleuth if summary becomes noisy |
| Dry-run still costs inference | Document clearly; intended for tuning |
| Operator typos session UUID | Explicit error when no segments match |

## Migration Plan

1. Ship via CLI update; backward compatible (new flags optional).
2. Existing checkpoints and summaries compatible.
3. Document session id discovery (folder name under agent-transcripts).

## Open Questions

_(none — session reprocess and dry-run scoped per user request)_
