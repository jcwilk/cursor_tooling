## Context

Sleuth refresh discovers all transcript segments under resolved workspace slugs, builds a pending list from checkpoint tails, processes each segment through the LangGraph pipeline, and finalizes into `summary.md`. The CLI today accepts only `--sleuth <id>` or `--all`. There is no way to refresh one Cursor agent session (UUID) without processing every other pending session.

A **session** is identified by `transcript_id` in discovery — the first path component under `agent-transcripts/` (parent `*.jsonl` and `subagents/*.jsonl` share the same id). Checkpoint keys are per `(transcript_id, relative_path)`.

## Goals / Non-Goals

**Goals:**

- `sleuth refresh --sleuth <id> --session <transcript_id>` processes only segments whose session identifier matches.
- Include parent and Task subagent transcript files for that session (existing subagent inclusion rule).
- Use the same collect → finalize pipeline; merge scoped segment summaries into the existing summary body at batch end.
- Advance checkpoint only for segments processed in the scoped run; leave other sessions' checkpoint entries untouched.
- Clear stderr when no matching or pending material exists.

**Non-Goals:**

- Session-scoped **reset** (defer; operator can manually edit checkpoint or full reset).
- Force reprocess of already-checkpointed session content without clearing checkpoint (defer `--reprocess`).
- Multiple `--session` values in one command (v1: one session per run).
- Changing transcript discovery slug rules or query schema.

## Decisions

### 1. CLI surface

**Decision:** Add optional `--session <transcript_id>` to `refresh`, requires `--sleuth` (not valid with `--all`).

```bash
sleuth --project-root . refresh --sleuth tooling --session 9d6af3ac-5907-4374-9833-36a850943515
```

**Alternatives considered:**

- *Config file session list* — rejected; too indirect for ad hoc operator use.
- *Environment variable* — rejected; not discoverable.

### 2. Segment filter placement

**Decision:** Filter `discover_segments` results in `refresh.py` after discovery, before `_pending_work`:

```python
if session_id:
    segments = [s for s in segments if s.transcript_id == session_id]
```

If the filtered list is empty, fail with explicit error: no transcript segments found for that session id.

### 3. Summary and checkpoint interaction

**Decision:** Session-scoped refresh is a **partial batch** of the normal refresh:

- `prior_body` = existing summary (unchanged).
- Collect phase runs only on pending segments in the scoped session.
- Finalize merges `prior_body` + new segment summaries once.
- Checkpoint updates only for segments advanced during this run.

Other sessions' checkpoint rows and summary content from prior runs remain valid; new material appends/merges at finalize.

**Re-processing a fully checkpointed session:** Out of scope for v1. Operator clears that session's rows from `checkpoint.yaml` or uses full reset if they need a rebuild.

### 4. Validation

**Decision:**

- `--session` without `--sleuth` → CLI error.
- `--session` with `--all` → CLI error.
- Unknown session id (no segments after filter) → error before inference.
- Session exists but nothing pending → stderr message and exit 0 (same as global "nothing new").

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Operator typos session UUID | Explicit error when no segments match |
| Summary merge without reprocessing other sessions may leave stale cross-session ordering | Acceptable; summary is progressive not chronological |
| Partial finalize still runs cross-segment merge for multi-file sessions (parent + subagents) | Correct; one session can have multiple segments |

## Migration Plan

1. Ship via CLI update; no schema migration.
2. Existing checkpoints and summaries compatible.
3. Document session id discovery (folder name under agent-transcripts).

## Open Questions

- `--reprocess` flag to ignore checkpoint for scoped session — defer to follow-up if needed.
