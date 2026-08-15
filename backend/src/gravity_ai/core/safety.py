from __future__ import annotations

from gravity_ai.core.contracts import RiskLevel, ToolDefinition


DESTRUCTIVE_RISKS = {RiskLevel.HIGH, RiskLevel.DESTRUCTIVE}


def requires_confirmation(definition: ToolDefinition) -> bool:
    return definition.requires_confirmation or definition.risk in DESTRUCTIVE_RISKS

