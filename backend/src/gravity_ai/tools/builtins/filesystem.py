from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from gravity_ai.core.contracts import (
    RiskLevel,
    ToolCall,
    ToolDefinition,
    ToolPermission,
    ToolResult,
)
from gravity_ai.tools.registry import ToolRegistry


def register_filesystem_tools(registry: ToolRegistry) -> None:
    registry.register(
        ToolDefinition(
            name="file.list",
            description="List files and directories in a path.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 200},
                },
            },
            permissions=(ToolPermission.FILESYSTEM_READ,),
            risk=RiskLevel.SAFE,
        ),
        _list_directory,
    )
    registry.register(
        ToolDefinition(
            name="file.search",
            description="Search files by name under a root directory.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "root": {"type": "string"},
                    "query": {"type": "string"},
                    "maxResults": {"type": "integer", "minimum": 1, "maximum": 200},
                },
                "required": ["root", "query"],
            },
            permissions=(ToolPermission.FILESYSTEM_READ,),
            risk=RiskLevel.SAFE,
        ),
        _search_files,
    )
    registry.register(
        ToolDefinition(
            name="program.open",
            description="Open a program by executable name or file path.",
            parameters_schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
            permissions=(ToolPermission.SYSTEM_PROCESS,),
            risk=RiskLevel.MEDIUM,
        ),
        _open_program,
    )
    registry.register(
        ToolDefinition(
            name="directory.create",
            description="Create a directory.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "parents": {"type": "boolean"},
                    "existOk": {"type": "boolean"},
                },
                "required": ["path"],
            },
            permissions=(ToolPermission.FILESYSTEM_WRITE,),
            risk=RiskLevel.LOW,
        ),
        _create_directory,
    )
    registry.register(
        ToolDefinition(
            name="file.copy",
            description="Copy a file to a destination.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "destination": {"type": "string"},
                },
                "required": ["source", "destination"],
            },
            permissions=(ToolPermission.FILESYSTEM_READ, ToolPermission.FILESYSTEM_WRITE),
            risk=RiskLevel.MEDIUM,
        ),
        _copy_file,
    )
    registry.register(
        ToolDefinition(
            name="file.move",
            description="Move a file to a destination.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "destination": {"type": "string"},
                },
                "required": ["source", "destination"],
            },
            permissions=(ToolPermission.FILESYSTEM_READ, ToolPermission.FILESYSTEM_WRITE),
            risk=RiskLevel.MEDIUM,
        ),
        _move_file,
    )
    registry.register(
        ToolDefinition(
            name="file.delete",
            description="Delete a single file after explicit confirmation.",
            parameters_schema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
            permissions=(ToolPermission.FILESYSTEM_DELETE,),
            risk=RiskLevel.DESTRUCTIVE,
            requires_confirmation=True,
        ),
        _delete_file,
    )


def _list_directory(call: ToolCall) -> ToolResult:
    path = _resolve_path(call.arguments.get("path") or ".")
    limit = _bounded_int(call.arguments.get("limit"), default=50, minimum=1, maximum=200)
    if not path.exists():
        return ToolResult.error_result(call.tool_name, f"Path does not exist: {path}", call.call_id)
    if not path.is_dir():
        return ToolResult.error_result(call.tool_name, f"Path is not a directory: {path}", call.call_id)

    entries = []
    for item in sorted(path.iterdir(), key=lambda value: (not value.is_dir(), value.name.lower()))[:limit]:
        entries.append(
            {
                "name": item.name,
                "path": str(item),
                "kind": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None,
            }
        )
    return ToolResult.ok(
        call.tool_name,
        {"path": str(path), "entries": entries, "count": len(entries)},
        call.call_id,
    )


def _search_files(call: ToolCall) -> ToolResult:
    root = _resolve_path(call.arguments.get("root") or ".")
    query = str(call.arguments.get("query") or "").lower().strip()
    max_results = _bounded_int(call.arguments.get("maxResults"), default=25, minimum=1, maximum=200)
    if not query:
        return ToolResult.error_result(call.tool_name, "Query is required.", call.call_id)
    if not root.exists() or not root.is_dir():
        return ToolResult.error_result(call.tool_name, f"Root directory is invalid: {root}", call.call_id)

    matches: list[dict[str, Any]] = []
    for item in _safe_walk(root):
        if query in item.name.lower():
            matches.append(
                {
                    "name": item.name,
                    "path": str(item),
                    "kind": "directory" if item.is_dir() else "file",
                }
            )
            if len(matches) >= max_results:
                break
    return ToolResult.ok(
        call.tool_name,
        {"root": str(root), "query": query, "matches": matches, "count": len(matches)},
        call.call_id,
    )


def _open_program(call: ToolCall) -> ToolResult:
    name = str(call.arguments.get("name") or "").strip()
    if not name:
        return ToolResult.error_result(call.tool_name, "Program name is required.", call.call_id)

    explicit_path = Path(name).expanduser()
    if explicit_path.exists():
        if os.name == "nt":
            os.startfile(str(explicit_path))  # type: ignore[attr-defined]
            return ToolResult.ok(call.tool_name, {"opened": str(explicit_path)}, call.call_id)
        process = subprocess.Popen([str(explicit_path)])  # noqa: S603
        return ToolResult.ok(call.tool_name, {"pid": process.pid, "opened": str(explicit_path)}, call.call_id)

    executable = shutil.which(name)
    if executable is None:
        return ToolResult.error_result(call.tool_name, f"Program not found: {name}", call.call_id)

    process = subprocess.Popen([executable])  # noqa: S603
    return ToolResult.ok(call.tool_name, {"pid": process.pid, "opened": executable}, call.call_id)


def _create_directory(call: ToolCall) -> ToolResult:
    path = _resolve_path(call.arguments.get("path"))
    parents = bool(call.arguments.get("parents", True))
    exist_ok = bool(call.arguments.get("existOk", True))
    path.mkdir(parents=parents, exist_ok=exist_ok)
    return ToolResult.ok(call.tool_name, {"path": str(path), "created": True}, call.call_id)


def _copy_file(call: ToolCall) -> ToolResult:
    source = _resolve_path(call.arguments.get("source"))
    destination = _resolve_path(call.arguments.get("destination"))
    if not source.is_file():
        return ToolResult.error_result(call.tool_name, f"Source file is invalid: {source}", call.call_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    final_path = shutil.copy2(source, destination)
    return ToolResult.ok(
        call.tool_name,
        {"source": str(source), "destination": str(Path(final_path).resolve())},
        call.call_id,
    )


def _move_file(call: ToolCall) -> ToolResult:
    source = _resolve_path(call.arguments.get("source"))
    destination = _resolve_path(call.arguments.get("destination"))
    if not source.exists():
        return ToolResult.error_result(call.tool_name, f"Source path is invalid: {source}", call.call_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    final_path = shutil.move(str(source), str(destination))
    return ToolResult.ok(
        call.tool_name,
        {"source": str(source), "destination": str(Path(final_path).resolve())},
        call.call_id,
    )


def _delete_file(call: ToolCall) -> ToolResult:
    path = _resolve_path(call.arguments.get("path"))
    if not path.exists():
        return ToolResult.error_result(call.tool_name, f"Path does not exist: {path}", call.call_id)
    if not path.is_file():
        return ToolResult.error_result(
            call.tool_name,
            "Only single-file deletion is enabled in Marco 1.",
            call.call_id,
        )
    path.unlink()
    return ToolResult.ok(call.tool_name, {"path": str(path), "deleted": True}, call.call_id)


def _resolve_path(value: object) -> Path:
    if value is None or str(value).strip() == "":
        raise ValueError("Path argument is required.")
    return Path(str(value)).expanduser().resolve()


def _bounded_int(value: object, default: int, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(minimum, min(maximum, number))


def _safe_walk(root: Path):
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            children = list(current.iterdir())
        except (OSError, PermissionError):
            continue
        for child in children:
            yield child
            if child.is_dir():
                stack.append(child)

