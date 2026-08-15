from __future__ import annotations


class GravityError(Exception):
    """Base exception for expected Gravity AI failures."""


class ToolNotFoundError(GravityError):
    """Raised when a tool call references an unknown tool."""


class PluginManifestError(GravityError):
    """Raised when a plugin manifest is invalid."""


class PermissionDeniedError(GravityError):
    """Raised when a policy blocks an action."""

