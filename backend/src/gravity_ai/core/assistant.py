from __future__ import annotations

from dataclasses import dataclass

from gravity_ai.llm.contracts import ChatMessage, LLMProvider, ModelResponse
from gravity_ai.llm.providers import EchoLLMProvider
from gravity_ai.memory.store import MemoryQuery, MemoryStore
from gravity_ai.tools.registry import ToolRegistry


@dataclass
class AssistantResponse:
    message: str
    model: str
    tool_suggestions: list[str]
    memory_matches: list[dict[str, str]]

    def to_dict(self) -> dict[str, object]:
        return {
            "message": self.message,
            "model": self.model,
            "toolSuggestions": self.tool_suggestions,
            "memoryMatches": self.memory_matches,
        }


class GravityAssistant:
    def __init__(
        self,
        registry: ToolRegistry,
        memory: MemoryStore,
        llm: LLMProvider | None = None,
    ) -> None:
        self._registry = registry
        self._memory = memory
        self._llm = llm or EchoLLMProvider()

    def respond(self, content: str) -> AssistantResponse:
        trimmed = content.strip()
        if not trimmed:
            return AssistantResponse(
                message="Envie uma tarefa ou pergunta para o Gravity AI.",
                model=self._llm.name,
                tool_suggestions=[],
                memory_matches=[],
            )

        suggestions = self._suggest_tools(trimmed)
        memories = self._memory.search(MemoryQuery(text=trimmed, limit=3))
        try:
            model_response: ModelResponse = self._llm.generate(
                [
                    ChatMessage(
                        role="system",
                        content=(
                            "You are Gravity AI, a Windows desktop assistant. "
                            "Answer naturally in the user's language. Be direct, useful, "
                            "and honest about which actions still require tools or confirmation."
                        ),
                    ),
                    ChatMessage(role="user", content=trimmed),
                ]
            )
        except Exception as exc:  # noqa: BLE001 - provider failures should not crash the API
            model_response = ModelResponse(
                content=f"Nao consegui consultar o modelo real agora: {exc}",
                model=self._llm.name,
                provider="error",
                usage={},
            )

        if suggestions:
            suffix = " Ferramentas candidatas: " + ", ".join(suggestions) + "."
        elif model_response.provider == "local":
            suffix = (
                " Configure GEMINI_API_KEY, GOOGLE_API_KEY ou OPENAI_API_KEY "
                "para ativar respostas reais pela API."
            )
        else:
            suffix = ""

        return AssistantResponse(
            message=f"{model_response.content}{suffix}",
            model=model_response.model,
            tool_suggestions=suggestions,
            memory_matches=[
                {"scope": item.scope.value, "key": item.key, "value": item.value}
                for item in memories
            ],
        )

    def _suggest_tools(self, content: str) -> list[str]:
        lowered = content.lower()
        candidates: list[str] = []
        if any(word in lowered for word in ("arquivo", "pasta", "downloads", "pdf")):
            candidates.extend(["file.search", "file.list"])
        if any(word in lowered for word in ("abrir", "executar", "programa", "vscode", "spotify")):
            candidates.append("program.open")
        available = {definition.name for definition in self._registry.list_definitions()}
        return [name for name in candidates if name in available]
