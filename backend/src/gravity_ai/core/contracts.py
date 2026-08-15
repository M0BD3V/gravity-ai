from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum, StrEnum
from typing import Any, Mapping
from uuid import uuid4


class RiskLevel(StrEnum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    DESTRUCTIVE = "destructive"


class ToolPermission(StrEnum):
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


class ToolStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "error"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters_schema: Mapping[str, Any] = field(default_factory=dict)
    permissions: tuple[ToolPermission, ...] = field(default_factory=tuple)
    risk: RiskLevel = RiskLevel.LOW
    requires_confirmation: bool = False

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(frozen=True)
class ToolCall:
    tool_name: str
    arguments: Mapping[str, Any] = field(default_factory=dict)
    confirmed: bool = False
    call_id: str = field(default_factory=lambda: str(uuid4()))
    requested_at: str = field(default_factory=lambda: utc_now())

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    status: ToolStatus
    content: Mapping[str, Any] = field(default_factory=dict)
    error: str | None = None
    call_id: str | None = None
    completed_at: str = field(default_factory=lambda: utc_now())

    @classmethod
    def ok(
        cls,
        tool_name: str,
        content: Mapping[str, Any] | None = None,
        call_id: str | None = None,
    ) -> "ToolResult":
        return cls(
            tool_name=tool_name,
            status=ToolStatus.SUCCESS,
            content=content or {},
            call_id=call_id,
        )

    @classmethod
    def error_result(
        cls,
        tool_name: str,
        error: str,
        call_id: str | None = None,
    ) -> "ToolResult":
        return cls(
            tool_name=tool_name,
            status=ToolStatus.ERROR,
            error=error,
            call_id=call_id,
        )

    @classmethod
    def confirmation_required(
        cls,
        tool_name: str,
        reason: str,
        call_id: str | None = None,
    ) -> "ToolResult":
        return cls(
            tool_name=tool_name,
            status=ToolStatus.REQUIRES_CONFIRMATION,
            error=reason,
            call_id=call_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    return value

