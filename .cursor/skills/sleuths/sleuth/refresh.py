from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from sleuth.checkpoint import Checkpoint, SegmentKey, checkpoint_path
from sleuth.config import SleuthsConfig, load_config, sleuths_dir
from sleuth.discover import TranscriptSegment, discover_segments, resolve_slugs
from sleuth.graph import run_segment_pipeline
from sleuth.inference import InferenceClient, inference_call_count, reset_inference_call_count
from sleuth.jsonl_extract import count_lines
from sleuth.pipeline import merge_into_summary_header, recursive_reduce, summary_body
from sleuth.query import SleuthQuery, list_sleuth_ids, load_query
from sleuth.tracing import configure_langsmith, warn_tracing_failure


def refresh_sleuth(project_root: Path, sleuth_id: str) -> None:
    configure_langsmith(project_root)
    config = load_config(project_root)
    _refresh_sleuth_with_config(project_root, sleuth_id, config)


def refresh_all(project_root: Path) -> None:
    configure_langsmith(project_root)
    config = load_config(project_root)
    ids = list_sleuth_ids(project_root)
    if not ids:
        raise RuntimeError("no sleuths found under .sleuths/queries/")
    for sleuth_id in ids:
        _refresh_sleuth_with_config(project_root, sleuth_id, config)


def _refresh_sleuth_with_config(
    project_root: Path,
    sleuth_id: str,
    config: SleuthsConfig,
) -> None:
    query = load_query(project_root, sleuth_id)
    slugs = resolve_slugs(project_root, config)
    segments = discover_segments(slugs)

    sleuth_dir = sleuths_dir(project_root) / sleuth_id
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

    pending = [
        work
        for seg in segments
        if (work := _pending_work(seg, processed)) is not None
    ]

    if not pending:
        print(f"Sleuth '{sleuth_id}': nothing new to process", file=sys.stderr)
        return

    print(
        f"Sleuth '{sleuth_id}': processing {len(pending)} segment(s)",
        file=sys.stderr,
    )

    reset_inference_call_count()
    new_segment_summaries: list[str] = []

    for work in pending:
        session_tag = _session_tag(work.segment)
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
            new_segment_summaries.append(segment_summary)

        body = _merge_new_summaries(
            client,
            query,
            processing,
            session_tag,
            prior_body,
            new_segment_summaries,
        )
        summary = merge_into_summary_header(query, body)

        checkpoint.upsert_segment(
            SegmentKey(
                transcript_id=work.segment.transcript_id,
                relative_path=work.segment.relative_path,
            ),
            work.end_line,
        )
        checkpoint.save(ckpt_path)
        summary_path.write_text(summary, encoding="utf-8")

    print(
        f"Sleuth '{sleuth_id}': inference calls this refresh: {inference_call_count()}",
        file=sys.stderr,
    )


def _merge_new_summaries(
    client: InferenceClient,
    query: SleuthQuery,
    processing,
    session_tag: str,
    prior_body: str | None,
    new_summaries: list[str],
) -> str:
    if not new_summaries:
        return prior_body or ""

    if prior_body and prior_body.strip():
        inputs = [prior_body, *new_summaries]
        return recursive_reduce(
            client, query, inputs, processing, session_tag, prior_body
        )

    return recursive_reduce(
        client, query, list(new_summaries), processing, session_tag, None
    )


@dataclass
class PendingWork:
    segment: TranscriptSegment
    start_line: int
    end_line: int


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
