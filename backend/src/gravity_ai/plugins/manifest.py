from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from gravity_ai.core.errors import PluginManifestError


class PluginPermission(StrEnum):
    FILESYSTEM_READ = "filesystem.read"
    FILESYSTEM_WRITE = "filesystem.write"
    FILESYSTEM_DELETE = "filesystem.delete"
    SYSTEM_PROCESS = "system.process"
    SYSTEM_SETTINGS = "system.settings"
    NETWORK = "network"
    BROWSER = "browser"
    AUTOMATION = "automation"
    MEMORY_READ = "memory.read"
    MEMORY_WRITE = "memory.write"


@dataclass(frozen=True)
class PluginCommand:
    name: str
    description: str
    tool: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PluginCommand":
        try:
            return cls(
                name=str(payload["name"]),
                description=str(payload["description"]),
                tool=str(payload["tool"]),
            )
        except KeyError as exc:
            raise PluginManifestError(f"Plugin command missing field: {exc.args[0]}") from exc


@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    entrypoint: str
    permissions: tuple[PluginPermission | str, ...] = field(default_factory=tuple)
    commands: tuple[PluginCommand, ...] = field(default_factory=tuple)
    settings: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: str | Path) -> "PluginManifest":
        manifest_path = Path(path)
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise PluginManifestError(f"Invalid JSON in {manifest_path}: {exc}") from exc
        return cls.from_dict(payload)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PluginManifest":
        try:
            plugin_id = str(payload["id"])
            name = str(payload["name"])
            version = str(payload["version"])
            entrypoint = str(payload["entrypoint"])
        except KeyError as exc:
            raise PluginManifestError(f"Plugin manifest missing field: {exc.args[0]}") from exc

        if not plugin_id or "." not in plugin_id:
            raise PluginManifestError("Plugin id must be a non-empty reverse-domain style id.")
        if not entrypoint:
            raise PluginManifestError("Plugin entrypoint is required.")

        commands_payload = payload.get("commands", [])
        if not isinstance(commands_payload, list):
            raise PluginManifestError("Plugin commands must be a list.")

        permissions_payload = payload.get("permissions", [])
        if not isinstance(permissions_payload, list):
            raise PluginManifestError("Plugin permissions must be a list.")

        return cls(
            plugin_id=plugin_id,
            name=name,
            version=version,
            entrypoint=entrypoint,
            permissions=tuple(_parse_permission(permission) for permission in permissions_payload),
            commands=tuple(PluginCommand.from_dict(item) for item in commands_payload),
            settings=dict(payload.get("settings", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["id"] = payload.pop("plugin_id")
        payload["permissions"] = [str(permission) for permission in self.permissions]
        return payload


def _parse_permission(value: object) -> PluginPermission | str:
    raw = str(value)
    try:
        return PluginPermission(raw)
    except ValueError:
        return raw
