from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from gravity_ai.llm.contracts import ChatMessage, ModelResponse


class EchoLLMProvider:
    @property
    def name(self) -> str:
        return "gravity-local-echo"

    def generate(self, messages: list[ChatMessage]) -> ModelResponse:
        user_message = next((message.content for message in reversed(messages) if message.role == "user"), "")
        content = (
            "Recebi sua solicitacao e montei uma resposta local de fundacao: "
            f"{user_message}"
        )
        return ModelResponse(
            content=content,
            model=self.name,
            provider="local",
            usage={"promptMessages": len(messages), "completionTokens": len(content.split())},
        )


@dataclass(frozen=True)
class GeminiProviderConfig:
    api_key: str
    model: str = "gemini-3.5-flash"
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    timeout_seconds: int = 60
    temperature: float | None = None
    max_output_tokens: int | None = None
    store: bool = False


@dataclass(frozen=True)
class OpenAIProviderConfig:
    api_key: str
    model: str = "gpt-5.6-terra"
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: int = 60
    reasoning_effort: str = "low"
    store: bool = False


class GeminiGenerateContentProvider:
    def __init__(self, config: GeminiProviderConfig) -> None:
        self._config = config

    @property
    def name(self) -> str:
        return self._config.model

    def generate(self, messages: list[ChatMessage]) -> ModelResponse:
        instructions = "\n\n".join(message.content for message in messages if message.role == "system")
        payload: dict[str, Any] = {
            "contents": _gemini_contents(messages),
            "systemInstruction": {"parts": [{"text": instructions or _default_instructions()}]},
            "store": self._config.store,
        }

        generation_config: dict[str, Any] = {}
        if self._config.temperature is not None:
            generation_config["temperature"] = self._config.temperature
        if self._config.max_output_tokens is not None:
            generation_config["maxOutputTokens"] = self._config.max_output_tokens
        if generation_config:
            payload["generationConfig"] = generation_config

        response = self._post_json(payload)
        return ModelResponse(
            content=_extract_gemini_text(response),
            model=self._config.model,
            provider="gemini",
            usage=_extract_gemini_usage(response),
        )

    def _post_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        model_path = self._config.model
        if not model_path.startswith("models/"):
            model_path = f"models/{model_path}"
        encoded_model = urllib.parse.quote(model_path, safe="/")
        encoded_key = urllib.parse.quote(self._config.api_key, safe="")
        url = f"{self._config.base_url.rstrip('/')}/{encoded_model}:generateContent?key={encoded_key}"
        request = urllib.request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self._config.timeout_seconds) as response:
                decoded = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Gemini API error {exc.code}: {details}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach Gemini API: {exc.reason}") from exc

        parsed = json.loads(decoded)
        if not isinstance(parsed, dict):
            raise RuntimeError("Gemini API returned an unexpected response.")
        return parsed


class OpenAIResponsesProvider:
    def __init__(self, config: OpenAIProviderConfig) -> None:
        self._config = config

    @property
    def name(self) -> str:
        return self._config.model

    def generate(self, messages: list[ChatMessage]) -> ModelResponse:
        instructions = "\n\n".join(message.content for message in messages if message.role == "system")
        input_messages = [
            {"role": message.role, "content": message.content}
            for message in messages
            if message.role != "system"
        ]
        payload: dict[str, Any] = {
            "model": self._config.model,
            "instructions": instructions or _default_instructions(),
            "input": input_messages,
            "store": self._config.store,
        }

        if self._config.model.startswith("gpt-5"):
            payload["reasoning"] = {"effort": self._config.reasoning_effort}

        response = self._post_json("/responses", payload)
        content = _extract_output_text(response)
        usage = _extract_usage(response)
        return ModelResponse(
            content=content,
            model=str(response.get("model") or self._config.model),
            provider="openai",
            usage=usage,
        )

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._config.base_url.rstrip('/')}{path}"
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url=url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._config.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self._config.timeout_seconds) as response:
                decoded = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI API error {exc.code}: {details}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach OpenAI API: {exc.reason}") from exc

        parsed = json.loads(decoded)
        if not isinstance(parsed, dict):
            raise RuntimeError("OpenAI API returned an unexpected response.")
        return parsed


def build_llm_provider_from_env() -> EchoLLMProvider | GeminiGenerateContentProvider | OpenAIResponsesProvider:
    provider = os.environ.get("GRAVITY_AI_LLM_PROVIDER", "auto").strip().lower()
    gemini_key = (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
    )
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if provider == "local":
        return EchoLLMProvider()

    if provider in {"gemini", "google", "auto"} and gemini_key:
        return GeminiGenerateContentProvider(
            GeminiProviderConfig(
                api_key=gemini_key,
                model=os.environ.get("GRAVITY_AI_GEMINI_MODEL")
                or os.environ.get("GEMINI_MODEL")
                or "gemini-3.5-flash",
                base_url=os.environ.get(
                    "GEMINI_BASE_URL",
                    "https://generativelanguage.googleapis.com/v1beta",
                ),
                temperature=_optional_float(os.environ.get("GRAVITY_AI_TEMPERATURE")),
                max_output_tokens=_optional_int(os.environ.get("GRAVITY_AI_MAX_OUTPUT_TOKENS")),
                store=os.environ.get("GRAVITY_AI_GEMINI_STORE", "false").lower() == "true",
            )
        )

    if provider in {"openai", "auto"} and openai_key:
        return OpenAIResponsesProvider(
            OpenAIProviderConfig(
                api_key=openai_key,
                model=os.environ.get("GRAVITY_AI_OPENAI_MODEL")
                or os.environ.get("OPENAI_MODEL")
                or "gpt-5.6-terra",
                base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                reasoning_effort=os.environ.get("GRAVITY_AI_REASONING_EFFORT", "low"),
                store=os.environ.get("GRAVITY_AI_OPENAI_STORE", "false").lower() == "true",
            )
        )
    return EchoLLMProvider()


def _default_instructions() -> str:
    return (
        "You are Gravity AI, a Windows desktop assistant. Answer naturally in the "
        "user's language. Be clear about what you can do now. Do not claim that an "
        "action was executed unless a tool result proves it. Destructive actions "
        "require explicit confirmation."
    )


def _extract_output_text(response: dict[str, Any]) -> str:
    direct = response.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct

    chunks: list[str] = []
    output = response.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                text = part.get("text")
                if isinstance(text, str):
                    chunks.append(text)

    content = "".join(chunks).strip()
    if not content:
        raise RuntimeError("OpenAI API response did not include output text.")
    return content


def _extract_usage(response: dict[str, Any]) -> dict[str, int]:
    usage = response.get("usage")
    if not isinstance(usage, dict):
        return {}
    result: dict[str, int] = {}
    for key, value in usage.items():
        if isinstance(value, int):
            result[key] = value
    return result


def _gemini_contents(messages: list[ChatMessage]) -> list[dict[str, Any]]:
    contents: list[dict[str, Any]] = []
    for message in messages:
        if message.role == "system":
            continue
        role = "model" if message.role == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": message.content}]})
    if not contents:
        contents.append({"role": "user", "parts": [{"text": ""}]})
    return contents


def _extract_gemini_text(response: dict[str, Any]) -> str:
    chunks: list[str] = []
    candidates = response.get("candidates")
    if isinstance(candidates, list):
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            content = candidate.get("content")
            if not isinstance(content, dict):
                continue
            parts = content.get("parts")
            if not isinstance(parts, list):
                continue
            for part in parts:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    chunks.append(part["text"])

    content = "".join(chunks).strip()
    if content:
        return content

    finish_reason = None
    if isinstance(candidates, list) and candidates and isinstance(candidates[0], dict):
        finish_reason = candidates[0].get("finishReason")
    raise RuntimeError(f"Gemini API response did not include text. finishReason={finish_reason}")


def _extract_gemini_usage(response: dict[str, Any]) -> dict[str, int]:
    usage = response.get("usageMetadata")
    if not isinstance(usage, dict):
        return {}
    return {key: value for key, value in usage.items() if isinstance(value, int)}


def _optional_float(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    return float(value)


def _optional_int(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    return int(value)
