"""Milestone 8J — sending gate: real Bale replies only when BALE_ENABLE_SENDING=true."""

from __future__ import annotations

import importlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.database import init_db
from app.handlers import route_update
from fastapi.testclient import TestClient


class SendingGateTests(unittest.TestCase):
    ENV_KEYS = (
        "BALE_BOT_TOKEN",
        "BALE_API_BASE_URL",
        "BALE_ENABLE_SENDING",
        "DATABASE_PATH",
        "BALE_REPLY_TEXT",
        "BALE_WEBHOOK_SECRET",
        "BALE_STORE_RAW_UPDATES",
        "BALE_ENABLE_ADMIN_NOTIFICATIONS",
        "BALE_ADMIN_CHAT_ID",
    )

    def _route_normal_message(self, *, sending_enabled: bool) -> tuple[dict, list[dict]]:
        sent_messages: list[dict] = []

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
                            f"BALE_ENABLE_SENDING={'true' if sending_enabled else 'false'}",
                            "DATABASE_PATH=test.db",
                            "BALE_REPLY_TEXT=سلام حسین جان!",
                            "BALE_WEBHOOK_SECRET=test-secret",
                            "BALE_ENABLE_ADMIN_NOTIFICATIONS=false",
                        ]
                    ),
                    encoding="utf-8",
                )

                init_db()
                with patch("app.handlers.BaleClient", FakeBaleClient):
                    result = route_update(
                        {
                            "message": {
                                "message_id": 123,
                                "chat": {"id": "demo-chat"},
                                "text": "Hello pharmacy",
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

        return result, sent_messages

    def _route_escalation_message(
        self,
        *,
        sending_enabled: bool,
        admin_notifications_enabled: bool,
    ) -> tuple[dict, list[dict]]:
        sent_messages: list[dict] = []

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
                            f"BALE_ENABLE_SENDING={'true' if sending_enabled else 'false'}",
                            "DATABASE_PATH=test.db",
                            "BALE_REPLY_TEXT=سلام حسین جان!",
                            "BALE_WEBHOOK_SECRET=test-secret",
                            (
                                "BALE_ENABLE_ADMIN_NOTIFICATIONS="
                                f"{'true' if admin_notifications_enabled else 'false'}"
                            ),
                            "BALE_ADMIN_CHAT_ID=admin-chat",
                        ]
                    ),
                    encoding="utf-8",
                )

                init_db()
                with patch("app.handlers.BaleClient", FakeBaleClient):
                    result = route_update(
                        {
                            "message": {
                                "message_id": 123,
                                "chat": {"id": "demo-chat"},
                                "text": "Can I use this medicine during pregnancy?",
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

        return result, sent_messages

    def test_normal_message_sends_real_reply_when_sending_enabled(self) -> None:
        result, sent_messages = self._route_normal_message(sending_enabled=True)

        self.assertTrue(result["ok"])
        self.assertTrue(result["reply_prepared"])
        self.assertFalse(result["reply_result"].get("skipped"))
        self.assertTrue(result["reply_result"]["ok"])
        self.assertEqual(len(sent_messages), 1)
        self.assertEqual(sent_messages[0]["chat_id"], "demo-chat")
        self.assertIn("نام دارو", sent_messages[0]["text"])

    def test_normal_message_skips_bale_send_when_sending_disabled(self) -> None:
        result, sent_messages = self._route_normal_message(sending_enabled=False)

        self.assertTrue(result["ok"])
        self.assertTrue(result["reply_prepared"])
        self.assertTrue(result["reply_result"]["skipped"])
        self.assertEqual(
            result["reply_result"]["reason"],
            "Sending is disabled. Set BALE_ENABLE_SENDING=true to enable.",
        )
        self.assertEqual(len(sent_messages), 0)
        self.assertIn("نام دارو", result["reply_result"]["text"])

    def test_admin_notification_requires_sending_gate_even_when_admin_flag_is_on(self) -> None:
        result, sent_messages = self._route_escalation_message(
            sending_enabled=False,
            admin_notifications_enabled=True,
        )

        self.assertTrue(result["admin_notification_prepared"])
        notification = result["admin_notification_result"]
        self.assertTrue(notification["skipped"])
        self.assertEqual(
            notification["reason"],
            "Admin notifications require BALE_ENABLE_SENDING=true.",
        )
        self.assertEqual(len(sent_messages), 0)


class WebhookSendingGateTests(unittest.TestCase):
    def test_webhook_sends_real_reply_when_sending_enabled(self) -> None:
        sent_messages: list[dict] = []

        class FakeBaleClient:
            def __init__(self, settings):
                self.settings = settings

            def send_message(self, chat_id, text, reply_to_message_id=None):
                sent_messages.append({"chat_id": chat_id, "text": text})
                return {"ok": True, "result": {"message_id": 456}}

        original_cwd = Path.cwd()
        env_keys = (
            "BALE_BOT_TOKEN",
            "BALE_API_BASE_URL",
            "BALE_ENABLE_SENDING",
            "DATABASE_PATH",
            "BALE_REPLY_TEXT",
            "BALE_WEBHOOK_SECRET",
        )
        original_values = {key: os.environ.get(key) for key in env_keys}

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                for key in original_values:
                    os.environ.pop(key, None)

                os.environ["BALE_BOT_TOKEN"] = "test-token"
                os.environ["BALE_API_BASE_URL"] = "https://example.test"
                os.environ["BALE_ENABLE_SENDING"] = "true"
                os.environ["DATABASE_PATH"] = "test.db"
                os.environ["BALE_REPLY_TEXT"] = "سلام حسین جان!"
                os.environ["BALE_WEBHOOK_SECRET"] = "test-secret"

                import app.main as main_module

                main_module = importlib.reload(main_module)

                payload = {
                    "message": {
                        "message_id": 123,
                        "chat": {"id": "demo-chat"},
                        "text": "Hello pharmacy",
                    }
                }

                with patch("app.handlers.BaleClient", FakeBaleClient):
                    with TestClient(main_module.app) as client:
                        response = client.post("/webhook/bale/test-secret", json=payload)
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["reply_prepared"])
        self.assertFalse(data["reply_result"].get("skipped"))
        self.assertEqual(len(sent_messages), 1)
        self.assertEqual(sent_messages[0]["chat_id"], "demo-chat")


if __name__ == "__main__":
    unittest.main()
