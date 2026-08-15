from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from gravity_ai.core.errors import PluginManifestError
from gravity_ai.plugins.manifest import PluginManifest


@dataclass(frozen=True)
class LoadedPlugin:
    manifest: PluginManifest
    root: Path

    @property
    def entrypoint_path(self) -> Path:
        return (self.root / self.manifest.entrypoint).resolve()


class PluginLoader:
    def __init__(self, plugins_root: str | Path) -> None:
        self.plugins_root = Path(plugins_root)

    def discover(self) -> list[LoadedPlugin]:
        if not self.plugins_root.exists():
            return []

        loaded: list[LoadedPlugin] = []
        for manifest_path in sorted(self.plugins_root.glob("*/plugin.json")):
            manifest = PluginManifest.from_file(manifest_path)
            plugin = LoadedPlugin(manifest=manifest, root=manifest_path.parent.resolve())
            self._validate_entrypoint(plugin)
            loaded.append(plugin)
        return loaded

    def _validate_entrypoint(self, plugin: LoadedPlugin) -> None:
        entrypoint = plugin.entrypoint_path
        try:
            entrypoint.relative_to(plugin.root)
        except ValueError as exc:
            raise PluginManifestError(
                f"Plugin entrypoint escapes plugin directory: {plugin.manifest.plugin_id}"
            ) from exc
        if not entrypoint.exists():
            raise PluginManifestError(
                f"Plugin entrypoint does not exist for {plugin.manifest.plugin_id}: {entrypoint}"
            )

