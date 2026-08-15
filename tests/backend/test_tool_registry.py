from __future__ import annotations

import unittest

from gravity_ai.core.contracts import RiskLevel, ToolCall, ToolDefinition, ToolResult, ToolStatus
from gravity_ai.tools.registry import ToolRegistry


class ToolRegistryTests(unittest.TestCase):
    def test_registers_and_executes_tool(self) -> None:
        registry = ToolRegistry()
        registry.register(
            ToolDefinition(name="test.echo", description="Echo", risk=RiskLevel.SAFE),
            lambda call: ToolResult.ok(call.tool_name, {"value": call.arguments["value"]}, call.call_id),
        )

        result = registry.execute(ToolCall(tool_name="test.echo", arguments={"value": "ok"}))

        self.assertEqual(result.status, ToolStatus.SUCCESS)
        self.assertEqual(result.content["value"], "ok")

    def test_blocks_confirmation_tool_until_confirmed(self) -> None:
        registry = ToolRegistry()
        registry.register(
            ToolDefinition(
                name="test.delete",
                description="Delete",
                risk=RiskLevel.DESTRUCTIVE,
                requires_confirmation=True,
            ),
            lambda call: ToolResult.ok(call.tool_name, {"deleted": True}, call.call_id),
        )

        blocked = registry.execute(ToolCall(tool_name="test.delete"))
        allowed = registry.execute(ToolCall(tool_name="test.delete", confirmed=True))

        self.assertEqual(blocked.status, ToolStatus.REQUIRES_CONFIRMATION)
        self.assertEqual(allowed.status, ToolStatus.SUCCESS)

    def test_duplicate_registration_fails(self) -> None:
        registry = ToolRegistry()
        definition = ToolDefinition(name="test.echo", description="Echo", risk=RiskLevel.SAFE)
        registry.register(definition, lambda call: ToolResult.ok(call.tool_name))

        with self.assertRaises(ValueError):
            registry.register(definition, lambda call: ToolResult.ok(call.tool_name))


if __name__ == "__main__":
    unittest.main()

