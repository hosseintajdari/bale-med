import os
import tempfile
import unittest
from pathlib import Path

from app.config import get_settings


class SettingsTests(unittest.TestCase):
    def test_get_settings_loads_values_from_local_env_file(self):
        original_cwd = Path.cwd()
        original_values = {
            key: os.environ.get(key)
            for key in (
                "BALE_BOT_TOKEN",
                "BALE_API_BASE_URL",
                "BALE_ENABLE_SENDING",
                "DATABASE_PATH",
                "BALE_REPLY_TEXT",
            )
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                for key in original_values:
                    os.environ.pop(key, None)

                Path(".env").write_text(
                    "\n".join(
                        [
                            "BALE_BOT_TOKEN=test-token",
                            "BALE_API_BASE_URL=https://example.test",
                            "BALE_ENABLE_SENDING=true",
                            "DATABASE_PATH=test.db",
                            "BALE_REPLY_TEXT=سلام حسین جان!",
                        ]
                    ),
                    encoding="utf-8",
                )

                settings = get_settings()
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

        self.assertEqual(settings.bale_bot_token, "test-token")
        self.assertEqual(settings.bale_api_base_url, "https://example.test")
        self.assertTrue(settings.bale_enable_sending)
        self.assertEqual(settings.database_path, "test.db")
        self.assertEqual(settings.bale_reply_text, "سلام حسین جان!")


if __name__ == "__main__":
    unittest.main()
