from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gravity_ai import __version__
from gravity_ai.config import load_env_file
from gravity_ai.core.assistant import GravityAssistant
from gravity_ai.core.contracts import ToolCall
from gravity_ai.llm import build_llm_provider_from_env
from gravity_ai.memory.store import InMemoryMemoryStore, MemoryStore
from gravity_ai.plugins.loader import PluginLoader
from gravity_ai.storage.sqlite import SQLiteStorage
from gravity_ai.tools import ToolRegistry, build_default_registry


@dataclass
class ApplicationContext:
    root_dir: Path
    registry: ToolRegistry
    plugin_loader: PluginLoader
    memory: MemoryStore
    assistant: GravityAssistant
    storage: SQLiteStorage | None = None

    @classmethod
    def create(
        cls,
        root_dir: str | Path | None = None,
        persist: bool = True,
        load_env: bool = True,
    ) -> "ApplicationContext":
        resolved_root = Path(root_dir or os.environ.get("GRAVITY_AI_ROOT", Path.cwd())).resolve()
        if load_env:
            load_env_file(resolved_root / ".env")
        registry = build_default_registry()
        memory = InMemoryMemoryStore()
        storage: SQLiteStorage | None = None
        if persist:
            storage = SQLiteStorage(resolved_root / ".gravity" / "gravity.db")
            storage.migrate()
        plugin_loader = PluginLoader(resolved_root / "plugins")
        assistant = GravityAssistant(
            registry=registry,
            memory=memory,
            llm=build_llm_provider_from_env(),
        )
        return cls(
            root_dir=resolved_root,
            registry=registry,
            plugin_loader=plugin_loader,
            memory=memory,
            assistant=assistant,
            storage=storage,
        )

    def health(self) -> dict[str, Any]:
        plugins = self.plugin_loader.discover()
        return {
            "name": "Gravity AI",
            "version": __version__,
            "status": "ok",
            "rootDir": str(self.root_dir),
            "tools": len(self.registry.list_definitions()),
            "plugins": len(plugins),
        }

    def list_tools(self) -> dict[str, Any]:
        return {"tools": [definition.to_dict() for definition in self.registry.list_definitions()]}

    def list_plugins(self) -> dict[str, Any]:
        return {"plugins": [plugin.manifest.to_dict() for plugin in self.plugin_loader.discover()]}

    def execute_tool(self, payload: dict[str, Any]) -> dict[str, Any]:
        call = ToolCall(
            tool_name=str(payload.get("toolName") or payload.get("tool_name") or ""),
            arguments=dict(payload.get("arguments", {})),
            confirmed=bool(payload.get("confirmed", False)),
        )
        return self.registry.execute(call).to_dict()

    def chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        content = str(payload.get("message") or payload.get("content") or "")
        return self.assistant.respond(content).to_dict()

    def close(self) -> None:
        if self.storage is not None:
            self.storage.close()
