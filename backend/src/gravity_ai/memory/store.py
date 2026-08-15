from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Protocol
from uuid import uuid4

from gravity_ai.core.contracts import utc_now


class MemoryScope(StrEnum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    PREFERENCE = "preference"
    HISTORY = "history"
    CONTEXT = "context"


@dataclass(frozen=True)
class MemoryEntry:
    key: str
    value: str
    scope: MemoryScope
    metadata: dict[str, str] = field(default_factory=dict)
    entry_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["scope"] = self.scope.value
        return payload


@dataclass(frozen=True)
class MemoryQuery:
    scope: MemoryScope | None = None
    text: str | None = None
    limit: int = 20


class MemoryStore(Protocol):
    def add(self, entry: MemoryEntry) -> MemoryEntry:
        ...

    def search(self, query: MemoryQuery) -> list[MemoryEntry]:
        ...


class InMemoryMemoryStore:
    def __init__(self) -> None:
        self._entries: list[MemoryEntry] = []

    def add(self, entry: MemoryEntry) -> MemoryEntry:
        self._entries.append(entry)
        return entry

    def search(self, query: MemoryQuery) -> list[MemoryEntry]:
        limit = max(1, min(query.limit, 100))
        entries = self._entries
        if query.scope is not None:
            entries = [entry for entry in entries if entry.scope == query.scope]
        if query.text:
            needle = query.text.lower()
            entries = [
                entry
                for entry in entries
                if needle in entry.key.lower() or needle in entry.value.lower()
            ]
        return entries[:limit]

