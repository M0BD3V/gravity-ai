from __future__ import annotations

from gravity_ai.tools.builtins.filesystem import register_filesystem_tools
from gravity_ai.tools.registry import ToolRegistry


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    register_filesystem_tools(registry)
    return registry

