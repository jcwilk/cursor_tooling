from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from sleuth.checkpoint import Checkpoint, SegmentKey, checkpoint_path
from sleuth.config import InferenceApi, OllamaConfig, ProcessingConfig, SleuthsConfig, TranscriptsConfig, load_config
from sleuth.context_budget import (
    group_by_budget,
    group_chunks_by_budget,
    group_chunks_by_min_max_budget,
)
from sleuth.discover import TranscriptSegment
from sleuth.inference import InferenceClient, _generate_ollama, _generate_openai_chat
from sleuth.pipeline import (
    merge_into_summary_header,
    recursive_reduce,
    run_relevance_pass,
    run_summarize_pass,
)
from sleuth.query import SleuthQuery
from sleuth.refresh import PendingWork, _refresh_sleuth_with_config
from sleuth.relevance import parse_relevant_ids
from sleuth.slug import slug_from_path
from sleuth.token import estimate_tokens


class TestProcessingConfig:
    def test_completion_limit_defaults(self):
        processing = ProcessingConfig()
        assert processing.relevance_max_completion_tokens == 200
        assert processing.summary_max_completion_tokens == 1000
        assert processing.pass_summary_cap_tokens == 1000
        assert processing.final_summary_target_tokens == 1000

    def test_load_config_parses_completion_limits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            sleuths = root / ".sleuths"
            sleuths.mkdir()
            (sleuths / "config.yaml").write_text(
                yaml.dump(
                    {
                        "ollama": {
                            "base_url": "http://127.0.0.1:11434",
                            "model": "test-model",
                        },
                        "processing": {
                            "relevance_max_completion_tokens": 150,
                            "summary_max_completion_tokens": 800,
                        },
                    }
                ),
                encoding="utf-8",
            )
            config = load_config(root)
            assert config.processing.relevance_max_completion_tokens == 150
            assert config.processing.summary_max_completion_tokens == 800


class TestInferenceClient:
    def test_ollama_request_includes_num_predict_when_limit_set(self):
        config = OllamaConfig(
            base_url="http://127.0.0.1:11434",
            model="test-model",
            api=InferenceApi.OLLAMA,
        )
        captured: dict = {}

        def fake_post(url, json, timeout):
            captured["url"] = url
            captured["body"] = json
            class Resp:
                ok = True

                def json(self):
                    return {"response": "ok"}

            return Resp()

        with patch("sleuth.inference.requests.post", side_effect=fake_post):
            _generate_ollama(config, "prompt", max_completion_tokens=200)

        assert captured["body"]["options"] == {"num_predict": 200}

    def test_ollama_request_omits_options_without_limit(self):
        config = OllamaConfig(
            base_url="http://127.0.0.1:11434",
            model="test-model",
            api=InferenceApi.OLLAMA,
        )
        captured: dict = {}

        def fake_post(url, json, timeout):
            captured["body"] = json
            class Resp:
                ok = True

                def json(self):
                    return {"response": "ok"}

            return Resp()

        with patch("sleuth.inference.requests.post", side_effect=fake_post):
            _generate_ollama(config, "prompt")

        assert "options" not in captured["body"]

    def test_openai_chat_request_includes_max_tokens_when_limit_set(self):
        config = OllamaConfig(
            base_url="http://127.0.0.1:11435",
            model="test-model",
            api=InferenceApi.OPENAI_CHAT,
        )
        captured: dict = {}

        def fake_post(url, json, timeout):
            captured["url"] = url
            captured["body"] = json
            class Resp:
                ok = True
                text = '{"choices":[{"message":{"content":"ok"}}]}'

            return Resp()

        with patch("sleuth.inference.requests.post", side_effect=fake_post):
            _generate_openai_chat(config, "prompt", max_completion_tokens=1000)

        assert captured["body"]["max_tokens"] == 1000

    def test_openai_chat_request_omits_max_tokens_without_limit(self):
        config = OllamaConfig(
            base_url="http://127.0.0.1:11435",
            model="test-model",
            api=InferenceApi.OPENAI_CHAT,
        )
        captured: dict = {}

        def fake_post(url, json, timeout):
            captured["body"] = json
            class Resp:
                ok = True
                text = '{"choices":[{"message":{"content":"ok"}}]}'

            return Resp()

        with patch("sleuth.inference.requests.post", side_effect=fake_post):
            _generate_openai_chat(config, "prompt")

        assert "max_tokens" not in captured["body"]


class TestPipelineCompletionLimits:
    def _chunk(self, index: int, chars: int):
        from sleuth.chunk import IndexedChunk

        return IndexedChunk(index=index, text="x" * chars)

    def test_relevance_pass_uses_relevance_completion_limit(self):
        from unittest.mock import Mock

        query = _make_query()
        processing = ProcessingConfig(
            relevance_min_content_tokens=100,
            relevance_max_content_tokens=5000,
            relevance_max_completion_tokens=200,
            max_chunks_per_batch=20,
        )
        chunks = [self._chunk(0, 400)]
        client = Mock()
        client.generate.return_value = '{"relevant_ids": [0]}'

        run_relevance_pass(client, query, chunks, processing, "sess")

        client.generate.assert_called_once()
        _, kwargs = client.generate.call_args
        assert kwargs["max_completion_tokens"] == 200

    def test_summarize_pass_uses_summary_completion_limit(self):
        from unittest.mock import Mock

        query = _make_query()
        processing = ProcessingConfig(
            summarize_target_content_tokens=8000,
            summary_max_completion_tokens=1000,
            pass_summary_cap_tokens=1000,
            max_chunks_per_batch=20,
        )
        chunks = [self._chunk(0, 400)]
        client = Mock()
        client.generate.return_value = "summary text"

        run_summarize_pass(client, query, chunks, processing, "sess")

        client.generate.assert_called_once()
        _, kwargs = client.generate.call_args
        assert kwargs["max_completion_tokens"] == 1000

    def test_merge_pass_uses_summary_completion_limit(self):
        from unittest.mock import Mock

        query = _make_query()
        processing = ProcessingConfig(
            merge_target_content_tokens=8000,
            merge_max_items_per_batch=2,
            summary_max_completion_tokens=1000,
            final_summary_target_tokens=100,
        )
        summaries = ["summary 0", "summary 1", "summary 2"]
        client = Mock()
        client.generate.return_value = "merged"

        recursive_reduce(client, query, summaries, processing, "sess")

        assert client.generate.call_count >= 1
        for call in client.generate.call_args_list:
            _, kwargs = call
            assert kwargs["max_completion_tokens"] == 1000


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


class TestSessionScopedRefresh:
    def test_session_filter_limits_segments_and_preserves_other_checkpoints(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root, query = _setup_project(root)
            sleuth_dir = root / ".sleuths" / "test-sleuth"
            sleuth_dir.mkdir(parents=True)

            other_key = SegmentKey(transcript_id="other-session", relative_path="other-session.jsonl")
            ckpt = Checkpoint(processed=[])
            ckpt.upsert_segment(other_key, 5)
            ckpt.save(checkpoint_path(sleuth_dir))

            target_path = root / "target.jsonl"
            target_path.write_text('{"role":"user","content":"line"}\n', encoding="utf-8")
            other_path = root / "other.jsonl"
            other_path.write_text('{"role":"user","content":"other"}\n', encoding="utf-8")

            segments = [
                _make_segment("target-session", target_path),
                TranscriptSegment(
                    transcript_id="other-session",
                    relative_path="other-session.jsonl",
                    absolute_path=other_path,
                    mtime=2.0,
                ),
            ]

            processed_segments: list[str] = []

            def fake_segment_pipeline(_client, _query, path, start_line, end_line, *_args, **_kwargs):
                processed_segments.append(f"{path}:{start_line}-{end_line}")
                return "session summary"

            with (
                patch("sleuth.refresh.resolve_slugs", return_value=["slug"]),
                patch("sleuth.refresh.discover_segments", return_value=segments),
                patch("sleuth.refresh.run_segment_pipeline", side_effect=fake_segment_pipeline),
                patch(
                    "sleuth.refresh.cross_segment_reduce",
                    return_value="merged body",
                ),
            ):
                _refresh_sleuth_with_config(
                    root,
                    "test-sleuth",
                    _make_config(),
                    session_id="target-session",
                )

            assert len(processed_segments) == 1
            assert "target.jsonl:1-1" in processed_segments[0]

            loaded = Checkpoint.load(checkpoint_path(sleuth_dir))
            assert loaded.line_count_map()[other_key] == 5
            target_key = SegmentKey(
                transcript_id="target-session",
                relative_path="target-session.jsonl",
            )
            assert loaded.line_count_map()[target_key] == 1

    def test_session_scope_reprocesses_from_line_one_when_checkpoint_complete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root, query = _setup_project(root)
            sleuth_dir = root / ".sleuths" / "test-sleuth"
            sleuth_dir.mkdir(parents=True)

            seg_path = root / "sess.jsonl"
            seg_path.write_text('{"role":"user","content":"line"}\n', encoding="utf-8")
            segment = _make_segment("sess-a", seg_path)

            key = SegmentKey(transcript_id="sess-a", relative_path="sess-a.jsonl")
            ckpt = Checkpoint(processed=[])
            ckpt.upsert_segment(key, 1)
            ckpt.save(checkpoint_path(sleuth_dir))

            pipeline_calls: list[tuple[int, int]] = []

            def fake_segment_pipeline(_client, _query, _path, start_line, end_line, *_args, **_kwargs):
                pipeline_calls.append((start_line, end_line))
                return "reprocessed summary"

            with (
                patch("sleuth.refresh.resolve_slugs", return_value=["slug"]),
                patch("sleuth.refresh.discover_segments", return_value=[segment]),
                patch("sleuth.refresh.run_segment_pipeline", side_effect=fake_segment_pipeline),
                patch(
                    "sleuth.refresh.cross_segment_reduce",
                    return_value="merged body",
                ),
            ):
                _refresh_sleuth_with_config(
                    root,
                    "test-sleuth",
                    _make_config(),
                    session_id="sess-a",
                )

            assert pipeline_calls == [(1, 1)]

    def test_dry_run_does_not_write_artifacts_and_prints_summary(self, capsys):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root, query = _setup_project(root)
            sleuth_dir = root / ".sleuths" / "test-sleuth"
            sleuth_dir.mkdir(parents=True)

            original_summary = merge_into_summary_header(query, "prior body")
            summary_path = sleuth_dir / "summary.md"
            summary_path.write_text(original_summary, encoding="utf-8")

            ckpt = Checkpoint(processed=[])
            ckpt.save(checkpoint_path(sleuth_dir))

            seg_path = root / "seg0.jsonl"
            seg_path.write_text('{"role":"user","content":"line"}\n', encoding="utf-8")
            segment = _make_segment("seg0", seg_path)

            with (
                patch("sleuth.refresh.resolve_slugs", return_value=["slug"]),
                patch("sleuth.refresh.discover_segments", return_value=[segment]),
                patch("sleuth.refresh.run_segment_pipeline", return_value="new summary"),
                patch(
                    "sleuth.refresh.cross_segment_reduce",
                    return_value="dry-run merged body",
                ),
            ):
                _refresh_sleuth_with_config(
                    root,
                    "test-sleuth",
                    _make_config(),
                    dry_run=True,
                )

            captured = capsys.readouterr()
            assert summary_path.read_text(encoding="utf-8") == original_summary
            assert Checkpoint.load(checkpoint_path(sleuth_dir)).line_count_map() == {}
            assert "dry-run merged body" in captured.out
            assert "# Test sleuth" in captured.out
            assert captured.err

    def test_dry_run_with_session_reprocesses_without_persistence(self, capsys):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root, query = _setup_project(root)
            sleuth_dir = root / ".sleuths" / "test-sleuth"
            sleuth_dir.mkdir(parents=True)

            seg_path = root / "sess.jsonl"
            seg_path.write_text('{"role":"user","content":"line"}\n', encoding="utf-8")
            segment = _make_segment("sess-x", seg_path)

            key = SegmentKey(transcript_id="sess-x", relative_path="sess-x.jsonl")
            ckpt = Checkpoint(processed=[])
            ckpt.upsert_segment(key, 1)
            ckpt.save(checkpoint_path(sleuth_dir))

            pipeline_calls: list[tuple[int, int]] = []

            def fake_segment_pipeline(_client, _query, _path, start_line, end_line, *_args, **_kwargs):
                pipeline_calls.append((start_line, end_line))
                return "session summary"

            with (
                patch("sleuth.refresh.resolve_slugs", return_value=["slug"]),
                patch("sleuth.refresh.discover_segments", return_value=[segment]),
                patch("sleuth.refresh.run_segment_pipeline", side_effect=fake_segment_pipeline),
                patch(
                    "sleuth.refresh.cross_segment_reduce",
                    return_value="session dry-run body",
                ),
            ):
                _refresh_sleuth_with_config(
                    root,
                    "test-sleuth",
                    _make_config(),
                    session_id="sess-x",
                    dry_run=True,
                )

            captured = capsys.readouterr()
            assert pipeline_calls == [(1, 1)]
            assert Checkpoint.load(checkpoint_path(sleuth_dir)).line_count_map()[key] == 1
            assert "session dry-run body" in captured.out

    def test_unknown_session_errors_before_inference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root, _query = _setup_project(root)

            with (
                patch("sleuth.refresh.resolve_slugs", return_value=["slug"]),
                patch("sleuth.refresh.discover_segments", return_value=[]),
                patch("sleuth.refresh.run_segment_pipeline") as pipeline_mock,
                pytest.raises(RuntimeError, match="no transcript segments found"),
            ):
                _refresh_sleuth_with_config(
                    root,
                    "test-sleuth",
                    _make_config(),
                    session_id="missing-session",
                )

            pipeline_mock.assert_not_called()


class TestRefreshCli:
    def test_session_requires_sleuth(self):
        from click.testing import CliRunner

        from sleuth.cli import cli

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(
                cli,
                ["--project-root", tmpdir, "refresh", "--session", "abc"],
            )
            assert result.exit_code == 1
            assert "--session requires --sleuth" in result.output

    def test_session_incompatible_with_all(self):
        from click.testing import CliRunner

        from sleuth.cli import cli

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(
                cli,
                [
                    "--project-root",
                    tmpdir,
                    "refresh",
                    "--all",
                    "--session",
                    "abc",
                ],
            )
            assert result.exit_code == 1
            assert "--session is incompatible with --all" in result.output
