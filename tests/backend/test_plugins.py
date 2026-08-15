from __future__ import annotations

import pathlib
import tempfile
import unittest

from gravity_ai.core.errors import PluginManifestError
from gravity_ai.plugins import PluginLoader, PluginManifest, PluginPermission


ROOT = pathlib.Path(__file__).resolve().parents[2]


class PluginTests(unittest.TestCase):
    def test_discovers_example_plugin(self) -> None:
        loader = PluginLoader(ROOT / "plugins")

        plugins = loader.discover()

        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0].manifest.plugin_id, "gravity.example_file_assistant")
        self.assertIn(PluginPermission.FILESYSTEM_READ, plugins[0].manifest.permissions)
        self.assertTrue(plugins[0].entrypoint_path.exists())

    def test_manifest_validation_rejects_missing_required_fields(self) -> None:
        with self.assertRaises(PluginManifestError):
            PluginManifest.from_dict({"id": "gravity.bad"})

    def test_loader_rejects_missing_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            plugin_dir = root / "bad-plugin"
            plugin_dir.mkdir()
            (plugin_dir / "plugin.json").write_text(
                """
                {
                  "id": "gravity.bad_plugin",
                  "name": "Bad Plugin",
                  "version": "0.1.0",
                  "entrypoint": "missing.py",
                  "permissions": [],
                  "commands": []
                }
                """,
                encoding="utf-8",
            )

            with self.assertRaises(PluginManifestError):
                PluginLoader(root).discover()


if __name__ == "__main__":
    unittest.main()
