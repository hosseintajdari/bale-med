import importlib
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.database import init_db
from app.shadow_review import form_to_annotation_input, parse_tristate_choice
from fastapi.testclient import TestClient


def _insert_shadow_ok_message(
    connection: sqlite3.Connection,
    *,
    text: str,
    extracted: dict,
    message_id: str = "100",
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO incoming_messages (
            received_at,
            chat_id,
            message_id,
            external_event_id,
            text,
            raw_update,
            needs_review,
            review_reason,
            review_status,
            llm_extracted_json,
            llm_model_id,
            llm_latency_ms,
            llm_validation_pass,
            llm_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "2026-07-16T10:00:00+00:00",
            "demo-chat",
            message_id,
            f"event-{message_id}",
            text,
            '{"raw_update_storage":"disabled"}',
            0,
            None,
            "not_required",
            json.dumps(extracted, ensure_ascii=False),
            "DeepSeek-V3.2",
            42,
            1,
            "shadow_ok",
        ),
    )
    connection.commit()
    return int(cursor.lastrowid)


class ShadowReviewHelperTests(unittest.TestCase):
    def test_parse_tristate_choice(self):
        self.assertIs(parse_tristate_choice("yes"), True)
        self.assertIs(parse_tristate_choice("no"), False)
        self.assertIsNone(parse_tristate_choice("skip"))
        with self.assertRaises(ValueError):
            parse_tristate_choice("maybe")

    def test_form_to_annotation_input(self):
        annotation = form_to_annotation_input(
            {
                "needs_review_ok": "yes",
                "drug_name_ok": "no",
                "corrected_drug_name": " ibuprofen ",
                "owner_notes": " typo in LLM ",
            }
        )
        self.assertTrue(annotation.needs_review_ok)
        self.assertFalse(annotation.drug_name_ok)
        self.assertEqual(annotation.corrected_drug_name, "ibuprofen")
        self.assertEqual(annotation.owner_notes, "typo in LLM")


class ShadowReviewRouteTests(unittest.TestCase):
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
        os.environ["BALE_REPLY_TEXT"] = "سلام"
        os.environ["BALE_WEBHOOK_SECRET"] = "test-secret"

        init_db()
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

    def _seed_shadow_message(
        self, *, text: str = "نیاز به استامینوفن دارم", message_id: str = "100"
    ) -> int:
        connection = sqlite3.connect("test.db")
        try:
            return _insert_shadow_ok_message(
                connection,
                text=text,
                extracted={
                    "needs_review": False,
                    "drug_name": "acetaminophen",
                    "main_question_topic": "availability",
                    "risk_flags": {
                        "allergy": False,
                        "pregnancy_lactation": False,
                        "pediatric": False,
                        "urgent_symptoms": False,
                        "dose_interaction_mention": False,
                    },
                    "approximate_age_band": "adult",
                },
                message_id=message_id,
            )
        finally:
            connection.close()

    def test_shadow_reviews_endpoint_lists_shadow_ok_rows(self):
        stored_message_id = self._seed_shadow_message()

        with TestClient(self.main_module.app) as client:
            response = client.get("/local/shadow-reviews?limit=10")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["limit"], 10)
        item = data["shadow_reviews"][0]
        self.assertEqual(item["id"], stored_message_id)
        self.assertEqual(item["llm_status"], "shadow_ok")
        self.assertEqual(item["llm_extracted"]["drug_name"], "acetaminophen")
        self.assertIsNone(item["annotation"])

    def test_shadow_reviews_ui_renders_message_preview(self):
        self._seed_shadow_message(text="پیام تست داروساز")

        with TestClient(self.main_module.app) as client:
            response = client.get("/local/shadow-reviews/ui")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("پیام تست داروساز", response.text)
        self.assertIn("P2 Shadow Review", response.text)

    def test_shadow_review_annotation_can_be_saved_via_json(self):
        stored_message_id = self._seed_shadow_message()

        with TestClient(self.main_module.app) as client:
            response = client.post(
                f"/local/shadow-reviews/{stored_message_id}/annotate",
                json={
                    "needs_review_ok": True,
                    "drug_name_ok": False,
                    "corrected_drug_name": "acetaminophen",
                    "owner_notes": "LLM used Latin name only",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["message_id"], stored_message_id)
        self.assertFalse(data["drug_name_ok"])
        self.assertEqual(data["owner_notes"], "LLM used Latin name only")

        with TestClient(self.main_module.app) as client:
            listed = client.get("/local/shadow-reviews").json()["shadow_reviews"][0]

        self.assertIsNotNone(listed["annotation"])
        self.assertFalse(listed["annotation"]["drug_name_ok"])

    def test_shadow_review_form_post_redirects_back_to_ui(self):
        stored_message_id = self._seed_shadow_message()

        with TestClient(self.main_module.app, follow_redirects=False) as client:
            response = client.post(
                f"/local/shadow-reviews/{stored_message_id}/annotate",
                data={
                    "needs_review_ok": "yes",
                    "drug_name_ok": "yes",
                    "owner_notes": "looks good",
                    "redirect_to_ui": "1",
                },
            )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["location"],
            f"/local/shadow-reviews/ui?saved={stored_message_id}",
        )

    def test_shadow_review_annotation_returns_404_for_non_shadow_message(self):
        connection = sqlite3.connect("test.db")
        try:
            cursor = connection.execute(
                """
                INSERT INTO incoming_messages (
                    received_at, chat_id, message_id, text, raw_update,
                    needs_review, review_status, llm_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "2026-07-16T10:00:00+00:00",
                    "demo-chat",
                    "201",
                    "Hello pharmacy",
                    '{"raw_update_storage":"disabled"}',
                    0,
                    "not_required",
                    None,
                ),
            )
            connection.commit()
            stored_message_id = int(cursor.lastrowid)
        finally:
            connection.close()

        with TestClient(self.main_module.app) as client:
            response = client.post(
                f"/local/shadow-reviews/{stored_message_id}/annotate",
                json={"needs_review_ok": True},
            )

        self.assertEqual(response.status_code, 404)

    def test_shadow_review_routes_reject_non_local_client(self):
        self._seed_shadow_message()

        with TestClient(self.main_module.app, client=("203.0.113.10", 50000)) as client:
            list_response = client.get("/local/shadow-reviews")
            ui_response = client.get("/local/shadow-reviews/ui")
            annotate_response = client.post(
                "/local/shadow-reviews/1/annotate",
                json={"needs_review_ok": True},
            )

        self.assertEqual(list_response.status_code, 404)
        self.assertEqual(ui_response.status_code, 404)
        self.assertEqual(annotate_response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
