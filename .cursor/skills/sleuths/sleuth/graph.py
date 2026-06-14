from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, StateGraph

from sleuth.chunk import IndexedChunk
from sleuth.config import ProcessingConfig
from sleuth.inference import InferenceClient
from sleuth.pipeline import (
    recursive_reduce,
    run_relevance_pass,
    run_summarize_pass,
    stream_chunks,
)
from sleuth.query import SleuthQuery


class SegmentState(TypedDict):
    query: SleuthQuery
    processing: ProcessingConfig
    segment_path: str
    session_tag: str
    start_line: int
    end_line: int
    chunks: list[IndexedChunk]
    relevant_chunks: list[IndexedChunk]
    pass_summaries: list[str]
    segment_summary: str


def build_segment_graph(client: InferenceClient) -> StateGraph:
    def load_chunks(state: SegmentState) -> dict:
        path = Path(state["segment_path"])
        chunks = stream_chunks(
            path,
            state["start_line"],
            state["end_line"],
            state["processing"].chunk_lines,
        )
        return {"chunks": chunks}

    def relevance_pass(state: SegmentState) -> dict:
        relevant = run_relevance_pass(
            client,
            state["query"],
            state["chunks"],
            state["processing"],
            state["session_tag"],
        )
        return {"relevant_chunks": relevant}

    def summarize_pass(state: SegmentState) -> dict:
        pass_summaries = run_summarize_pass(
            client,
            state["query"],
            state["relevant_chunks"],
            state["processing"],
            state["session_tag"],
        )
        return {"pass_summaries": pass_summaries}

    def hierarchical_reduce(state: SegmentState) -> dict:
        segment_summary = recursive_reduce(
            client,
            state["query"],
            state["pass_summaries"],
            state["processing"],
            state["session_tag"],
            None,
        )
        return {"segment_summary": segment_summary}

    graph = StateGraph(SegmentState)
    graph.add_node("load_chunks", load_chunks)
    graph.add_node("relevance_pass", relevance_pass)
    graph.add_node("summarize_pass", summarize_pass)
    graph.add_node("hierarchical_reduce", hierarchical_reduce)
    graph.set_entry_point("load_chunks")
    graph.add_edge("load_chunks", "relevance_pass")
    graph.add_edge("relevance_pass", "summarize_pass")
    graph.add_edge("summarize_pass", "hierarchical_reduce")
    graph.add_edge("hierarchical_reduce", END)
    return graph


def run_segment_pipeline(
    client: InferenceClient,
    query: SleuthQuery,
    transcript_path: Path,
    start_line: int,
    end_line: int,
    processing: ProcessingConfig,
    session_tag: str,
) -> str:
    graph = build_segment_graph(client).compile()
    initial: SegmentState = {
        "query": query,
        "processing": processing,
        "segment_path": str(transcript_path),
        "session_tag": session_tag,
        "start_line": start_line,
        "end_line": end_line,
        "chunks": [],
        "relevant_chunks": [],
        "pass_summaries": [],
        "segment_summary": "",
    }
    result = graph.invoke(initial)
    return str(result.get("segment_summary", ""))
