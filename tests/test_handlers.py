import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.database import init_db
from app.handlers import route_update


class HandlerTests(unittest.TestCase):
    ENV_KEYS = (
        "BALE_BOT_TOKEN",
        "BALE_API_BASE_URL",
        "BALE_ENABLE_SENDING",
        "DATABASE_PATH",
        "BALE_REPLY_TEXT",
        "BALE_WEBHOOK_SECRET",
        "BALE_STORE_RAW_UPDATES",
    )

    def _route_text_message(self, text: str) -> dict:
        original_cwd = Path.cwd()
        original_values = {key: os.environ.get(key) for key in self.ENV_KEYS}

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
                            "BALE_ENABLE_SENDING=false",
                            "DATABASE_PATH=test.db",
                            "BALE_REPLY_TEXT=سلام حسین جان!",
                            "BALE_WEBHOOK_SECRET=test-secret",
                        ]
                    ),
                    encoding="utf-8",
                )

                init_db()
                return route_update(
                    {
                        "message": {
                            "message_id": 123,
                            "chat": {"id": "demo-chat"},
                            "text": text,
                        }
                    }
                )
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    def test_route_update_stores_message_and_prepares_dry_run_reply(self):
        original_cwd = Path.cwd()
        original_values = {key: os.environ.get(key) for key in self.ENV_KEYS}

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
                            "BALE_ENABLE_SENDING=false",
                            "DATABASE_PATH=test.db",
                            "BALE_REPLY_TEXT=سلام حسین جان!",
                            "BALE_WEBHOOK_SECRET=test-secret",
                        ]
                    ),
                    encoding="utf-8",
                )

                init_db()
                result = route_update(
                    {
                        "message": {
                            "message_id": 123,
                            "chat": {"id": "demo-chat"},
                            "text": "Hello pharmacy",
                        }
                    }
                )

                connection = sqlite3.connect("test.db")
                try:
                    row = connection.execute(
                        "SELECT chat_id, message_id, text FROM incoming_messages"
                    ).fetchone()
                finally:
                    connection.close()
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

        self.assertTrue(result["ok"])
        self.assertTrue(result["reply_prepared"])
        self.assertTrue(result["reply_result"]["skipped"])
        self.assertIn("medicine name", result["reply_result"]["text"])
        self.assertIn("pharmacist", result["reply_result"]["text"])
        self.assertEqual(row, ("demo-chat", "123", "Hello pharmacy"))

    def test_normal_text_returns_safe_intake_reply(self):
        result = self._route_text_message("I need help with a medicine question")

        reply_text = result["reply_result"]["text"]
        self.assertIn("medicine name", reply_text)
        self.assertIn("patient age range", reply_text)
        self.assertIn("pharmacist", reply_text)
        self.assertNotIn("take", reply_text.lower())

    def test_high_risk_text_returns_escalation_reply(self):
        result = self._route_text_message("Can I change medication dosage while pregnant?")

        reply_text = result["reply_result"]["text"]
        self.assertIn("pharmacist review", reply_text)
        self.assertIn("cannot give diagnosis", reply_text)
        self.assertIn("dosage", reply_text)

    def test_raw_update_storage_is_disabled_by_default(self):
        original_cwd = Path.cwd()
        original_values = {key: os.environ.get(key) for key in self.ENV_KEYS}

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
                            "BALE_ENABLE_SENDING=false",
                            "DATABASE_PATH=test.db",
                            "BALE_REPLY_TEXT=سلام حسین جان!",
                            "BALE_WEBHOOK_SECRET=test-secret",
                        ]
                    ),
                    encoding="utf-8",
                )

                init_db()
                route_update(
                    {
                        "message": {
                            "message_id": 123,
                            "chat": {"id": "demo-chat"},
                            "text": "private patient text",
                        },
                        "debug_extra": "should not be stored raw by default",
                    }
                )

                connection = sqlite3.connect("test.db")
                try:
                    raw_update = connection.execute("SELECT raw_update FROM incoming_messages").fetchone()[0]
                finally:
                    connection.close()
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

        self.assertEqual(json.loads(raw_update), {"raw_update_storage": "disabled"})

    def test_raw_update_storage_can_be_enabled_for_debugging(self):
        original_cwd = Path.cwd()
        original_values = {key: os.environ.get(key) for key in self.ENV_KEYS}

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
                            "BALE_ENABLE_SENDING=false",
                            "DATABASE_PATH=test.db",
                            "BALE_REPLY_TEXT=سلام حسین جان!",
                            "BALE_WEBHOOK_SECRET=test-secret",
                            "BALE_STORE_RAW_UPDATES=true",
                        ]
                    ),
                    encoding="utf-8",
                )

                init_db()
                route_update(
                    {
                        "message": {
                            "message_id": 123,
                            "chat": {"id": "demo-chat"},
                            "text": "Hello pharmacy",
                        },
                        "debug_extra": "stored only when explicitly enabled",
                    }
                )

                connection = sqlite3.connect("test.db")
                try:
                    raw_update = connection.execute("SELECT raw_update FROM incoming_messages").fetchone()[0]
                finally:
                    connection.close()
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

        stored_payload = json.loads(raw_update)
        self.assertEqual(stored_payload["message"]["text"], "Hello pharmacy")
        self.assertEqual(stored_payload["debug_extra"], "stored only when explicitly enabled")

    def test_start_command_returns_safe_introduction(self):
        result = self._route_text_message("/start")

        self.assertIn("pharmacy message intake assistant", result["reply_result"]["text"])
        self.assertIn("not a medical advisor", result["reply_result"]["text"])

    def test_help_command_lists_available_commands(self):
        result = self._route_text_message("/help")

        reply_text = result["reply_result"]["text"]
        self.assertIn("/start", reply_text)
        self.assertIn("/help", reply_text)
        self.assertIn("/status", reply_text)

    def test_status_command_confirms_bot_is_running(self):
        result = self._route_text_message("/status")

        self.assertEqual(result["reply_result"]["text"], "Bot is running and ready to receive pharmacy intake messages.")

    def test_unknown_text_uses_safe_intake_reply(self):
        result = self._route_text_message("Hello pharmacy")

        reply_text = result["reply_result"]["text"]
        self.assertIn("medicine name", reply_text)
        self.assertIn("pharmacist", reply_text)


if __name__ == "__main__":
    unittest.main()
