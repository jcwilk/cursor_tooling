from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, TypeVar

from langsmith import traceable

from sleuth.chunk import IndexedChunk
from sleuth.config import ProcessingConfig
from sleuth.context_budget import (
    group_by_budget,
    group_chunks_by_budget,
    group_chunks_by_min_max_budget,
)
from sleuth.inference import (
    STAGE_CROSS_MERGE,
    STAGE_INTRA_MERGE,
    STAGE_RELEVANCE,
    STAGE_SUMMARIZE,
    InferenceClient,
    set_inference_stage,
)
from sleuth.jsonl_extract import extract_lines
from sleuth.prompts import (
    content_budget,
    merge_prompt,
    merge_prompt_overhead,
    relevance_prompt,
    relevance_prompt_overhead,
    stage_content_budget,
    summarize_prompt,
    summarize_prompt_overhead,
)
from sleuth.query import SleuthQuery
from sleuth.relevance import parse_relevant_ids
from sleuth.token import estimate_tokens

T = TypeVar("T")
R = TypeVar("R")


def run_parallel_batches(
    items: list[T],
    max_workers: int,
    fn: Callable[[int, T], R],
) -> list[R]:
    if not items:
        return []
    workers = max(1, max_workers)
    results: list[R | None] = [None] * len(items)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(fn, idx, item) for idx, item in enumerate(items)]
        for idx, future in enumerate(futures):
            results[idx] = future.result()
    return results  # type: ignore[list-item]


def stream_chunks(
    path: Path,
    start_line: int,
    end_line: int,
    chunk_lines: int,
) -> list[IndexedChunk]:
    chunks: list[IndexedChunk] = []
    line = start_line
    index = 0

    while line <= end_line:
        chunk_end = min(line + chunk_lines - 1, end_line)
        text = extract_lines(path, line, chunk_end)
        line = chunk_end + 1

        if not text.strip():
            continue

        chunks.append(IndexedChunk(index=index, text=text))
        index += 1

    return chunks


@traceable(name="sleuth filter chunks for relevance", run_type="chain")
def run_relevance_pass(
    client: InferenceClient,
    query: SleuthQuery,
    chunks: list[IndexedChunk],
    processing: ProcessingConfig,
    session_tag: str,
) -> list[IndexedChunk]:
    overhead = relevance_prompt_overhead(query, session_tag)
    min_content = processing.relevance_min_content_tokens
    max_content = min(
        processing.relevance_max_content_tokens,
        content_budget(processing, overhead),
    )
    max_items = processing.max_chunks_per_batch
    groups = group_chunks_by_min_max_budget(chunks, min_content, max_content, max_items)

    def process_group(_idx: int, group: list[IndexedChunk]) -> list[IndexedChunk]:
        group_tokens = sum(estimate_tokens(c.text) for c in group)
        if group_tokens < min_content:
            print(
                f"relevance: batch below minimum target "
                f"({group_tokens} < {min_content} est. content tokens) — segment tail",
                file=sys.stderr,
            )
        indexed = [(c.index, c.text) for c in group]
        prompt = relevance_prompt(query, indexed, session_tag)
        set_inference_stage(STAGE_RELEVANCE)
        response = client.generate(
            prompt, max_completion_tokens=processing.relevance_max_completion_tokens
        )
        max_idx = group[-1].index if group else 0
        ids = parse_relevant_ids(response, max_idx)
        return [c for c in group if c.index in ids]

    group_results = run_parallel_batches(
        groups, processing.max_parallel_inference_requests, process_group
    )
    relevant: list[IndexedChunk] = []
    for group_relevant in group_results:
        relevant.extend(group_relevant)
    return relevant


@traceable(name="sleuth summarize relevant chunks", run_type="chain")
def run_summarize_pass(
    client: InferenceClient,
    query: SleuthQuery,
    relevant: list[IndexedChunk],
    processing: ProcessingConfig,
    session_tag: str,
) -> list[str]:
    if not relevant:
        return []

    overhead = summarize_prompt_overhead(
        query, session_tag, processing.pass_summary_cap_tokens
    )
    budget = stage_content_budget(
        processing.summarize_target_content_tokens, processing, overhead
    )
    max_items = processing.max_chunks_per_batch
    groups = group_chunks_by_budget(relevant, budget, max_items)

    def process_group(_idx: int, group: list[IndexedChunk]) -> str:
        indexed = [(c.index, c.text) for c in group]
        prompt = summarize_prompt(
            query, indexed, session_tag, processing.pass_summary_cap_tokens
        )
        set_inference_stage(STAGE_SUMMARIZE)
        return client.generate(
            prompt, max_completion_tokens=processing.summary_max_completion_tokens
        )

    summaries = run_parallel_batches(
        groups, processing.max_parallel_inference_requests, process_group
    )
    return [summary for summary in summaries if summary.strip()]


def recursive_reduce(
    client: InferenceClient,
    query: SleuthQuery,
    summaries: list[str],
    processing: ProcessingConfig,
    session_tag: str,
    seed_aggregate: str | None = None,
    *,
    merge_stage: str = STAGE_INTRA_MERGE,
) -> str:
    if not summaries:
        return ""

    if (
        len(summaries) == 1
        and estimate_tokens(summaries[0]) <= processing.final_summary_target_tokens
    ):
        return summaries[0]

    target = processing.final_summary_target_tokens
    max_items = processing.merge_max_items_per_batch

    while len(summaries) > 1 or (
        len(summaries) == 1 and estimate_tokens(summaries[0]) > target
    ):
        overhead = merge_prompt_overhead(query, session_tag, target, seed_aggregate is not None)
        budget = stage_content_budget(
            processing.merge_target_content_tokens, processing, overhead
        )
        groups = group_by_budget(summaries, budget, max_items)

        def process_group(_idx: int, group: list[str]) -> str:
            prompt = merge_prompt(query, group, session_tag, target, seed_aggregate)
            set_inference_stage(merge_stage)
            return client.generate(
                prompt, max_completion_tokens=processing.summary_max_completion_tokens
            )

        merged_results = run_parallel_batches(
            groups, processing.max_parallel_inference_requests, process_group
        )
        next_round = [merged for merged in merged_results if merged.strip()]

        if not next_round:
            break
        summaries = next_round
        seed_aggregate = None

    return summaries[0] if summaries else ""


@traceable(name="sleuth merge pass summaries within segment", run_type="chain")
def intra_segment_reduce(
    client: InferenceClient,
    query: SleuthQuery,
    summaries: list[str],
    processing: ProcessingConfig,
    session_tag: str,
    seed_aggregate: str | None = None,
) -> str:
    return recursive_reduce(
        client,
        query,
        summaries,
        processing,
        session_tag,
        seed_aggregate,
        merge_stage=STAGE_INTRA_MERGE,
    )


@traceable(name="sleuth merge segment summaries into summary", run_type="chain")
def cross_segment_reduce(
    client: InferenceClient,
    query: SleuthQuery,
    summaries: list[str],
    processing: ProcessingConfig,
    session_tag: str,
    seed_aggregate: str | None = None,
) -> str:
    return recursive_reduce(
        client,
        query,
        summaries,
        processing,
        session_tag,
        seed_aggregate,
        merge_stage=STAGE_CROSS_MERGE,
    )


def summary_body(summary: str) -> str | None:
    body = "\n".join(summary.splitlines()[1:]).strip()
    return body if body else None


def merge_into_summary_header(query: SleuthQuery, body: str) -> str:
    return f"# {query.description}\n\n{body.strip()}"
