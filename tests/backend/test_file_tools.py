from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gravity_ai.core.contracts import ToolCall, ToolStatus
from gravity_ai.tools import build_default_registry


class FileToolTests(unittest.TestCase):
    def test_list_search_copy_move_and_delete_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "notes.txt"
            source.write_text("gravity", encoding="utf-8")
            registry = build_default_registry()

            listed = registry.execute(
                ToolCall(tool_name="file.list", arguments={"path": str(root), "limit": 10})
            )
            self.assertEqual(listed.status, ToolStatus.SUCCESS)
            self.assertEqual(listed.content["count"], 1)

            searched = registry.execute(
                ToolCall(tool_name="file.search", arguments={"root": str(root), "query": "note"})
            )
            self.assertEqual(searched.status, ToolStatus.SUCCESS)
            self.assertEqual(searched.content["count"], 1)

            copied = registry.execute(
                ToolCall(
                    tool_name="file.copy",
                    arguments={"source": str(source), "destination": str(root / "copy.txt")},
                )
            )
            self.assertEqual(copied.status, ToolStatus.SUCCESS)
            self.assertTrue((root / "copy.txt").exists())

            moved = registry.execute(
                ToolCall(
                    tool_name="file.move",
                    arguments={"source": str(root / "copy.txt"), "destination": str(root / "moved.txt")},
                )
            )
            self.assertEqual(moved.status, ToolStatus.SUCCESS)
            self.assertTrue((root / "moved.txt").exists())

            blocked = registry.execute(
                ToolCall(tool_name="file.delete", arguments={"path": str(root / "moved.txt")})
            )
            self.assertEqual(blocked.status, ToolStatus.REQUIRES_CONFIRMATION)
            self.assertTrue((root / "moved.txt").exists())

            deleted = registry.execute(
                ToolCall(
                    tool_name="file.delete",
                    arguments={"path": str(root / "moved.txt")},
                    confirmed=True,
                )
            )
            self.assertEqual(deleted.status, ToolStatus.SUCCESS)
            self.assertFalse((root / "moved.txt").exists())

    def test_create_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "a" / "b"
            registry = build_default_registry()

            result = registry.execute(
                ToolCall(tool_name="directory.create", arguments={"path": str(target)})
            )

            self.assertEqual(result.status, ToolStatus.SUCCESS)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()

