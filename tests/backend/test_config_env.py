from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from gravity_ai.config import load_env_file


class EnvConfigTests(unittest.TestCase):
    def test_load_env_file_sets_missing_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            env_path.write_text(
                """
                # comment
                GRAVITY_AI_LLM_PROVIDER=gemini
                QUOTED_VALUE="hello world"
                """,
                encoding="utf-8",
            )

            old_provider = os.environ.pop("GRAVITY_AI_LLM_PROVIDER", None)
            old_quoted = os.environ.pop("QUOTED_VALUE", None)
            try:
                loaded = load_env_file(env_path)

                self.assertEqual(loaded["GRAVITY_AI_LLM_PROVIDER"], "gemini")
                self.assertEqual(os.environ["GRAVITY_AI_LLM_PROVIDER"], "gemini")
                self.assertEqual(os.environ["QUOTED_VALUE"], "hello world")
            finally:
                _restore_env("GRAVITY_AI_LLM_PROVIDER", old_provider)
                _restore_env("QUOTED_VALUE", old_quoted)


def _restore_env(key: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
