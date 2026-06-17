from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from langsmith import traceable

from sleuth.checkpoint import Checkpoint, SegmentKey, checkpoint_path
from sleuth.config import SleuthsConfig, load_config, sleuths_dir
from sleuth.discover import TranscriptSegment, discover_segments, resolve_slugs
from sleuth.graph import run_segment_pipeline
from sleuth.inference import (
    InferenceClient,
    inference_call_count,
    inference_stage_counts,
    reset_inference_call_count,
)
from sleuth.jsonl_extract import count_lines
from sleuth.pipeline import (
    cross_segment_reduce,
    merge_into_summary_header,
    summary_body,
)
from sleuth.query import SleuthQuery, list_sleuth_ids, load_query
from sleuth.tracing import configure_langsmith, warn_tracing_failure


def refresh_sleuth(
    project_root: Path,
    sleuth_id: str,
    *,
    session_id: str | None = None,
    dry_run: bool = False,
) -> None:
    configure_langsmith(project_root)
    config = load_config(project_root)
    _refresh_sleuth_with_config(
        project_root,
        sleuth_id,
        config,
        session_id=session_id,
        dry_run=dry_run,
    )


def refresh_all(project_root: Path) -> None:
    configure_langsmith(project_root)
    config = load_config(project_root)
    ids = list_sleuth_ids(project_root)
    if not ids:
        raise RuntimeError("no sleuths found under .sleuths/queries/")
    for sleuth_id in ids:
        _refresh_sleuth_with_config(project_root, sleuth_id, config)


@traceable(name="sleuth refresh operation", run_type="chain")
def _refresh_sleuth_with_config(
    project_root: Path,
    sleuth_id: str,
    config: SleuthsConfig,
    *,
    session_id: str | None = None,
    dry_run: bool = False,
) -> None:
    query = load_query(project_root, sleuth_id)
    slugs = resolve_slugs(project_root, config)
    segments = discover_segments(slugs)

    if session_id is not None:
        segments = [seg for seg in segments if seg.transcript_id == session_id]
        if not segments:
            raise RuntimeError(
                f"no transcript segments found for session '{session_id}'"
            )

    sleuth_dir = sleuths_dir(project_root) / sleuth_id
    if not dry_run:
        sleuth_dir.mkdir(parents=True, exist_ok=True)

    ckpt_path = checkpoint_path(sleuth_dir)
    checkpoint = Checkpoint.load(ckpt_path)
    processed = checkpoint.line_count_map()

    summary_path = sleuth_dir / "summary.md"
    if summary_path.exists():
        summary = summary_path.read_text(encoding="utf-8")
    else:
        summary = merge_into_summary_header(query, "")

    client = InferenceClient(config.ollama)
    processing = config.processing
    prior_body = summary_body(summary)

    pending: list[PendingWork] = []
    for seg in segments:
        if session_id is not None:
            work = _session_reprocess_work(seg)
        else:
            work = _pending_work(seg, processed)
        if work is not None:
            pending.append(work)

    if not pending:
        print(f"Sleuth '{sleuth_id}': nothing new to process", file=sys.stderr)
        return

    print(
        f"Sleuth '{sleuth_id}': processing {len(pending)} segment(s)",
        file=sys.stderr,
    )

    reset_inference_call_count()
    batch_segment_summaries: list[str] = []
    last_session_tag = "[refresh batch]"

    for work in pending:
        session_tag = _session_tag(work.segment)
        last_session_tag = session_tag
        try:
            segment_summary = run_segment_pipeline(
                client,
                query,
                work.segment.absolute_path,
                work.start_line,
                work.end_line,
                processing,
                session_tag,
            )
        except Exception as exc:
            if _is_tracing_error(exc):
                warn_tracing_failure(exc)
                raise
            raise

        if segment_summary.strip():
            batch_segment_summaries.append(segment_summary)

        if not dry_run:
            checkpoint.upsert_segment(
                SegmentKey(
                    transcript_id=work.segment.transcript_id,
                    relative_path=work.segment.relative_path,
                ),
                work.end_line,
            )
            checkpoint.save(ckpt_path)

    if batch_segment_summaries:
        body = _finalize_batch_summary(
            client,
            query,
            processing,
            last_session_tag,
            prior_body,
            batch_segment_summaries,
        )
        summary = merge_into_summary_header(query, body)
        if dry_run:
            sys.stdout.write(summary)
            if not summary.endswith("\n"):
                sys.stdout.write("\n")
        else:
            summary_path.write_text(summary, encoding="utf-8")

    _print_inference_summary(sleuth_id)


def _finalize_batch_summary(
    client: InferenceClient,
    query: SleuthQuery,
    processing,
    session_tag: str,
    prior_body: str | None,
    batch_segment_summaries: list[str],
) -> str:
    if prior_body and prior_body.strip():
        return cross_segment_reduce(
            client,
            query,
            batch_segment_summaries,
            processing,
            session_tag,
            prior_body,
        )
    return cross_segment_reduce(
        client,
        query,
        batch_segment_summaries,
        processing,
        session_tag,
        None,
    )


def _print_inference_summary(sleuth_id: str) -> None:
    counts = inference_stage_counts()
    print(
        f"Sleuth '{sleuth_id}': inference calls this refresh: {inference_call_count()} "
        f"(relevance={counts['relevance']}, summarize={counts['summarize']}, "
        f"intra_merge={counts['intra_merge']}, cross_merge={counts['cross_merge']})",
        file=sys.stderr,
    )


@dataclass
class PendingWork:
    segment: TranscriptSegment
    start_line: int
    end_line: int


def _session_reprocess_work(seg: TranscriptSegment) -> PendingWork | None:
    try:
        total = count_lines(seg.absolute_path)
    except OSError:
        return None
    if total == 0:
        return None

    return PendingWork(
        segment=seg,
        start_line=1,
        end_line=total,
    )


def _pending_work(
    seg: TranscriptSegment,
    processed: dict[SegmentKey, int],
) -> PendingWork | None:
    try:
        total = count_lines(seg.absolute_path)
    except OSError:
        return None
    if total == 0:
        return None

    key = SegmentKey(
        transcript_id=seg.transcript_id,
        relative_path=seg.relative_path,
    )
    done = processed.get(key, 0)
    if done >= total:
        return None

    return PendingWork(
        segment=seg,
        start_line=done + 1,
        end_line=total,
    )


def _session_tag(seg: TranscriptSegment) -> str:
    if seg.relative_path.startswith("subagents/"):
        sub_id = seg.relative_path.removeprefix("subagents/").removesuffix(".jsonl")
        return f"[session {seg.transcript_id}] [subagent {sub_id}]"
    return f"[session {seg.transcript_id}]"


def _is_tracing_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return "langsmith" in msg or "tracing" in msg
