import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.database import init_db
from app.handlers import build_admin_review_notification_text, get_reply_text, route_update


class HandlerTests(unittest.TestCase):
    ENV_KEYS = (
        "BALE_BOT_TOKEN",
        "BALE_API_BASE_URL",
        "BALE_ENABLE_SENDING",
        "DATABASE_PATH",
        "BALE_REPLY_TEXT",
        "BALE_WEBHOOK_SECRET",
        "BALE_STORE_RAW_UPDATES",
        "BALE_ADMIN_CHAT_ID",
        "BALE_ENABLE_ADMIN_NOTIFICATIONS",
    )

    def _route_text_message(self, text: str, env_overrides: dict[str, str] | None = None) -> dict:
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
                if env_overrides:
                    for key, value in env_overrides.items():
                        os.environ[key] = value

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
        self.assertIn("نام دارو", result["reply_result"]["text"])
        self.assertIn("داروساز", result["reply_result"]["text"])
        self.assertEqual(row, ("demo-chat", "123", "Hello pharmacy"))

    def test_normal_text_returns_safe_intake_reply(self):
        result = self._route_text_message("I need help with a medicine question")

        reply_text = result["reply_result"]["text"]
        self.assertIn("نام دارو", reply_text)
        self.assertIn("سن بیمار", reply_text)
        self.assertIn("پرسش اصلی", reply_text)
        self.assertIn("داروساز", reply_text)
        self.assertNotIn("take", reply_text.lower())

    def test_high_risk_text_returns_escalation_reply(self):
        result = self._route_text_message("Can I change medication dosage while pregnant?")

        reply_text = result["reply_result"]["text"]
        self.assertIn("بررسی داروساز", reply_text)
        self.assertIn("تشخیص", reply_text)
        self.assertIn("دوز", reply_text)
        self.assertIn("اورژانس", reply_text)
        self.assertNotIn("take", reply_text.lower())
        self.assertNotIn("start medication", reply_text.lower())

    def test_allergy_text_returns_escalation_reply(self):
        result = self._route_text_message("I have an allergy to this medicine")

        reply_text = result["reply_result"]["text"]
        self.assertIn("بررسی داروساز", reply_text)
        self.assertIn("حساسیت", reply_text)

    def test_pregnancy_text_returns_escalation_reply(self):
        result = self._route_text_message("Can I use this during pregnancy?")

        reply_text = result["reply_result"]["text"]
        self.assertIn("بررسی داروساز", reply_text)
        self.assertIn("بارداری", reply_text)

    def test_persian_high_risk_text_returns_escalation_reply(self):
        result = self._route_text_message("در بارداری برای کودک با این دارو حساسیت دارم")

        reply_text = result["reply_result"]["text"]
        self.assertIn("بررسی داروساز", reply_text)
        self.assertIn("بارداری", reply_text)

    def test_normal_text_stores_no_review_required(self):
        result, row = self._route_text_message_and_fetch_review_row(
            "I need help with a medicine question"
        )

        self.assertTrue(result["ok"])
        self.assertEqual(row, (0, None, "not_required"))

    def test_escalation_text_stores_pending_review_metadata(self):
        result, row = self._route_text_message_and_fetch_review_row(
            "Can I use this during pregnancy?"
        )

        self.assertTrue(result["ok"])
        self.assertEqual(row, (1, "pharmacist_review_required", "pending"))

    def test_controlled_substance_mentions_are_stored_for_pharmacist_review(self):
        messages = [
            "I want Valium",
            "I take clonazepam",
            "استامینوفن کدئین می‌خواهم",
            "/help I want Valium",
            "/rare valium",
        ]
        for message in messages:
            with self.subTest(message=message):
                result, row = self._route_text_message_and_fetch_review_row(message)
                self.assertTrue(result["ok"])
                self.assertEqual(
                    row,
                    (1, "pharmacist_review_required", "pending"),
                )

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
                        for row in connection.execute(
                            "PRAGMA table_info(incoming_messages)"
                        ).fetchall()
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
                    count = connection.execute("SELECT COUNT(*) FROM incoming_messages").fetchone()[
                        0
                    ]
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

    def test_new_and_duplicate_messages_make_no_network_requests(self):
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
                    "update_id": 988,
                    "message": {
                        "message_id": 124,
                        "chat": {"id": "demo-chat"},
                        "text": "Hello pharmacy",
                    },
                }
                with patch("urllib.request.urlopen") as urlopen:
                    first_result = route_update(payload)
                    duplicate_result = route_update(payload)

                request_count = urlopen.call_count
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
        self.assertEqual(request_count, 0)

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
                    count = connection.execute("SELECT COUNT(*) FROM incoming_messages").fetchone()[
                        0
                    ]
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
                    count = connection.execute("SELECT COUNT(*) FROM incoming_messages").fetchone()[
                        0
                    ]
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
                    raw_update = connection.execute(
                        "SELECT raw_update FROM incoming_messages"
                    ).fetchone()[0]
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
                    raw_update = connection.execute(
                        "SELECT raw_update FROM incoming_messages"
                    ).fetchone()[0]
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

        reply_text = result["reply_result"]["text"]
        self.assertIn("دستیار دریافت پیام داروخانه", reply_text)
        self.assertIn("جایگزین نظر داروساز یا پزشک نیست", reply_text)
        self.assertIn("داروساز", reply_text)

    def test_help_command_lists_available_commands(self):
        result = self._route_text_message("/help")

        reply_text = result["reply_result"]["text"]
        self.assertIn("دستورهای قابل استفاده", reply_text)
        self.assertIn("/start", reply_text)
        self.assertIn("/help", reply_text)
        self.assertIn("/status", reply_text)

    def test_status_command_confirms_bot_is_running(self):
        result = self._route_text_message("/status")

        reply_text = result["reply_result"]["text"]
        self.assertIn("ربات فعال است", reply_text)
        self.assertIn("ارسال پیام واقعی خاموش است", reply_text)
        self.assertIn("حالت آزمایشی", reply_text)
        self.assertNotIn("test-token", reply_text)
        self.assertNotIn("test-secret", reply_text)
        self.assertNotIn("demo-chat", reply_text)
        self.assertNotIn("BALE_BOT_TOKEN", reply_text)
        self.assertNotIn("BALE_WEBHOOK_SECRET", reply_text)

    def test_status_command_reports_when_sending_is_enabled(self):
        reply_text = get_reply_text("/status", "fallback", bale_enable_sending=True)

        self.assertIn("ربات فعال است", reply_text)
        self.assertIn("ارسال پیام واقعی روشن است", reply_text)
        self.assertIn("ممکن است پاسخ واقعی در بله ارسال شود", reply_text)
        self.assertNotIn("test-token", reply_text)
        self.assertNotIn("test-secret", reply_text)
        self.assertNotIn("BALE_BOT_TOKEN", reply_text)
        self.assertNotIn("BALE_WEBHOOK_SECRET", reply_text)

    def test_unknown_text_uses_safe_intake_reply(self):
        result = self._route_text_message("Hello pharmacy")

        reply_text = result["reply_result"]["text"]
        self.assertIn("نام دارو", reply_text)
        self.assertIn("داروساز", reply_text)

    def test_persian_reply_text_is_preserved_as_unicode(self):
        result = self._route_text_message("برای مصرف دارو سوال دارم")

        reply_text = result["reply_result"]["text"]
        self.assertIn("پیام شما دریافت شد", reply_text)
        self.assertIn("نام دارو", reply_text)
        self.assertIn("؟", reply_text)

    def test_review_needed_message_prepares_skipped_admin_notification_metadata(self):
        result = self._route_text_message("Can I use this medicine during pregnancy?")

        self.assertTrue(result["admin_notification_prepared"])
        notification = result["admin_notification_result"]
        self.assertTrue(notification["skipped"])
        self.assertEqual(notification["reason"], "Admin notifications are disabled.")
        self.assertEqual(notification["stored_message_id"], result["stored_message_id"])
        self.assertEqual(notification["review_reason"], "pharmacist_review_required")
        self.assertNotIn("text", notification)

    def test_normal_message_does_not_prepare_admin_notification(self):
        result = self._route_text_message("I need help with a medicine question")

        self.assertFalse(result["admin_notification_prepared"])
        self.assertIsNone(result["admin_notification_result"])

    def test_duplicate_delivery_does_not_prepare_duplicate_admin_notification(self):
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
                            "BALE_ENABLE_ADMIN_NOTIFICATIONS=true",
                            "BALE_ADMIN_CHAT_ID=admin-chat",
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
                        "text": "Can I use this medicine during pregnancy?",
                    },
                }
                first_result = route_update(payload)
                duplicate_result = route_update(payload)
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

        self.assertTrue(first_result["admin_notification_prepared"])
        self.assertFalse(duplicate_result["admin_notification_prepared"])
        self.assertIsNone(duplicate_result["admin_notification_result"])

    def test_missing_admin_chat_id_skips_admin_notification_without_crashing(self):
        result = self._route_text_message(
            "Can I use this medicine during pregnancy?",
            env_overrides={"BALE_ENABLE_ADMIN_NOTIFICATIONS": "true"},
        )

        self.assertTrue(result["admin_notification_prepared"])
        notification = result["admin_notification_result"]
        self.assertTrue(notification["skipped"])
        self.assertEqual(notification["reason"], "BALE_ADMIN_CHAT_ID is not configured.")

    def test_admin_notification_text_does_not_include_secrets_or_full_patient_text(self):
        message_text = (
            "Can I use this medicine during pregnancy? "
            "test-token test-secret demo-chat private patient details should not all appear"
        )
        notification_text = build_admin_review_notification_text(
            stored_message_id=123,
            review_reason="pharmacist_review_required",
            message_text=message_text,
            settings=type(
                "SettingsStub",
                (),
                {
                    "bale_bot_token": "test-token",
                    "bale_webhook_secret": "test-secret",
                    "bale_admin_chat_id": "admin-chat",
                },
            )(),
            chat_id="demo-chat",
        )
        self.assertIn("stored_message_id=", notification_text)
        self.assertIn("review_reason=pharmacist_review_required", notification_text)
        self.assertNotIn("test-token", notification_text)
        self.assertNotIn("test-secret", notification_text)
        self.assertNotIn("demo-chat", notification_text)
        self.assertNotIn("private patient details should not all appear", notification_text)

    def test_admin_notification_text_preview_does_not_return_full_short_message(self):
        notification_text = build_admin_review_notification_text(
            stored_message_id=123,
            review_reason="pharmacist_review_required",
            message_text="Can I use this during pregnancy?",
            settings=type(
                "SettingsStub",
                (),
                {
                    "bale_bot_token": "test-token",
                    "bale_webhook_secret": "test-secret",
                    "bale_admin_chat_id": "admin-chat",
                },
            )(),
            chat_id="demo-chat",
        )

        self.assertIn("text_preview=[redacted message:", notification_text)
        self.assertNotIn("Can I use this during pregnancy?", notification_text)

    def test_enabled_admin_notification_sends_when_sending_is_enabled(self):
        sent_messages = []

        class FakeBaleClient:
            def __init__(self, settings):
                self.settings = settings

            def send_message(self, chat_id, text, reply_to_message_id=None):
                sent_messages.append(
                    {
                        "chat_id": chat_id,
                        "text": text,
                        "reply_to_message_id": reply_to_message_id,
                    }
                )
                return {"ok": True, "result": {"message_id": 456}}

        with patch("app.handlers.BaleClient", FakeBaleClient):
            result = self._route_text_message(
                "Can I use this medicine during pregnancy?",
                env_overrides={
                    "BALE_ENABLE_SENDING": "true",
                    "BALE_ENABLE_ADMIN_NOTIFICATIONS": "true",
                    "BALE_ADMIN_CHAT_ID": "admin-chat",
                },
            )

        self.assertTrue(result["admin_notification_prepared"])
        self.assertFalse(result["admin_notification_result"]["skipped"])
        self.assertEqual(len(sent_messages), 2)
        self.assertEqual(sent_messages[1]["chat_id"], "admin-chat")
        self.assertIn("/local/reviews/pending", sent_messages[1]["text"])


if __name__ == "__main__":
    unittest.main()
