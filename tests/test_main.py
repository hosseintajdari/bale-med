import importlib
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


class WebhookRouteTests(unittest.TestCase):
    def setUp(self):
        self.original_cwd = Path.cwd()
        self.original_values = {
            key: os.environ.get(key)
            for key in (
                "BALE_BOT_TOKEN",
                "BALE_API_BASE_URL",
                "BALE_ENABLE_SENDING",
                "DATABASE_PATH",
                "BALE_REPLY_TEXT",
                "BALE_WEBHOOK_SECRET",
            )
        }
        self.temp_dir = tempfile.TemporaryDirectory()
        os.chdir(self.temp_dir.name)
        for key in self.original_values:
            os.environ.pop(key, None)

        os.environ["BALE_BOT_TOKEN"] = "test-token"
        os.environ["BALE_API_BASE_URL"] = "https://example.test"
        os.environ["BALE_ENABLE_SENDING"] = "false"
        os.environ["DATABASE_PATH"] = "test.db"
        os.environ["BALE_REPLY_TEXT"] = "سلام حسین جان!"
        os.environ["BALE_WEBHOOK_SECRET"] = "test-secret"

        import app.main as main_module

        self.main_module = importlib.reload(main_module)

    def tearDown(self):
        os.chdir(self.original_cwd)
        for key, value in self.original_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.temp_dir.cleanup()

    def _payload(self, text: str = "Hello pharmacy", message_id: int = 123) -> dict:
        return {
            "message": {
                "message_id": message_id,
                "chat": {"id": "demo-chat"},
                "text": text,
            }
        }

    def test_webhook_accepts_correct_secret_and_stores_message(self):
        with TestClient(self.main_module.app) as client:
            response = client.post("/webhook/bale/test-secret", json=self._payload())

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertTrue(data["reply_prepared"])
        self.assertTrue(data["reply_result"]["skipped"])

        connection = sqlite3.connect("test.db")
        try:
            row = connection.execute(
                "SELECT chat_id, message_id, text FROM incoming_messages"
            ).fetchone()
        finally:
            connection.close()

        self.assertEqual(row, ("demo-chat", "123", "Hello pharmacy"))

    def test_webhook_response_does_not_include_admin_notification_text(self):
        os.environ["BALE_ENABLE_ADMIN_NOTIFICATIONS"] = "true"
        os.environ["BALE_ADMIN_CHAT_ID"] = "admin-chat"

        import app.main as main_module

        self.main_module = importlib.reload(main_module)

        with TestClient(self.main_module.app) as client:
            response = client.post(
                "/webhook/bale/test-secret",
                json=self._payload("Can I use this during pregnancy?", message_id=124),
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["admin_notification_prepared"])
        self.assertNotIn("text", data["admin_notification_result"])

    def test_webhook_rejects_wrong_secret(self):
        with TestClient(self.main_module.app) as client:
            response = client.post("/webhook/bale/wrong-secret", json=self._payload())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Not Found")

        connection = sqlite3.connect("test.db")
        try:
            count = connection.execute("SELECT COUNT(*) FROM incoming_messages").fetchone()[0]
        finally:
            connection.close()

        self.assertEqual(count, 0)

    def test_pending_reviews_endpoint_lists_only_pending_review_items(self):
        with TestClient(self.main_module.app) as client:
            client.post("/webhook/bale/test-secret", json=self._payload("Hello pharmacy", message_id=123))
            client.post(
                "/webhook/bale/test-secret",
                json=self._payload("Can I use this medicine during pregnancy?", message_id=124),
            )

            response = client.get("/local/reviews/pending")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["pending_reviews"]), 1)
        pending = data["pending_reviews"][0]
        self.assertEqual(pending["chat_id"], "demo-chat")
        self.assertEqual(pending["message_id"], "124")
        self.assertEqual(pending["text"], "Can I use this medicine during pregnancy?")
        self.assertEqual(pending["review_reason"], "pharmacist_review_required")
        self.assertEqual(pending["review_status"], "pending")
        self.assertNotIn("raw_update", pending)

    def test_pending_reviews_endpoint_returns_empty_list_for_fresh_database(self):
        with TestClient(self.main_module.app) as client:
            response = client.get("/local/reviews/pending")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"pending_reviews": []})

    def test_pending_reviews_endpoint_rejects_non_local_client(self):
        with TestClient(self.main_module.app, client=("203.0.113.10", 50000)) as client:
            response = client.get("/local/reviews/pending")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Not Found")

    def test_pending_review_item_can_be_marked_reviewed(self):
        with TestClient(self.main_module.app) as client:
            webhook_response = client.post(
                "/webhook/bale/test-secret",
                json=self._payload("Can I use this medicine during pregnancy?", message_id=124),
            )
            stored_message_id = webhook_response.json()["stored_message_id"]

            response = client.post(f"/local/reviews/{stored_message_id}/mark-reviewed")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "ok": True,
                "message_id": stored_message_id,
                "review_status": "reviewed",
                "changed": True,
            },
        )

        connection = sqlite3.connect("test.db")
        try:
            row = connection.execute(
                "SELECT review_status FROM incoming_messages WHERE id = ?",
                (stored_message_id,),
            ).fetchone()
        finally:
            connection.close()

        self.assertEqual(row, ("reviewed",))

    def test_reviewed_item_no_longer_appears_in_pending_reviews(self):
        with TestClient(self.main_module.app) as client:
            webhook_response = client.post(
                "/webhook/bale/test-secret",
                json=self._payload("Can I use this medicine during pregnancy?", message_id=124),
            )
            stored_message_id = webhook_response.json()["stored_message_id"]

            client.post(f"/local/reviews/{stored_message_id}/mark-reviewed")
            response = client.get("/local/reviews/pending")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"pending_reviews": []})

    def test_mark_reviewed_endpoint_rejects_non_local_client(self):
        with TestClient(self.main_module.app, client=("203.0.113.10", 50000)) as client:
            response = client.post("/local/reviews/1/mark-reviewed")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Not Found")

    def test_mark_reviewed_endpoint_returns_404_for_missing_item(self):
        with TestClient(self.main_module.app) as client:
            response = client.post("/local/reviews/999/mark-reviewed")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Not Found")

    def test_mark_reviewed_endpoint_is_safe_for_already_reviewed_item(self):
        with TestClient(self.main_module.app) as client:
            webhook_response = client.post(
                "/webhook/bale/test-secret",
                json=self._payload("Can I use this medicine during pregnancy?", message_id=124),
            )
            stored_message_id = webhook_response.json()["stored_message_id"]

            first_response = client.post(f"/local/reviews/{stored_message_id}/mark-reviewed")
            second_response = client.post(f"/local/reviews/{stored_message_id}/mark-reviewed")

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(
            second_response.json(),
            {
                "ok": True,
                "message_id": stored_message_id,
                "review_status": "reviewed",
                "changed": False,
            },
        )


if __name__ == "__main__":
    unittest.main()
