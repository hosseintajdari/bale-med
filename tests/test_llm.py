import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.config import get_settings
from app.database import init_db
from app.handlers import route_update
from app.llm.service import LLMRunResult, merge_review_metadata
from app.llm.types import LLMAuditMetadata, LLMExtractedFields
from app.llm.validator import validate_llm_payload


def _valid_payload(**overrides) -> dict:
    payload = {
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
    }
    payload.update(overrides)
    return payload


class LLMValidatorTests(unittest.TestCase):
    def test_validator_accepts_safe_structured_payload(self):
        extracted = validate_llm_payload(_valid_payload())
        self.assertFalse(extracted.needs_review)
        self.assertEqual(extracted.drug_name, "acetaminophen")
        self.assertEqual(extracted.main_question_topic, "availability")

    def test_validator_rejects_banned_clinical_advice_in_string_fields(self):
        with self.assertRaises(ValueError):
            validate_llm_payload(_valid_payload(main_question_topic="You should take 500mg daily"))

        with self.assertRaises(ValueError):
            validate_llm_payload(_valid_payload(drug_name="diagnosis: migraine"))

    def test_validator_rejects_invalid_age_band(self):
        with self.assertRaises(ValueError):
            validate_llm_payload(_valid_payload(approximate_age_band="teen"))


class LLMServiceTests(unittest.TestCase):
    def test_merge_review_metadata_preserves_keyword_floor_in_live_mode(self):
        keyword_metadata = {
            "needs_review": True,
            "review_reason": "pharmacist_review_required",
            "review_status": "pending",
        }
        llm_result = LLMRunResult(
            extracted=LLMExtractedFields(
                needs_review=False,
                drug_name=None,
                main_question_topic=None,
                risk_flags={
                    key: False
                    for key in (
                        "allergy",
                        "pregnancy_lactation",
                        "pediatric",
                        "urgent_symptoms",
                        "dose_interaction_mention",
                    )
                },
                approximate_age_band=None,
            ),
            audit=LLMAuditMetadata(
                model_id="test-model",
                latency_ms=10,
                validation_pass=True,
                status="live_ok",
            ),
            extracted_json="{}",
        )
        settings = type(
            "SettingsStub",
            (),
            {"bale_enable_llm": True, "bale_llm_mode": "live"},
        )()

        merged = merge_review_metadata(keyword_metadata, llm_result, settings)
        self.assertEqual(merged, keyword_metadata)

    def test_merge_review_metadata_unions_llm_needs_review_in_live_mode(self):
        keyword_metadata = {
            "needs_review": False,
            "review_reason": None,
            "review_status": "not_required",
        }
        llm_result = LLMRunResult(
            extracted=LLMExtractedFields(
                needs_review=True,
                drug_name="ibuprofen",
                main_question_topic="side effects",
                risk_flags={
                    key: False
                    for key in (
                        "allergy",
                        "pregnancy_lactation",
                        "pediatric",
                        "urgent_symptoms",
                        "dose_interaction_mention",
                    )
                },
                approximate_age_band="adult",
            ),
            audit=LLMAuditMetadata(
                model_id="test-model",
                latency_ms=12,
                validation_pass=True,
                status="live_ok",
            ),
            extracted_json="{}",
        )
        settings = type(
            "SettingsStub",
            (),
            {"bale_enable_llm": True, "bale_llm_mode": "live"},
        )()

        merged = merge_review_metadata(keyword_metadata, llm_result, settings)
        self.assertTrue(merged["needs_review"])
        self.assertEqual(merged["review_reason"], "llm_review_required")
        self.assertEqual(merged["review_status"], "pending")

    def test_merge_review_metadata_escalates_on_llm_failure_in_live_mode(self):
        keyword_metadata = {
            "needs_review": False,
            "review_reason": None,
            "review_status": "not_required",
        }
        llm_result = LLMRunResult(
            extracted=None,
            audit=LLMAuditMetadata(
                model_id="test-model",
                latency_ms=None,
                validation_pass=False,
                status="validation_failed",
            ),
            extracted_json=None,
        )
        settings = type(
            "SettingsStub",
            (),
            {"bale_enable_llm": True, "bale_llm_mode": "live"},
        )()

        merged = merge_review_metadata(keyword_metadata, llm_result, settings)
        self.assertTrue(merged["needs_review"])
        self.assertEqual(merged["review_reason"], "llm_fail_safe")

    def test_merge_review_metadata_does_not_change_routing_in_shadow_mode(self):
        keyword_metadata = {
            "needs_review": False,
            "review_reason": None,
            "review_status": "not_required",
        }
        llm_result = LLMRunResult(
            extracted=LLMExtractedFields(
                needs_review=True,
                drug_name=None,
                main_question_topic="urgent",
                risk_flags={
                    key: False
                    for key in (
                        "allergy",
                        "pregnancy_lactation",
                        "pediatric",
                        "urgent_symptoms",
                        "dose_interaction_mention",
                    )
                },
                approximate_age_band=None,
            ),
            audit=LLMAuditMetadata(
                model_id="test-model",
                latency_ms=8,
                validation_pass=True,
                status="shadow_ok",
            ),
            extracted_json="{}",
        )
        settings = type(
            "SettingsStub",
            (),
            {"bale_enable_llm": True, "bale_llm_mode": "shadow"},
        )()

        merged = merge_review_metadata(keyword_metadata, llm_result, settings)
        self.assertEqual(merged, keyword_metadata)


class LLMHandlerIntegrationTests(unittest.TestCase):
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
        "BALE_ENABLE_LLM",
        "BALE_LLM_MODE",
        "BALE_LLM_API_BASE_URL",
        "BALE_LLM_API_KEY",
        "BALE_LLM_MODEL",
        "BALE_LLM_TIMEOUT_SECONDS",
    )

    def _route_with_llm(
        self,
        text: str,
        env_overrides: dict[str, str] | None = None,
        fake_client: object | None = None,
    ) -> tuple[dict, tuple | None]:
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
                patch_target = "app.llm.service.build_llm_client"
                if fake_client is not None:
                    with patch(patch_target, return_value=fake_client):
                        result = route_update(
                            {
                                "message": {
                                    "message_id": 123,
                                    "chat": {"id": "demo-chat"},
                                    "text": text,
                                }
                            }
                        )
                else:
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
                        SELECT needs_review, review_reason, review_status,
                               llm_extracted_json, llm_status, llm_validation_pass
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

    def test_env_defaults_keep_llm_disabled(self):
        original_cwd = Path.cwd()
        original_values = {key: os.environ.get(key) for key in self.ENV_KEYS}

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

        self.assertFalse(settings.bale_enable_llm)
        self.assertEqual(settings.bale_llm_mode, "shadow")

    def test_shadow_mode_persists_llm_fields_without_changing_review_routing(self):
        class FakeClient:
            def classify_message(self, snippet: str) -> dict:
                return _valid_payload(
                    needs_review=True,
                    main_question_topic="stock question",
                    drug_name="vitamin d",
                )

        result, row = self._route_with_llm(
            "Do you have vitamin D?",
            env_overrides={
                "BALE_ENABLE_LLM": "true",
                "BALE_LLM_MODE": "shadow",
                "BALE_LLM_API_BASE_URL": "https://llm.example.test",
                "BALE_LLM_API_KEY": "secret-key",
            },
            fake_client=FakeClient(),
        )

        self.assertTrue(result["ok"])
        self.assertIn("نام دارو", result["reply_result"]["text"])
        needs_review, review_reason, review_status, extracted_json, llm_status, validation_pass = (
            row
        )
        self.assertEqual((needs_review, review_reason, review_status), (0, None, "not_required"))
        self.assertEqual(llm_status, "shadow_ok")
        self.assertEqual(validation_pass, 1)
        extracted = json.loads(extracted_json)
        self.assertTrue(extracted["needs_review"])
        self.assertEqual(extracted["drug_name"], "vitamin d")

    def test_live_mode_unions_llm_needs_review_without_changing_reply_template(self):
        class FakeClient:
            def classify_message(self, snippet: str) -> dict:
                return _valid_payload(needs_review=True, main_question_topic="unclear timing")

        result, row = self._route_with_llm(
            "When should I take this supplement?",
            env_overrides={
                "BALE_ENABLE_LLM": "true",
                "BALE_LLM_MODE": "live",
                "BALE_LLM_API_BASE_URL": "https://llm.example.test",
                "BALE_LLM_API_KEY": "secret-key",
            },
            fake_client=FakeClient(),
        )

        self.assertIn("نام دارو", result["reply_result"]["text"])
        needs_review, review_reason, review_status, _, llm_status, _ = row
        self.assertEqual(
            (needs_review, review_reason, review_status), (1, "llm_review_required", "pending")
        )
        self.assertEqual(llm_status, "live_ok")

    def test_keyword_floor_is_not_downgraded_in_live_mode(self):
        class FakeClient:
            def classify_message(self, snippet: str) -> dict:
                return _valid_payload(needs_review=False)

        result, row = self._route_with_llm(
            "Can I use this during pregnancy?",
            env_overrides={
                "BALE_ENABLE_LLM": "true",
                "BALE_LLM_MODE": "live",
                "BALE_LLM_API_BASE_URL": "https://llm.example.test",
                "BALE_LLM_API_KEY": "secret-key",
            },
            fake_client=FakeClient(),
        )

        self.assertIn("بررسی داروساز", result["reply_result"]["text"])
        needs_review, review_reason, review_status, _, _, _ = row
        self.assertEqual(
            (needs_review, review_reason, review_status),
            (1, "pharmacist_review_required", "pending"),
        )

    def test_validator_failure_escalates_in_live_mode(self):
        class FakeClient:
            def classify_message(self, snippet: str) -> dict:
                return _valid_payload(main_question_topic="You should take 2 tablets")

        _, row = self._route_with_llm(
            "How many tablets?",
            env_overrides={
                "BALE_ENABLE_LLM": "true",
                "BALE_LLM_MODE": "live",
                "BALE_LLM_API_BASE_URL": "https://llm.example.test",
                "BALE_LLM_API_KEY": "secret-key",
            },
            fake_client=FakeClient(),
        )

        needs_review, review_reason, review_status, extracted_json, llm_status, validation_pass = (
            row
        )
        self.assertEqual(
            (needs_review, review_reason, review_status), (1, "llm_fail_safe", "pending")
        )
        self.assertIsNone(extracted_json)
        self.assertEqual(llm_status, "validation_failed")
        self.assertEqual(validation_pass, 0)

    def test_llm_disabled_behaves_like_before(self):
        _, row = self._route_with_llm("I need help with a medicine question")
        needs_review, review_reason, review_status, extracted_json, llm_status, validation_pass = (
            row
        )
        self.assertEqual((needs_review, review_reason, review_status), (0, None, "not_required"))
        self.assertIsNone(extracted_json)
        self.assertIsNone(llm_status)
        self.assertIsNone(validation_pass)


if __name__ == "__main__":
    unittest.main()
