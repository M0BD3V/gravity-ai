from __future__ import annotations

import unittest
from unittest.mock import patch

from gravity_ai.llm import (
    ChatMessage,
    EchoLLMProvider,
    GeminiGenerateContentProvider,
    GeminiProviderConfig,
    OpenAIProviderConfig,
    OpenAIResponsesProvider,
    build_llm_provider_from_env,
)


class LLMContractTests(unittest.TestCase):
    def test_echo_provider_returns_model_response(self) -> None:
        provider = EchoLLMProvider()

        response = provider.generate([ChatMessage(role="user", content="Abra o VS Code.")])

        self.assertEqual(response.provider, "local")
        self.assertEqual(response.model, provider.name)
        self.assertIn("Abra o VS Code", response.content)

    def test_openai_provider_parses_responses_output_text(self) -> None:
        provider = OpenAIResponsesProvider(
            OpenAIProviderConfig(api_key="test-key", model="gpt-5.6-terra")
        )

        with patch.object(
            provider,
            "_post_json",
            return_value={
                "model": "gpt-5.6-terra",
                "output_text": "Resposta real simulada.",
                "usage": {"input_tokens": 10, "output_tokens": 4},
            },
        ):
            response = provider.generate([ChatMessage(role="user", content="Ola")])

        self.assertEqual(response.provider, "openai")
        self.assertEqual(response.content, "Resposta real simulada.")
        self.assertEqual(response.usage["input_tokens"], 10)

    def test_gemini_provider_parses_generate_content_response(self) -> None:
        provider = GeminiGenerateContentProvider(
            GeminiProviderConfig(api_key="test-key", model="gemini-3.5-flash")
        )

        with patch.object(
            provider,
            "_post_json",
            return_value={
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": "Resposta Gemini simulada."}],
                            "role": "model",
                        },
                        "finishReason": "STOP",
                    }
                ],
                "usageMetadata": {
                    "promptTokenCount": 8,
                    "candidatesTokenCount": 4,
                    "totalTokenCount": 12,
                },
            },
        ):
            response = provider.generate([ChatMessage(role="user", content="Ola")])

        self.assertEqual(response.provider, "gemini")
        self.assertEqual(response.content, "Resposta Gemini simulada.")
        self.assertEqual(response.usage["totalTokenCount"], 12)

    @patch.dict("os.environ", {"GRAVITY_AI_LLM_PROVIDER": "local"}, clear=True)
    def test_provider_factory_can_force_local(self) -> None:
        provider = build_llm_provider_from_env()

        self.assertIsInstance(provider, EchoLLMProvider)

    @patch.dict(
        "os.environ",
        {"GRAVITY_AI_LLM_PROVIDER": "auto", "OPENAI_API_KEY": "test-key"},
        clear=True,
    )
    def test_provider_factory_uses_openai_when_key_exists(self) -> None:
        provider = build_llm_provider_from_env()

        self.assertIsInstance(provider, OpenAIResponsesProvider)

    @patch.dict(
        "os.environ",
        {"GRAVITY_AI_LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "test-key"},
        clear=True,
    )
    def test_provider_factory_uses_gemini_when_configured(self) -> None:
        provider = build_llm_provider_from_env()

        self.assertIsInstance(provider, GeminiGenerateContentProvider)

    @patch.dict(
        "os.environ",
        {
            "GRAVITY_AI_LLM_PROVIDER": "auto",
            "GEMINI_API_KEY": "test-key",
            "OPENAI_API_KEY": "openai-key",
        },
        clear=True,
    )
    def test_provider_factory_prefers_gemini_in_auto(self) -> None:
        provider = build_llm_provider_from_env()

        self.assertIsInstance(provider, GeminiGenerateContentProvider)


if __name__ == "__main__":
    unittest.main()
