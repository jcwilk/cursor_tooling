from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sleuth.config import SleuthsConfig, cursor_projects_dir
from sleuth.slug import slug_from_path


@dataclass
class TranscriptSegment:
    transcript_id: str
    relative_path: str
    absolute_path: Path
    mtime: float


def resolve_slugs(project_root: Path, config: SleuthsConfig) -> list[str]:
    slugs = [slug_from_path(project_root)]

    if (project_root / ".git").exists():
        try:
            for path in _git_worktree_paths(project_root):
                s = slug_from_path(path)
                if s not in slugs:
                    slugs.append(s)
        except (OSError, subprocess.CalledProcessError):
            pass

    for s in config.transcripts.extra_transcript_slugs:
        if s not in slugs:
            slugs.append(s)

    slugs = sorted(set(slugs))
    print(f"Resolved transcript slugs: {', '.join(slugs)}", file=sys.stderr)
    return slugs


def _git_worktree_paths(project_root: Path) -> list[Path]:
    output = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=True,
    )
    paths: list[Path] = []
    for line in output.stdout.splitlines():
        if line.startswith("worktree "):
            paths.append(Path(line[len("worktree ") :]))
    return paths


def discover_segments(slugs: list[str]) -> list[TranscriptSegment]:
    projects = cursor_projects_dir()
    segments: list[TranscriptSegment] = []

    for slug in slugs:
        root = projects / slug / "agent-transcripts"
        if not root.is_dir():
            continue

        for path in root.rglob("*.jsonl"):
            if not path.is_file():
                continue
            transcript_id = _session_id_from_path(root, path)
            relative_path = path.relative_to(root).as_posix()
            try:
                mtime = path.stat().st_mtime
            except OSError:
                mtime = 0.0
            segments.append(
                TranscriptSegment(
                    transcript_id=transcript_id,
                    relative_path=relative_path,
                    absolute_path=path,
                    mtime=mtime,
                )
            )

    segments.sort(key=lambda s: s.mtime)
    return segments


def _session_id_from_path(agent_transcripts: Path, jsonl: Path) -> str:
    rel = jsonl.relative_to(agent_transcripts)
    parts = rel.parts
    if not parts:
        raise ValueError(f"unexpected jsonl path: {jsonl}")
    return parts[0]
