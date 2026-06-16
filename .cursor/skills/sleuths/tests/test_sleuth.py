from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from sleuth.checkpoint import Checkpoint, SegmentKey, checkpoint_path
from sleuth.config import InferenceApi, OllamaConfig, ProcessingConfig, SleuthsConfig, TranscriptsConfig
from sleuth.context_budget import (
    group_by_budget,
    group_chunks_by_budget,
    group_chunks_by_min_max_budget,
)
from sleuth.discover import TranscriptSegment
from sleuth.pipeline import merge_into_summary_header, run_relevance_pass
from sleuth.query import SleuthQuery
from sleuth.refresh import PendingWork, _refresh_sleuth_with_config
from sleuth.relevance import parse_relevant_ids
from sleuth.slug import slug_from_path
from sleuth.token import estimate_tokens


class TestSlug:
    def test_workspace_slug(self):
        assert (
            slug_from_path(Path("/home/user/workspace/cursor_tooling"))
            == "home-user-workspace-cursor-tooling"
        )

    def test_worktree_slug(self):
        assert (
            slug_from_path(Path("/home/user/.cursor/worktrees/my_app/abc12"))
            == "home-user-cursor-worktrees-my-app-abc12"
        )


class TestToken:
    def test_empty_is_zero(self):
        assert estimate_tokens("") == 0

    def test_four_chars_is_one_token(self):
        assert estimate_tokens("abcd") == 1
        assert estimate_tokens("abcde") == 2


class TestRelevance:
    def test_parses_valid_ids(self):
        assert parse_relevant_ids('{"relevant_ids": [0, 2, 5]}', 5) == [0, 2, 5]

    def test_ignores_out_of_range(self):
        assert parse_relevant_ids('{"relevant_ids": [0, 99]}', 3) == [0]

    def test_strips_fences(self):
        raw = '```json\n{"relevant_ids": [1]}\n```'
        assert parse_relevant_ids(raw, 3) == [1]

    def test_parse_failure_empty(self):
        assert parse_relevant_ids("not json", 3) == []


class TestContextBudget:
    def _item(self, chars: int) -> str:
        return "x" * chars

    def _chunk(self, index: int, chars: int):
        from sleuth.chunk import IndexedChunk

        return IndexedChunk(index=index, text=self._item(chars))

    def test_single_oversized_item_splits(self):
        big = self._item(100)
        groups = group_by_budget([big], 10, 20)
        assert len(groups) >= 2
        joined = "".join(g for group in groups for g in group)
        assert len(joined) == len(big)

    def test_exact_fit_single_group(self):
        a = self._item(4)
        b = self._item(4)
        budget = estimate_tokens(a) + estimate_tokens(b)
        groups = group_by_budget([a, b], budget, 20)
        assert len(groups) == 1
        assert len(groups[0]) == 2

    def test_count_cap_splits_token_fitting_group(self):
        chunks = [self._chunk(i, 4) for i in range(5)]
        budget = estimate_tokens(self._item(4)) * 10
        groups = group_chunks_by_budget(chunks, budget, 2)
        assert len(groups) == 3
        assert len(groups[0]) == 2
        assert len(groups[1]) == 2
        assert len(groups[2]) == 1


class TestMinMaxBudget:
    def _chunk(self, index: int, chars: int):
        from sleuth.chunk import IndexedChunk

        return IndexedChunk(index=index, text="x" * chars)

    def _group_tokens(self, group: list) -> int:
        return sum(estimate_tokens(c.text) for c in group)

    def test_grows_until_minimum_target_met(self):
        # 500 est. tokens each; min=1000, max=5000
        chunks = [self._chunk(i, 2000) for i in range(5)]
        groups = group_chunks_by_min_max_budget(chunks, min_content=1000, max_content=5000, max_items=20)
        assert len(groups) >= 1
        assert self._group_tokens(groups[0]) >= 1000
        assert self._group_tokens(groups[0]) <= 5000

    def test_finalizes_before_exceeding_maximum(self):
        chunks = [self._chunk(i, 2000) for i in range(4)]  # 500 tokens each
        groups = group_chunks_by_min_max_budget(chunks, min_content=1000, max_content=1500, max_items=20)
        assert len(groups) >= 2
        for group in groups[:-1]:
            tokens = self._group_tokens(group)
            assert tokens >= 1000
            assert tokens <= 1500

    def test_short_tail_below_minimum_still_processes(self):
        chunks = [self._chunk(0, 400)]  # 100 tokens
        groups = group_chunks_by_min_max_budget(chunks, min_content=1000, max_content=5000, max_items=20)
        assert len(groups) == 1
        assert len(groups[0]) == 1

    def test_oversized_leading_chunk_truncation(self):
        big = self._chunk(0, 40000)  # 10000 tokens
        groups = group_chunks_by_min_max_budget([big], min_content=1000, max_content=2000, max_items=20)
        assert len(groups) >= 2
        assert self._group_tokens(groups[0]) <= 2000
        joined = "".join(c.text for group in groups for c in group)
        assert len(joined) == len(big.text)


class TestRelevanceBatching:
    def _chunk(self, index: int, chars: int):
        from sleuth.chunk import IndexedChunk

        return IndexedChunk(index=index, text="x" * chars)

    def test_relevance_batches_meet_min_target(self):
        from unittest.mock import Mock

        query = _make_query()
        processing = ProcessingConfig(
            relevance_min_content_tokens=1000,
            relevance_max_content_tokens=5000,
            max_chunks_per_batch=20,
        )
        chunks = [self._chunk(i, 2000) for i in range(8)]  # 500 tokens each

        relevance_calls: list[list] = []

        original_group = group_chunks_by_min_max_budget

        def capture_group(*args, **kwargs):
            groups = original_group(*args, **kwargs)
            relevance_calls.extend(groups)
            return groups

        client = Mock()
        client.generate.return_value = '{"relevant_ids": []}'

        with patch(
            "sleuth.pipeline.group_chunks_by_min_max_budget",
            side_effect=capture_group,
        ):
            run_relevance_pass(client, query, chunks, processing, "sess")

        assert relevance_calls
        for group in relevance_calls[:-1]:
            tokens = sum(estimate_tokens(c.text) for c in group)
            assert tokens >= 1000
            assert tokens <= 5000


class TestMergeBatching:
    def test_merge_groups_at_most_two_items(self):
        from unittest.mock import Mock

        from sleuth.pipeline import recursive_reduce

        query = _make_query()
        processing = ProcessingConfig(
            merge_target_content_tokens=8000,
            merge_max_items_per_batch=2,
            final_summary_target_tokens=100,
        )
        summaries = [f"summary {i}" for i in range(5)]

        merge_group_sizes: list[int] = []
        original_group = group_by_budget

        def capture_group(items, budget, max_items):
            groups = original_group(items, budget, max_items)
            merge_group_sizes.extend(len(g) for g in groups)
            return groups

        client = Mock()
        client.generate.return_value = "merged"

        with patch("sleuth.pipeline.group_by_budget", side_effect=capture_group):
            recursive_reduce(client, query, summaries, processing, "sess")

        assert merge_group_sizes
        assert all(size <= 2 for size in merge_group_sizes)


class TestCheckpoint:
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = checkpoint_path(Path(tmp))
            ckpt = Checkpoint(processed=[])
            key = SegmentKey(transcript_id="sess-1", relative_path="foo.jsonl")
            ckpt.upsert_segment(key, 42)
            ckpt.save(path)

            loaded = Checkpoint.load(path)
            assert loaded.line_count_map()[key] == 42

            ckpt.upsert_segment(key, 99)
            ckpt.save(path)
            loaded2 = Checkpoint.load(path)
            assert loaded2.line_count_map()[key] == 99


def _make_query() -> SleuthQuery:
    return SleuthQuery(
        id="test-sleuth",
        description="Test sleuth",
        prompt="Extract test facts.",
    )


def _make_config() -> SleuthsConfig:
    return SleuthsConfig(
        ollama=OllamaConfig(
            base_url="http://127.0.0.1:11434",
            model="test-model",
            api=InferenceApi.OLLAMA,
        ),
        transcripts=TranscriptsConfig(extra_transcript_slugs=[]),
        processing=ProcessingConfig(
            context_budget_tokens=16384,
            response_headroom_tokens=1000,
            pass_summary_cap_tokens=4000,
            final_summary_target_tokens=4000,
            chunk_lines=1,
            max_chunks_per_batch=20,
        ),
    )


def _make_segment(seg_id: str, path: Path) -> TranscriptSegment:
    return TranscriptSegment(
        transcript_id=seg_id,
        relative_path=f"{seg_id}.jsonl",
        absolute_path=path,
        mtime=1.0,
    )


def _setup_project(tmp: Path) -> tuple[Path, SleuthQuery]:
    query = _make_query()
    sleuths = tmp / ".sleuths"
    (sleuths / "queries").mkdir(parents=True)
    query_path = sleuths / "queries" / "test-sleuth.yaml"
    query_path.write_text(
        yaml.dump(
            {
                "id": query.id,
                "description": query.description,
                "prompt": query.prompt,
            }
        ),
        encoding="utf-8",
    )
    (sleuths / "config.yaml").write_text(
        yaml.dump(
            {
                "ollama": {
                    "base_url": "http://127.0.0.1:11434",
                    "model": "test-model",
                }
            }
        ),
        encoding="utf-8",
    )
    return tmp, query


class TestRefreshOrchestration:
    def test_cross_segment_merge_runs_once_after_n_segments(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root, query = _setup_project(root)
            sleuth_dir = root / ".sleuths" / "test-sleuth"
            sleuth_dir.mkdir(parents=True)

            seg_paths = []
            for i in range(3):
                p = root / f"seg{i}.jsonl"
                p.write_text('{"role":"user","content":"line"}\n', encoding="utf-8")
                seg_paths.append(p)

            segments = [_make_segment(f"seg{i}", seg_paths[i]) for i in range(3)]
            pending = [
                PendingWork(segment=segments[i], start_line=1, end_line=1)
                for i in range(3)
            ]

            cross_merge_calls: list[tuple[list[str], str | None]] = []

            def fake_segment_pipeline(*_args, **_kwargs) -> str:
                return "segment summary"

            def fake_cross_segment_reduce(
                _client, _query, summaries, _processing, _session_tag, seed
            ) -> str:
                cross_merge_calls.append((list(summaries), seed))
                return "final body"

            with (
                patch("sleuth.refresh.resolve_slugs", return_value=["slug"]),
                patch("sleuth.refresh.discover_segments", return_value=segments),
                patch("sleuth.refresh._pending_work", side_effect=pending),
                patch(
                    "sleuth.refresh.run_segment_pipeline",
                    side_effect=fake_segment_pipeline,
                ),
                patch(
                    "sleuth.refresh.cross_segment_reduce",
                    side_effect=fake_cross_segment_reduce,
                ),
            ):
                _refresh_sleuth_with_config(root, "test-sleuth", _make_config())

            assert len(cross_merge_calls) == 1
            summaries, seed = cross_merge_calls[0]
            assert summaries == ["segment summary", "segment summary", "segment summary"]
            assert seed is None

            summary_text = (sleuth_dir / "summary.md").read_text(encoding="utf-8")
            assert "final body" in summary_text

    def test_incremental_refresh_uses_prior_as_seed_not_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root, query = _setup_project(root)
            sleuth_dir = root / ".sleuths" / "test-sleuth"
            sleuth_dir.mkdir(parents=True)

            prior = "prior knowledge"
            summary_path = sleuth_dir / "summary.md"
            summary_path.write_text(
                merge_into_summary_header(query, prior), encoding="utf-8"
            )

            seg_path = root / "seg0.jsonl"
            seg_path.write_text('{"role":"user","content":"line"}\n', encoding="utf-8")
            segment = _make_segment("seg0", seg_path)
            pending = [PendingWork(segment=segment, start_line=1, end_line=1)]

            cross_merge_calls: list[tuple[list[str], str | None]] = []

            def fake_cross_segment_reduce(
                _client, _query, summaries, _processing, _session_tag, seed
            ) -> str:
                cross_merge_calls.append((list(summaries), seed))
                return "merged body"

            with (
                patch("sleuth.refresh.resolve_slugs", return_value=["slug"]),
                patch("sleuth.refresh.discover_segments", return_value=[segment]),
                patch("sleuth.refresh._pending_work", side_effect=pending),
                patch(
                    "sleuth.refresh.run_segment_pipeline",
                    return_value="new segment summary",
                ),
                patch(
                    "sleuth.refresh.cross_segment_reduce",
                    side_effect=fake_cross_segment_reduce,
                ),
            ):
                _refresh_sleuth_with_config(root, "test-sleuth", _make_config())

            assert len(cross_merge_calls) == 1
            summaries, seed = cross_merge_calls[0]
            assert summaries == ["new segment summary"]
            assert seed == prior
            assert prior not in summaries

    def test_mid_batch_failure_leaves_summary_unchanged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root, query = _setup_project(root)
            sleuth_dir = root / ".sleuths" / "test-sleuth"
            sleuth_dir.mkdir(parents=True)

            original_summary = merge_into_summary_header(query, "stable body")
            summary_path = sleuth_dir / "summary.md"
            summary_path.write_text(original_summary, encoding="utf-8")

            seg_paths = []
            for i in range(2):
                p = root / f"seg{i}.jsonl"
                p.write_text('{"role":"user","content":"line"}\n', encoding="utf-8")
                seg_paths.append(p)

            segments = [_make_segment(f"seg{i}", seg_paths[i]) for i in range(2)]
            pending = [
                PendingWork(segment=segments[i], start_line=1, end_line=1)
                for i in range(2)
            ]

            call_count = 0

            def flaky_segment_pipeline(*_args, **_kwargs) -> str:
                nonlocal call_count
                call_count += 1
                if call_count == 2:
                    raise RuntimeError("simulated failure")
                return "segment summary"

            with (
                patch("sleuth.refresh.resolve_slugs", return_value=["slug"]),
                patch("sleuth.refresh.discover_segments", return_value=segments),
                patch("sleuth.refresh._pending_work", side_effect=pending),
                patch(
                    "sleuth.refresh.run_segment_pipeline",
                    side_effect=flaky_segment_pipeline,
                ),
                pytest.raises(RuntimeError, match="simulated failure"),
            ):
                _refresh_sleuth_with_config(root, "test-sleuth", _make_config())

            assert summary_path.read_text(encoding="utf-8") == original_summary

            ckpt = Checkpoint.load(checkpoint_path(sleuth_dir))
            key = SegmentKey(transcript_id="seg0", relative_path="seg0.jsonl")
            assert ckpt.line_count_map()[key] == 1
            key2 = SegmentKey(transcript_id="seg1", relative_path="seg1.jsonl")
            assert key2 not in ckpt.line_count_map()
