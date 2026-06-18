from __future__ import annotations

import re
import sys


def parse_relevant_ids(response: str, max_index: int) -> list[int]:
    """Parse LLM relevance output into zero-based chunk indices."""
    trimmed = _strip_code_fences(response.strip())
    if not trimmed:
        return []

    ids: list[int] = []
    saw_token = False
    for token in trimmed.split(","):
        part = token.strip()
        if not part:
            continue
        saw_token = True
        if not re.fullmatch(r"-?\d+", part):
            print(
                f"relevance: skipping non-numeric token {part!r}",
                file=sys.stderr,
            )
            continue
        idx = int(part)
        if idx < 0 or idx > max_index:
            continue
        if idx not in ids:
            ids.append(idx)

    if saw_token and not ids:
        print("relevance: no valid indices in response", file=sys.stderr)
        return []
    if not saw_token and trimmed:
        print(f"relevance: unparseable response: {trimmed!r}", file=sys.stderr)
        return []

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
