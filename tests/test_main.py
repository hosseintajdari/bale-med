import asyncio
import importlib
import json
import os
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from starlette.requests import Request

LOCAL_REVIEW_TEST_HEADERS = {
    "Authorization": "Basic cmV2aWV3OnRlc3QtbG9jYWwtcmV2aWV3LXRva2Vu"
}


class AuthorizedTestClient(TestClient):
    def __init__(self, app, **kwargs):
        kwargs.setdefault("headers", LOCAL_REVIEW_TEST_HEADERS)
        super().__init__(app, **kwargs)


TestClient = AuthorizedTestClient


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
                "BALE_LOCAL_REVIEW_TOKEN",
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
        os.environ["BALE_LOCAL_REVIEW_TOKEN"] = "test-local-review-token"

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
        self.assertNotIn("chat_id", data["reply_result"])

        connection = sqlite3.connect("test.db")
        try:
            row = connection.execute(
                "SELECT chat_id, message_id, text FROM incoming_messages"
            ).fetchone()
        finally:
            connection.close()

        self.assertEqual(row, ("demo-chat", "123", "Hello pharmacy"))

    def test_webhook_runs_sync_processing_outside_the_event_loop_thread(self):
        event_loop_thread = threading.get_ident()
        processing_threads = []

        async def receive():
            return {
                "type": "http.request",
                "body": json.dumps(self._payload()).encode("utf-8"),
                "more_body": False,
            }

        request = Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/webhook/bale/test-secret",
                "headers": [],
                "query_string": b"",
                "server": ("testserver", 80),
                "client": ("testclient", 123),
                "scheme": "http",
                "http_version": "1.1",
            },
            receive,
        )

        def record_processing_thread(update):
            processing_threads.append(threading.get_ident())
            return {"ok": True, "update_received": bool(update)}

        with patch.object(
            self.main_module, "route_update", side_effect=record_processing_thread
        ):
            result = asyncio.run(self.main_module.bale_webhook("test-secret", request))

        self.assertEqual(result, {"ok": True, "update_received": True})
        self.assertEqual(len(processing_threads), 1)
        self.assertNotEqual(processing_threads[0], event_loop_thread)

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
            client.post(
                "/webhook/bale/test-secret", json=self._payload("Hello pharmacy", message_id=123)
            )
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
        self.assertIn("llm_extracted", pending)
        self.assertIn("llm_status", pending)
        self.assertNotIn("raw_update", pending)

    def test_pending_reviews_endpoint_returns_empty_list_for_fresh_database(self):
        with TestClient(self.main_module.app) as client:
            response = client.get("/local/reviews/pending")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"pending_reviews": []})

    def test_pending_reviews_endpoint_rejects_missing_token_from_non_local_client(self):
        with TestClient(self.main_module.app, client=("203.0.113.10", 50000), headers={}) as client:
            response = client.get("/local/reviews/pending")

        self.assertEqual(response.status_code, 401)

    def test_authenticated_review_endpoint_works_behind_header_stripping_proxy(self):
        with TestClient(self.main_module.app, client=("127.0.0.1", 50000)) as client:
            response = client.get("/local/reviews/pending")

        self.assertEqual(response.status_code, 200)

    def test_review_endpoint_rejects_missing_token_even_when_proxy_strips_forwarded_headers(self):
        with TestClient(self.main_module.app, headers={}) as client:
            response = client.get("/local/reviews/pending")

        self.assertEqual(response.status_code, 401)

    def test_authenticated_pending_reviews_works_with_forwarded_header(self):
        with TestClient(self.main_module.app) as client:
            response = client.get(
                "/local/reviews/pending",
                headers={"X-Forwarded-For": "203.0.113.10"},
            )

        self.assertEqual(response.status_code, 200)

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

    def test_authenticated_mark_reviewed_works_with_forwarded_header(self):
        with TestClient(self.main_module.app) as client:
            webhook_response = client.post(
                "/webhook/bale/test-secret",
                json=self._payload("Can I use this medicine during pregnancy?", message_id=124),
            )
            stored_message_id = webhook_response.json()["stored_message_id"]

            response = client.post(
                f"/local/reviews/{stored_message_id}/mark-reviewed",
                headers={"X-Forwarded-For": "203.0.113.10"},
            )

        self.assertEqual(response.status_code, 200)

        connection = sqlite3.connect("test.db")
        try:
            row = connection.execute(
                "SELECT review_status FROM incoming_messages WHERE id = ?",
                (stored_message_id,),
            ).fetchone()
        finally:
            connection.close()

        self.assertEqual(row, ("reviewed",))

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

    def test_webhook_rejects_malformed_json_with_400(self):
        with TestClient(self.main_module.app) as client:
            response = client.post(
                "/webhook/bale/test-secret",
                content="malformed-not-json",
                headers={"Content-Type": "application/json"},
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid JSON payload")

    def test_webhook_rejects_non_dict_json_with_400(self):
        with TestClient(self.main_module.app) as client:
            response = client.post(
                "/webhook/bale/test-secret",
                json=["not", "a", "dict"],
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Webhook payload must be a JSON object")

    def test_review_stats_endpoint_returns_metrics(self):
        with TestClient(self.main_module.app) as client:
            initial_stats = client.get("/local/reviews/stats").json()
            self.assertEqual(initial_stats["total_messages"], 0)
            self.assertEqual(initial_stats["pending_reviews"], 0)

            webhook_response = client.post(
                "/webhook/bale/test-secret",
                json=self._payload("Can I use this medicine during pregnancy?", message_id=124),
            )
            stored_message_id = webhook_response.json()["stored_message_id"]

            after_insert_stats = client.get("/local/reviews/stats").json()
            self.assertEqual(after_insert_stats["total_messages"], 1)
            self.assertEqual(after_insert_stats["pending_reviews"], 1)
            self.assertEqual(after_insert_stats["reviewed"], 0)

            client.post(f"/local/reviews/{stored_message_id}/mark-reviewed")

            after_review_stats = client.get("/local/reviews/stats").json()
            self.assertEqual(after_review_stats["total_messages"], 1)
            self.assertEqual(after_review_stats["pending_reviews"], 0)
            self.assertEqual(after_review_stats["reviewed"], 1)

    def test_review_stats_endpoint_rejects_missing_token_from_non_local_client(self):
        with TestClient(self.main_module.app, client=("203.0.113.10", 50000), headers={}) as client:
            response = client.get("/local/reviews/stats")
        self.assertEqual(response.status_code, 401)

    def test_annotate_shadow_review_rejects_invalid_json_with_400(self):
        with TestClient(self.main_module.app) as client:
            response = client.post(
                "/local/shadow-reviews/1/annotate",
                content="invalid json payload {{{",
                headers={"Content-Type": "application/json"},
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid JSON payload")

    def test_annotate_shadow_review_rejects_invalid_form_utf8_with_400(self):
        with TestClient(self.main_module.app, raise_server_exceptions=False) as client:
            response = client.post(
                "/local/shadow-reviews/1/annotate",
                content=b"\xff",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid form encoding")

    def test_annotate_shadow_review_rejects_invalid_schema_with_422(self):
        with TestClient(self.main_module.app) as client:
            response = client.post(
                "/local/shadow-reviews/1/annotate",
                json={"owner_notes": 12345},  # numbers not allowed where string/null expected
                headers={"Content-Type": "application/json"},
            )
        self.assertEqual(response.status_code, 422)

    def test_lexicon_resolve_endpoint_exact_and_fuzzy(self):
        with TestClient(self.main_module.app) as client:
            # 1. Exact match
            res = client.get("/api/v1/lexicon/resolve", params={"q": "استامینوفن"})
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data["matched"])
            self.assertEqual(data["canonical_entry"]["generic_name"], "Acetaminophen")
            self.assertFalse(data["is_controlled"])

            # 2. Controlled substance
            res_controlled = client.get("/api/v1/lexicon/resolve", params={"q": "استامینوفن کدئین"})
            self.assertEqual(res_controlled.status_code, 200)
            data_ctrl = res_controlled.json()
            self.assertTrue(data_ctrl["matched"])
            self.assertTrue(data_ctrl["is_controlled"])

    def test_lexicon_controlled_list_endpoint(self):
        with TestClient(self.main_module.app) as client:
            res = client.get("/api/v1/lexicon/controlled")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn("controlled_drugs", data)
            self.assertGreater(len(data["controlled_drugs"]), 0)
            names = [d["generic_name"] for d in data["controlled_drugs"]]
            self.assertIn("Acetaminophen Codeine", names)
            self.assertIn("Diazepam", names)
            self.assertIn("Clonazepam", names)


if __name__ == "__main__":
    unittest.main()

