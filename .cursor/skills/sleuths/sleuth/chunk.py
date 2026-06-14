from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IndexedChunk:
    index: int
    text: str
