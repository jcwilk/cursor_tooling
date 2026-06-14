from __future__ import annotations

import json
from pathlib import Path


def extract_lines(path: Path, start_line_1based: int, end_line: int) -> str:
    """Extract text from JSONL lines start_line_1based..=end_line (1-based, inclusive)."""
    parts: list[str] = []
    with path.open(encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            if idx < start_line_1based:
                continue
            if idx > end_line:
                break
            line = line.strip()
            if not line:
                continue
            value = json.loads(line)
            text = _line_to_text(value)
            if text and text.strip():
                parts.append(text)
    return "\n\n".join(parts)


def count_lines(path: Path) -> int:
    with path.open(encoding="utf-8") as f:
        return sum(1 for _ in f)


def _line_to_text(value: dict) -> str | None:
    role = value.get("role")
    if not isinstance(role, str):
        return None
    message = value.get("message")
    if not isinstance(message, dict):
        return None
    content = message.get("content")
    if not isinstance(content, list):
        return None

    blocks: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        kind = block.get("type")
        if kind == "text":
            t = block.get("text")
            if isinstance(t, str):
                blocks.append(f"[{role}] {t}")
        elif kind == "tool_use":
            name = block.get("name", "tool")
            blocks.append(f"[{role}] tool_use: {name}")

    if not blocks:
        return None
    return "\n".join(blocks)
