from __future__ import annotations

import json
import re
import sys


def parse_relevant_ids(response: str, max_index: int) -> list[int]:
    """Parse LLM relevance output into zero-based chunk indices."""
    trimmed = _strip_code_fences(response.strip())
    try:
        parsed = json.loads(trimmed)
    except json.JSONDecodeError as e:
        print(f"relevance: failed to parse JSON: {e}", file=sys.stderr)
        return []

    raw_ids = parsed.get("relevant_ids", []) if isinstance(parsed, dict) else []
    ids: list[int] = []
    for v in raw_ids:
        idx: int | None = None
        if isinstance(v, int):
            idx = v
        elif isinstance(v, float) and v.is_integer():
            idx = int(v)
        if idx is None or idx > max_index:
            continue
        if idx not in ids:
            ids.append(idx)
    ids.sort()
    return ids


def _strip_code_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```json"):
        rest = s[7:]
        if rest.endswith("```"):
            rest = rest[:-3]
        return rest.strip()
    if s.startswith("```"):
        rest = s[3:]
        if rest.endswith("```"):
            rest = rest[:-3]
        return rest.strip()
    return s
