from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from gravity_ai.core.contracts import ToolCall, ToolDefinition, ToolResult
from gravity_ai.core.safety import requires_confirmation


ToolHandler = Callable[[ToolCall], ToolResult]


@dataclass(frozen=True)
class RegisteredTool:
    definition: ToolDefinition
    handler: ToolHandler


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(self, definition: ToolDefinition, handler: ToolHandler) -> None:
        if definition.name in self._tools:
            raise ValueError(f"Tool already registered: {definition.name}")
        self._tools[definition.name] = RegisteredTool(definition=definition, handler=handler)

    def get(self, name: str) -> ToolDefinition | None:
        registered = self._tools.get(name)
        return registered.definition if registered else None

    def list_definitions(self) -> list[ToolDefinition]:
        return [registered.definition for registered in self._tools.values()]

    def execute(self, call: ToolCall) -> ToolResult:
        registered = self._tools.get(call.tool_name)
        if registered is None:
            return ToolResult.error_result(
                tool_name=call.tool_name,
                error=f"Unknown tool: {call.tool_name}",
                call_id=call.call_id,
            )

        if requires_confirmation(registered.definition) and not call.confirmed:
            return ToolResult.confirmation_required(
                tool_name=call.tool_name,
                reason="This tool requires explicit confirmation before execution.",
                call_id=call.call_id,
            )

        try:
            return registered.handler(call)
        except Exception as exc:  # noqa: BLE001 - handlers must not crash the runtime
            return ToolResult.error_result(
                tool_name=call.tool_name,
                error=str(exc),
                call_id=call.call_id,
            )

