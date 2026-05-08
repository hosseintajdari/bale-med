import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.database import init_db
from app.handlers import get_reply_text, route_update


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

    def _route_text_message_and_fetch_review_row(self, text: str) -> tuple[dict, tuple]:
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
                            "text": text,
                        }
                    }
                )

                connection = sqlite3.connect("test.db")
                try:
                    row = connection.execute(
                        """
                        SELECT needs_review, review_reason, review_status
                        FROM incoming_messages
                        """
                    ).fetchone()
                finally:
                    connection.close()

                return result, row
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

    def test_allergy_text_returns_escalation_reply(self):
        result = self._route_text_message("I have an allergy to this medicine")

        reply_text = result["reply_result"]["text"]
        self.assertIn("pharmacist review", reply_text)
        self.assertIn("cannot give diagnosis", reply_text)

    def test_pregnancy_text_returns_escalation_reply(self):
        result = self._route_text_message("Can I use this during pregnancy?")

        reply_text = result["reply_result"]["text"]
        self.assertIn("pharmacist review", reply_text)
        self.assertIn("cannot give diagnosis", reply_text)

    def test_normal_text_stores_no_review_required(self):
        result, row = self._route_text_message_and_fetch_review_row("I need help with a medicine question")

        self.assertTrue(result["ok"])
        self.assertEqual(row, (0, None, "not_required"))

    def test_escalation_text_stores_pending_review_metadata(self):
        result, row = self._route_text_message_and_fetch_review_row("Can I use this during pregnancy?")

        self.assertTrue(result["ok"])
        self.assertEqual(row, (1, "pharmacist_review_required", "pending"))

    def test_command_text_stores_no_review_required(self):
        result, row = self._route_text_message_and_fetch_review_row("/status")

        self.assertTrue(result["ok"])
        self.assertEqual(row, (0, None, "not_required"))

    def test_route_update_logs_sanitized_webhook_and_reply_audit_events(self):
        message_text = "private patient text with test-token test-secret demo-chat"

        with self.assertLogs("app.handlers", level="INFO") as captured:
            result = self._route_text_message(message_text)

        self.assertTrue(result["ok"])
        log_output = "\n".join(captured.output)
        self.assertIn("webhook_update_received", log_output)
        self.assertIn("reply_prepared", log_output)
        self.assertIn("stored_message_id=", log_output)
        self.assertIn("has_text=True", log_output)
        self.assertIn("text_length=", log_output)
        self.assertIn("review_status=not_required", log_output)
        self.assertIn("sending_enabled=False", log_output)
        self.assertNotIn(message_text, log_output)
        self.assertNotIn("test-token", log_output)
        self.assertNotIn("test-secret", log_output)
        self.assertNotIn("demo-chat", log_output)

    def test_fresh_database_has_review_metadata_columns(self):
        original_cwd = Path.cwd()
        original_values = {key: os.environ.get(key) for key in self.ENV_KEYS}

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                for key in original_values:
                    os.environ.pop(key, None)

                os.environ["BALE_BOT_TOKEN"] = "test-token"
                os.environ["BALE_API_BASE_URL"] = "https://example.test"
                os.environ["BALE_ENABLE_SENDING"] = "false"
                os.environ["DATABASE_PATH"] = "test.db"
                os.environ["BALE_WEBHOOK_SECRET"] = "test-secret"

                init_db()

                connection = sqlite3.connect("test.db")
                try:
                    columns = {
                        row[1]
                        for row in connection.execute("PRAGMA table_info(incoming_messages)").fetchall()
                    }
                finally:
                    connection.close()
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

        self.assertIn("needs_review", columns)
        self.assertIn("review_reason", columns)
        self.assertIn("review_status", columns)
        self.assertIn("external_event_id", columns)

    def test_duplicate_delivery_with_same_stable_identifier_is_not_inserted_twice(self):
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
                payload = {
                    "update_id": 987,
                    "message": {
                        "message_id": 123,
                        "chat": {"id": "demo-chat"},
                        "text": "Hello pharmacy",
                    },
                }
                first_result = route_update(payload)
                duplicate_result = route_update(payload)

                connection = sqlite3.connect("test.db")
                try:
                    count = connection.execute("SELECT COUNT(*) FROM incoming_messages").fetchone()[0]
                    row = connection.execute(
                        "SELECT external_event_id FROM incoming_messages"
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

        self.assertTrue(first_result["ok"])
        self.assertTrue(first_result["message_inserted"])
        self.assertFalse(first_result["duplicate_delivery"])
        self.assertTrue(first_result["reply_prepared"])
        self.assertTrue(duplicate_result["ok"])
        self.assertFalse(duplicate_result["message_inserted"])
        self.assertTrue(duplicate_result["duplicate_delivery"])
        self.assertFalse(duplicate_result["reply_prepared"])
        self.assertEqual(first_result["stored_message_id"], duplicate_result["stored_message_id"])
        self.assertEqual(count, 1)
        self.assertEqual(row, ("update:987",))

    def test_duplicate_delivery_uses_chat_and_message_id_when_update_id_is_missing(self):
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
                payload = {
                    "message": {
                        "message_id": 123,
                        "chat": {"id": "demo-chat"},
                        "text": "Hello pharmacy",
                    },
                }
                first_result = route_update(payload)
                duplicate_result = route_update(payload)

                connection = sqlite3.connect("test.db")
                try:
                    count = connection.execute("SELECT COUNT(*) FROM incoming_messages").fetchone()[0]
                    row = connection.execute(
                        "SELECT external_event_id FROM incoming_messages"
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

        self.assertTrue(first_result["message_inserted"])
        self.assertFalse(first_result["duplicate_delivery"])
        self.assertFalse(duplicate_result["message_inserted"])
        self.assertTrue(duplicate_result["duplicate_delivery"])
        self.assertEqual(first_result["stored_message_id"], duplicate_result["stored_message_id"])
        self.assertEqual(count, 1)
        self.assertEqual(row, ("message:demo-chat:123",))

    def test_repeated_message_without_stable_identifier_is_still_stored(self):
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
                payload = {
                    "message": {
                        "chat": {"id": "demo-chat"},
                        "text": "Hello pharmacy",
                    },
                }
                first_result = route_update(payload)
                second_result = route_update(payload)

                connection = sqlite3.connect("test.db")
                try:
                    count = connection.execute("SELECT COUNT(*) FROM incoming_messages").fetchone()[0]
                    external_ids = connection.execute(
                        "SELECT external_event_id FROM incoming_messages ORDER BY id"
                    ).fetchall()
                finally:
                    connection.close()
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

        self.assertTrue(first_result["message_inserted"])
        self.assertFalse(first_result["duplicate_delivery"])
        self.assertTrue(second_result["message_inserted"])
        self.assertFalse(second_result["duplicate_delivery"])
        self.assertEqual(count, 2)
        self.assertEqual(external_ids, [(None,), (None,)])

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

        reply_text = result["reply_result"]["text"]
        self.assertIn("Bot is running", reply_text)
        self.assertIn("sending is OFF", reply_text)
        self.assertIn("dry-run mode", reply_text)
        self.assertNotIn("test-token", reply_text)
        self.assertNotIn("test-secret", reply_text)

    def test_status_command_reports_when_sending_is_enabled(self):
        reply_text = get_reply_text("/status", "fallback", bale_enable_sending=True)

        self.assertIn("Bot is running", reply_text)
        self.assertIn("sending is ON", reply_text)
        self.assertIn("real Bale replies may be sent", reply_text)
        self.assertNotIn("test-token", reply_text)
        self.assertNotIn("test-secret", reply_text)

    def test_unknown_text_uses_safe_intake_reply(self):
        result = self._route_text_message("Hello pharmacy")

        reply_text = result["reply_result"]["text"]
        self.assertIn("medicine name", reply_text)
        self.assertIn("pharmacist", reply_text)


if __name__ == "__main__":
    unittest.main()
