from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from sleuth.checkpoint import Checkpoint, SegmentKey, checkpoint_path
from sleuth.context_budget import group_by_budget, group_chunks_by_budget
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
