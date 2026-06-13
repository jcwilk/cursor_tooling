from __future__ import annotations

from pathlib import Path

from sleuth.chunk import IndexedChunk
from sleuth.config import ProcessingConfig
from sleuth.context_budget import group_by_budget, group_chunks_by_budget
from sleuth.inference import InferenceClient
from sleuth.jsonl_extract import extract_lines
from sleuth.prompts import (
    content_budget,
    merge_prompt,
    merge_prompt_overhead,
    relevance_prompt,
    relevance_prompt_overhead,
    summarize_prompt,
    summarize_prompt_overhead,
)
from sleuth.query import SleuthQuery
from sleuth.relevance import parse_relevant_ids
from sleuth.token import estimate_tokens


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


def run_relevance_pass(
    client: InferenceClient,
    query: SleuthQuery,
    chunks: list[IndexedChunk],
    processing: ProcessingConfig,
    session_tag: str,
) -> list[IndexedChunk]:
    overhead = relevance_prompt_overhead(query, session_tag)
    budget = content_budget(processing, overhead)
    max_items = processing.max_chunks_per_batch
    groups = group_chunks_by_budget(chunks, budget, max_items)

    relevant: list[IndexedChunk] = []
    for group in groups:
        indexed = [(c.index, c.text) for c in group]
        prompt = relevance_prompt(query, indexed, session_tag)
        response = client.generate(prompt)
        max_idx = group[-1].index if group else 0
        ids = parse_relevant_ids(response, max_idx)
        for c in group:
            if c.index in ids:
                relevant.append(c)
    return relevant


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
    budget = content_budget(processing, overhead)
    max_items = processing.max_chunks_per_batch
    groups = group_chunks_by_budget(relevant, budget, max_items)

    pass_summaries: list[str] = []
    for group in groups:
        indexed = [(c.index, c.text) for c in group]
        prompt = summarize_prompt(
            query, indexed, session_tag, processing.pass_summary_cap_tokens
        )
        summary = client.generate(prompt)
        if summary.strip():
            pass_summaries.append(summary)
    return pass_summaries


def recursive_reduce(
    client: InferenceClient,
    query: SleuthQuery,
    summaries: list[str],
    processing: ProcessingConfig,
    session_tag: str,
    seed_aggregate: str | None = None,
) -> str:
    if not summaries:
        return ""

    if (
        len(summaries) == 1
        and estimate_tokens(summaries[0]) <= processing.final_summary_target_tokens
    ):
        return summaries[0]

    target = processing.final_summary_target_tokens
    max_items = processing.max_chunks_per_batch

    while len(summaries) > 1 or (
        len(summaries) == 1 and estimate_tokens(summaries[0]) > target
    ):
        overhead = merge_prompt_overhead(query, session_tag, target, seed_aggregate is not None)
        budget = content_budget(processing, overhead)
        groups = group_by_budget(summaries, budget, max_items)

        next_round: list[str] = []
        for group in groups:
            prompt = merge_prompt(query, group, session_tag, target, seed_aggregate)
            merged = client.generate(prompt)
            if merged.strip():
                next_round.append(merged)

        if not next_round:
            break
        summaries = next_round

    return summaries[0] if summaries else ""


def summary_body(summary: str) -> str | None:
    body = "\n".join(summary.splitlines()[1:]).strip()
    return body if body else None


def merge_into_summary_header(query: SleuthQuery, body: str) -> str:
    return f"# {query.description}\n\n{body.strip()}"
