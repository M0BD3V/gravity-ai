from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from gravity_ai.memory.store import MemoryEntry, MemoryScope


class SQLiteStorage:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.database_path)
        self._connection.row_factory = sqlite3.Row

    def migrate(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_entries (
                entry_id TEXT PRIMARY KEY,
                scope TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    def upsert_memory(self, entry: MemoryEntry) -> MemoryEntry:
        self._connection.execute(
            """
            INSERT INTO memory_entries (
                entry_id, scope, key, value, metadata_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(entry_id) DO UPDATE SET
                scope=excluded.scope,
                key=excluded.key,
                value=excluded.value,
                metadata_json=excluded.metadata_json,
                updated_at=excluded.updated_at
            """,
            (
                entry.entry_id,
                entry.scope.value,
                entry.key,
                entry.value,
                json.dumps(entry.metadata, sort_keys=True),
                entry.created_at,
                entry.updated_at,
            ),
        )
        self._connection.commit()
        return entry

    def list_memory(self, scope: MemoryScope | None = None) -> list[MemoryEntry]:
        if scope is None:
            rows: Iterable[sqlite3.Row] = self._connection.execute(
                "SELECT * FROM memory_entries ORDER BY created_at ASC"
            )
        else:
            rows = self._connection.execute(
                "SELECT * FROM memory_entries WHERE scope = ? ORDER BY created_at ASC",
                (scope.value,),
            )
        return [self._row_to_memory(row) for row in rows]

    def _row_to_memory(self, row: sqlite3.Row) -> MemoryEntry:
        return MemoryEntry(
            entry_id=row["entry_id"],
            scope=MemoryScope(row["scope"]),
            key=row["key"],
            value=row["value"],
            metadata=json.loads(row["metadata_json"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

