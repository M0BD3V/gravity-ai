from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ModelResponse:
    content: str
    model: str
    provider: str
    usage: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class LLMProvider(Protocol):
    @property
    def name(self) -> str:
        ...

    def generate(self, messages: list[ChatMessage]) -> ModelResponse:
        ...

