from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from sleuth.config import sleuths_dir


@dataclass
class SleuthQuery:
    id: str
    description: str
    prompt: str


def load_query(project_root: Path, sleuth_id: str) -> SleuthQuery:
    path = sleuths_dir(project_root) / "queries" / f"{sleuth_id}.yaml"
    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    qid = raw.get("id") or sleuth_id
    return SleuthQuery(
        id=str(qid),
        description=str(raw["description"]),
        prompt=str(raw["prompt"]),
    )


def list_sleuth_ids(project_root: Path) -> list[str]:
    queries_dir = sleuths_dir(project_root) / "queries"
    if not queries_dir.is_dir():
        return []
    ids = [
        p.stem
        for p in queries_dir.iterdir()
        if p.is_file() and p.suffix == ".yaml"
    ]
    ids.sort()
    return ids
