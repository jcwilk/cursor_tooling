from __future__ import annotations

import sys
from pathlib import Path

from sleuth.checkpoint import checkpoint_path
from sleuth.config import sleuths_dir
from sleuth.query import list_sleuth_ids, load_query


def reset_sleuth(project_root: Path, sleuth_id: str) -> None:
    load_query(project_root, sleuth_id)
    _reset_sleuth_artifacts(project_root, sleuth_id)


def reset_all(project_root: Path) -> None:
    ids = list_sleuth_ids(project_root)
    if not ids:
        raise RuntimeError("no sleuths found under .sleuths/queries/")
    for sleuth_id in ids:
        _reset_sleuth_artifacts(project_root, sleuth_id)


def _reset_sleuth_artifacts(project_root: Path, sleuth_id: str) -> None:
    sleuth_dir = sleuths_dir(project_root) / sleuth_id
    summary_path = sleuth_dir / "summary.md"
    ckpt_path = checkpoint_path(sleuth_dir)

    removed: list[str] = []
    if summary_path.exists():
        summary_path.unlink()
        removed.append("summary.md")
    if ckpt_path.exists():
        ckpt_path.unlink()
        removed.append("checkpoint.yaml")

    if not removed:
        print(
            f"Sleuth '{sleuth_id}': nothing to reset (no summary or checkpoint)",
            file=sys.stderr,
        )
    else:
        print(
            f"Sleuth '{sleuth_id}': removed {', '.join(removed)}",
            file=sys.stderr,
        )
