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
                "BALE_WEBHOOK_SECRET",
                "BALE_LOCAL_REVIEW_TOKEN",
                "BALE_ADMIN_CHAT_ID",
                "BALE_ENABLE_ADMIN_NOTIFICATIONS",
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
                            "BALE_WEBHOOK_SECRET=test-secret",
                            "BALE_LOCAL_REVIEW_TOKEN=review-token",
                            "BALE_ADMIN_CHAT_ID=admin-chat",
                            "BALE_ENABLE_ADMIN_NOTIFICATIONS=true",
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
        self.assertEqual(settings.bale_webhook_secret, "test-secret")
        self.assertEqual(settings.bale_local_review_token, "review-token")
        self.assertEqual(settings.bale_admin_chat_id, "admin-chat")
        self.assertTrue(settings.bale_enable_admin_notifications)
        self.assertFalse(settings.bale_enable_llm)
        self.assertEqual(settings.bale_llm_mode, "shadow")

    def test_get_settings_default_reply_text_is_persian_and_safe(self):
        original_cwd = Path.cwd()
        original_values = {
            key: os.environ.get(key)
            for key in (
                "BALE_BOT_TOKEN",
                "BALE_API_BASE_URL",
                "BALE_ENABLE_SENDING",
                "DATABASE_PATH",
                "BALE_REPLY_TEXT",
                "BALE_WEBHOOK_SECRET",
                "BALE_LOCAL_REVIEW_TOKEN",
                "BALE_ADMIN_CHAT_ID",
                "BALE_ENABLE_ADMIN_NOTIFICATIONS",
            )
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                for key in original_values:
                    os.environ.pop(key, None)

                settings = get_settings()
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

        self.assertIn("پیام شما دریافت شد", settings.bale_reply_text)
        self.assertIn("جایگزین نظر داروساز یا پزشک نیست", settings.bale_reply_text)
        self.assertIn("داروساز", settings.bale_reply_text)
        self.assertEqual(settings.bale_admin_chat_id, "")
        self.assertFalse(settings.bale_enable_admin_notifications)
        self.assertFalse(settings.bale_enable_llm)
        self.assertEqual(settings.bale_llm_mode, "shadow")


if __name__ == "__main__":
    unittest.main()
