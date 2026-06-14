from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class SegmentKey:
    transcript_id: str
    relative_path: str


@dataclass
class ProcessedSegment:
    transcript_id: str
    relative_path: str
    line_count: int


@dataclass
class Checkpoint:
    processed: list[ProcessedSegment]

    @classmethod
    def load(cls, path: Path) -> Checkpoint:
        if not path.exists():
            return cls(processed=[])
        with path.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        processed = [
            ProcessedSegment(
                transcript_id=str(p["transcript_id"]),
                relative_path=str(p["relative_path"]),
                line_count=int(p["line_count"]),
            )
            for p in raw.get("processed") or []
        ]
        return cls(processed=processed)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "processed": [
                {
                    "transcript_id": p.transcript_id,
                    "relative_path": p.relative_path,
                    "line_count": p.line_count,
                }
                for p in self.processed
            ]
        }
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def line_count_map(self) -> dict[SegmentKey, int]:
        return {
            SegmentKey(p.transcript_id, p.relative_path): p.line_count for p in self.processed
        }

    def upsert_segment(self, key: SegmentKey, line_count: int) -> None:
        for existing in self.processed:
            if (
                existing.transcript_id == key.transcript_id
                and existing.relative_path == key.relative_path
            ):
                existing.line_count = line_count
                return
        self.processed.append(
            ProcessedSegment(
                transcript_id=key.transcript_id,
                relative_path=key.relative_path,
                line_count=line_count,
            )
        )


def checkpoint_path(sleuth_dir: Path) -> Path:
    return sleuth_dir / "checkpoint.yaml"
