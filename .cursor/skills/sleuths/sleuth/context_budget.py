from __future__ import annotations

import json
import re
import sys

from sleuth.chunk import IndexedChunk
from sleuth.config import ProcessingConfig
from sleuth.token import estimate_tokens, truncate_prefix_to_tokens


def group_chunks_by_budget(
    chunks: list[IndexedChunk],
    available_budget: int,
    max_items: int,
) -> list[list[IndexedChunk]]:
    if not chunks:
        return []
    if available_budget == 0:
        return [chunks]

    groups: list[list[IndexedChunk]] = []
    pending = list(chunks)

    while pending:
        group: list[IndexedChunk] = []
        group_tokens = 0

        while pending:
            if max_items > 0 and len(group) >= max_items:
                break

            item = pending.pop(0)
            item_tokens = estimate_tokens(item.text)

            if not group and item_tokens > available_budget:
                prefix, remainder = truncate_prefix_to_tokens(item.text, available_budget)
                if prefix:
                    print(
                        f"context-budget: truncated chunk {item.index} "
                        f"({item_tokens} → {estimate_tokens(prefix)} est. tokens)",
                        file=sys.stderr,
                    )
                    group.append(IndexedChunk(index=item.index, text=prefix))
                if remainder:
                    pending.insert(0, IndexedChunk(index=item.index, text=remainder))
                break

            if group_tokens + item_tokens <= available_budget:
                group_tokens += item_tokens
                group.append(item)
                continue

            if len(group) > 1:
                pending.insert(0, item)
                break

            pending.insert(0, item)
            break

        if group:
            groups.append(group)
        elif pending:
            stuck = pending.pop(0)
            print(
                f"context-budget: dropping stuck chunk {stuck.index} — budget {available_budget}",
                file=sys.stderr,
            )

    return groups


def group_chunks_by_min_max_budget(
    chunks: list[IndexedChunk],
    min_content: int,
    max_content: int,
    max_items: int,
) -> list[list[IndexedChunk]]:
    if not chunks:
        return []
    if max_content <= 0:
        return [chunks]

    groups: list[list[IndexedChunk]] = []
    pending = list(chunks)

    while pending:
        group: list[IndexedChunk] = []
        group_tokens = 0

        while pending:
            if max_items > 0 and len(group) >= max_items:
                break

            item = pending[0]
            item_tokens = estimate_tokens(item.text)

            if group_tokens >= min_content and group_tokens + item_tokens > max_content:
                break

            if not group and item_tokens > max_content:
                prefix, remainder = truncate_prefix_to_tokens(item.text, max_content)
                pending.pop(0)
                if prefix:
                    print(
                        f"context-budget: truncated chunk {item.index} "
                        f"({item_tokens} → {estimate_tokens(prefix)} est. tokens)",
                        file=sys.stderr,
                    )
                    group.append(IndexedChunk(index=item.index, text=prefix))
                    group_tokens += estimate_tokens(prefix)
                if remainder:
                    pending.insert(0, IndexedChunk(index=item.index, text=remainder))
                break

            if group_tokens + item_tokens > max_content:
                if group_tokens >= min_content:
                    break
                if group:
                    break
                pending.pop(0)
                print(
                    f"context-budget: dropping stuck chunk {item.index} "
                    f"— max content {max_content}",
                    file=sys.stderr,
                )
                continue

            pending.pop(0)
            group_tokens += item_tokens
            group.append(item)

        if group:
            groups.append(group)
        elif pending:
            stuck = pending.pop(0)
            print(
                f"context-budget: dropping stuck chunk {stuck.index} "
                f"— max content {max_content}",
                file=sys.stderr,
            )

    return groups


def group_by_budget(
    items: list[str],
    available_budget: int,
    max_items: int,
) -> list[list[str]]:
    if not items:
        return []
    if available_budget == 0:
        return []

    groups: list[list[str]] = []
    pending = list(items)

    while pending:
        group: list[str] = []
        group_tokens = 0

        while pending:
            if max_items > 0 and len(group) >= max_items:
                break

            item = pending.pop(0)
            item_tokens = estimate_tokens(item)

            if not group and item_tokens > available_budget:
                prefix, remainder = truncate_prefix_to_tokens(item, available_budget)
                if prefix:
                    print(
                        f"context-budget: truncated oversized item "
                        f"({item_tokens} → {estimate_tokens(prefix)} est. tokens)",
                        file=sys.stderr,
                    )
                    group.append(prefix)
                if remainder:
                    pending.insert(0, remainder)
                break

            if group_tokens + item_tokens <= available_budget:
                group_tokens += item_tokens
                group.append(item)
                continue

            if len(group) > 1:
                pending.insert(0, item)
                break

            pending.insert(0, item)
            break

        if group:
            groups.append(group)
        elif pending:
            stuck = pending.pop(0)
            print(
                f"context-budget: dropping stuck item ({estimate_tokens(stuck)} est. tokens) "
                f"— budget {available_budget}",
                file=sys.stderr,
            )

    return groups
