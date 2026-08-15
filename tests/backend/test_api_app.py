from __future__ import annotations

import pathlib
import unittest

from gravity_ai.api.app import ApplicationContext


ROOT = pathlib.Path(__file__).resolve().parents[2]


class ApplicationContextTests(unittest.TestCase):
    def test_health_lists_tools_and_plugins(self) -> None:
        app = ApplicationContext.create(root_dir=ROOT, persist=False, load_env=False)

        health = app.health()

        self.assertEqual(health["status"], "ok")
        self.assertGreaterEqual(health["tools"], 7)
        self.assertEqual(health["plugins"], 1)

    def test_execute_tool_uses_registry_policy(self) -> None:
        app = ApplicationContext.create(root_dir=ROOT, persist=False, load_env=False)

        result = app.execute_tool({"toolName": "file.delete", "arguments": {"path": "missing.txt"}})

        self.assertEqual(result["status"], "requires_confirmation")

    def test_chat_returns_local_response(self) -> None:
        app = ApplicationContext.create(root_dir=ROOT, persist=False, load_env=False)

        response = app.chat({"message": "Procure aquele PDF que baixei ontem."})

        self.assertIn("Recebi sua solicitacao", response["message"])
        self.assertIn("file.search", response["toolSuggestions"])


if __name__ == "__main__":
    unittest.main()
