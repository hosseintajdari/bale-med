"""tests/test_shadow_emitter.py — تست‌های واحد shadow_emitter."""
from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from app.shadow_emitter import (
    EmitResult,
    EmitterSettings,
    _map_risk_level,
    build_shadow_payload,
    emit_shadow_record,
)


class TestMapRiskLevel(unittest.TestCase):
    """تست‌های تبدیل LLM fields به risk level."""

    def test_none_fields_returns_safe(self):
        self.assertEqual(_map_risk_level(None), "safe")

    def test_urgent_symptoms_returns_redline(self):
        fields = {"risk_flags": {"urgent_symptoms": True}, "needs_review": False}
        self.assertEqual(_map_risk_level(fields), "redline")

    def test_dose_interaction_returns_redline(self):
        fields = {"risk_flags": {"dose_interaction_mention": True}, "needs_review": False}
        self.assertEqual(_map_risk_level(fields), "redline")

    def test_allergy_returns_caution(self):
        fields = {"risk_flags": {"allergy": True}, "needs_review": False}
        self.assertEqual(_map_risk_level(fields), "caution")

    def test_pregnancy_returns_caution(self):
        fields = {"risk_flags": {"pregnancy_lactation": True}, "needs_review": False}
        self.assertEqual(_map_risk_level(fields), "caution")

    def test_needs_review_returns_caution(self):
        fields = {"risk_flags": {}, "needs_review": True}
        self.assertEqual(_map_risk_level(fields), "caution")

    def test_all_clear_returns_safe(self):
        fields = {
            "risk_flags": {
                "allergy": False,
                "pregnancy_lactation": False,
                "pediatric": False,
                "urgent_symptoms": False,
                "dose_interaction_mention": False,
            },
            "needs_review": False,
        }
        self.assertEqual(_map_risk_level(fields), "safe")


class TestBuildShadowPayload(unittest.TestCase):
    """تست‌های ساخت payload."""

    def _make_payload(self, **kwargs):
        defaults = {
            "chat_id": "123456789",
            "user_message": "قیمت آموکسی‌سیلین؟",
            "proposed_reply": "پیام شما دریافت شد.",
            "timestamp": "2026-09-17T00:00:00+00:00",
        }
        defaults.update(kwargs)
        return build_shadow_payload(**defaults)

    def test_engine_id_is_set(self):
        payload = self._make_payload()
        self.assertEqual(payload["engine_id"], "bale-med-v2")

    def test_session_id_format(self):
        payload = self._make_payload(chat_id="987654321")
        self.assertEqual(payload["shadow_item"]["sessionId"], "bale-987654321")

    def test_channel_is_bale(self):
        payload = self._make_payload()
        self.assertEqual(payload["shadow_item"]["channel"], "bale")

    def test_status_is_pending(self):
        payload = self._make_payload()
        self.assertEqual(payload["shadow_item"]["status"], "pending")

    def test_shadow_id_format(self):
        payload = self._make_payload()
        shadow_id = payload["shadow_item"]["id"]
        self.assertTrue(shadow_id.startswith("sh-"), f"ID باید با sh- شروع شود: {shadow_id}")
        parts = shadow_id.split("-")
        self.assertEqual(len(parts), 3)

    def test_required_fields_present(self):
        payload = self._make_payload()
        item = payload["shadow_item"]
        for field in ("id", "sessionId", "channel", "userMessage", "proposedReply",
                      "timestamp", "riskLevel", "status"):
            self.assertIn(field, item, f"فیلد اجباری {field} وجود ندارد")

    def test_deterministic_rule_passed_through(self):
        payload = self._make_payload(deterministic_rule="qanoon-price-v3")
        self.assertEqual(payload["shadow_item"]["deterministicRuleApplied"], "qanoon-price-v3")

    def test_json_serializable(self):
        payload = self._make_payload()
        # نباید exception بیندازد
        json.dumps(payload, ensure_ascii=False)


class TestEmitShadowRecord(unittest.TestCase):
    """تست‌های ارسال shadow record."""

    def _disabled_settings(self) -> EmitterSettings:
        return EmitterSettings(
            enabled=False, base_url="http://localhost:3000", token="test", timeout_seconds=5.0
        )

    def _enabled_settings(self, token: str = "tok-123") -> EmitterSettings:
        return EmitterSettings(
            enabled=True, base_url="http://localhost:3000", token=token, timeout_seconds=5.0
        )

    def _sample_payload(self) -> dict:
        return build_shadow_payload(
            chat_id="111",
            user_message="سلام",
            proposed_reply="پیام دریافت شد.",
            timestamp="2026-09-17T00:00:00+00:00",
        )

    def test_disabled_returns_skipped(self):
        result = emit_shadow_record(self._sample_payload(), settings=self._disabled_settings())
        self.assertTrue(result.skipped)
        self.assertFalse(result.success)

    def test_missing_token_returns_skipped(self):
        settings = EmitterSettings(
            enabled=True, base_url="http://localhost:3000", token="", timeout_seconds=5.0
        )
        result = emit_shadow_record(self._sample_payload(), settings=settings)
        self.assertTrue(result.skipped)

    def test_success_200(self):
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response

        with patch("app.shadow_emitter.httpx.Client", return_value=mock_client):
            result = emit_shadow_record(self._sample_payload(), settings=self._enabled_settings())

        self.assertTrue(result.success)
        self.assertFalse(result.skipped)
        self.assertEqual(result.status_code, 200)
        self.assertIsNone(result.error)

    def test_server_error_401(self):
        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response

        with patch("app.shadow_emitter.httpx.Client", return_value=mock_client):
            result = emit_shadow_record(self._sample_payload(), settings=self._enabled_settings())

        self.assertFalse(result.success)
        self.assertFalse(result.skipped)
        self.assertEqual(result.status_code, 401)

    def test_timeout_does_not_raise(self):
        import httpx as _httpx

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = _httpx.TimeoutException("timeout")

        with patch("app.shadow_emitter.httpx.Client", return_value=mock_client):
            result = emit_shadow_record(self._sample_payload(), settings=self._enabled_settings())

        self.assertFalse(result.success)
        self.assertEqual(result.error, "timeout")

    def test_unexpected_exception_does_not_raise(self):
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = RuntimeError("boom")

        with patch("app.shadow_emitter.httpx.Client", return_value=mock_client):
            result = emit_shadow_record(self._sample_payload(), settings=self._enabled_settings())

        self.assertFalse(result.success)
        self.assertIn("unexpected", result.error or "")


if __name__ == "__main__":
    unittest.main()
