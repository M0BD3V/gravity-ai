from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gravity_ai.memory import MemoryEntry, MemoryScope
from gravity_ai.storage import SQLiteStorage


class StorageTests(unittest.TestCase):
    def test_sqlite_persists_memory_entries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            storage = SQLiteStorage(Path(directory) / "gravity.db")
            storage.migrate()
            entry = MemoryEntry(
                scope=MemoryScope.PREFERENCE,
                key="notebook",
                value="Lenovo",
                metadata={"source": "test"},
            )

            storage.upsert_memory(entry)
            entries = storage.list_memory(MemoryScope.PREFERENCE)
            storage.close()

            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].key, "notebook")
            self.assertEqual(entries[0].value, "Lenovo")
            self.assertEqual(entries[0].metadata["source"], "test")


if __name__ == "__main__":
    unittest.main()

