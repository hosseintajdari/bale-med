"""shadow_emitter.py — ارسال shadow record به bale-panel.

این ماژول مسئول ارسال نتایج LLM shadow به pipeline پنل مدیریت است.
**shadow-only**: هرگز پاسخ بیمار را تغییر نمی‌دهد.

متغیرهای محیطی:
    PANEL_BASE_URL        آدرس bale-panel (پیش‌فرض: http://localhost:3000)
    PANEL_OPERATOR_TOKEN  توکن Bearer برای احراز هویت (اجباری برای emit)
    PANEL_EMIT_ENABLED    true/1/yes برای فعال کردن emit (پیش‌فرض: false)
    PANEL_EMIT_TIMEOUT    تایم‌اوت ثانیه (پیش‌فرض: 5.0)

قرارداد API: docs/api-contract.md (از bale-panel) — v1.0
"""
from __future__ import annotations

import json
import logging
import os
import random
import socket
import string
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

RiskLevel = Literal["safe", "caution", "redline"]

_ENDPOINT = "/api/pipeline/ingest/shadow-trace"
_ENGINE_ID = "bale-med-v2"


# ---------------------------------------------------------------------------
# تنظیمات
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EmitterSettings:
    """تنظیمات ارتباط با bale-panel."""

    enabled: bool
    base_url: str
    token: str
    timeout_seconds: float


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_float(value: str | None, default: float) -> float:
    if value is None or not value.strip():
        return default
    try:
        return float(value.strip())
    except ValueError:
        return default


def get_emitter_settings() -> EmitterSettings:
    """تنظیمات emitter را از متغیرهای محیطی می‌خواند."""
    return EmitterSettings(
        enabled=_to_bool(os.getenv("PANEL_EMIT_ENABLED"), default=False),
        base_url=os.getenv("PANEL_BASE_URL", "http://localhost:3000").rstrip("/"),
        token=os.getenv("PANEL_OPERATOR_TOKEN", ""),
        timeout_seconds=_to_float(os.getenv("PANEL_EMIT_TIMEOUT"), default=5.0),
    )


# ---------------------------------------------------------------------------
# ساخت Payload
# ---------------------------------------------------------------------------


def _generate_shadow_id() -> str:
    """یک ID یکتا با فرمت sh-{timestamp}-{rand5} می‌سازد."""
    ts = int(time.time())
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"sh-{ts}-{rand}"


def _map_risk_level(extracted_fields: dict | None) -> RiskLevel:
    """بر اساس فیلدهای LLM سطح ریسک را تعیین می‌کند."""
    if extracted_fields is None:
        return "safe"

    risk_flags: dict = extracted_fields.get("risk_flags", {})
    if risk_flags.get("urgent_symptoms") or risk_flags.get("dose_interaction_mention"):
        return "redline"
    if any(
        risk_flags.get(k)
        for k in ("allergy", "pregnancy_lactation", "pediatric")
    ):
        return "caution"
    if extracted_fields.get("needs_review"):
        return "caution"
    return "safe"


def build_shadow_payload(
    *,
    chat_id: str,
    user_message: str,
    proposed_reply: str,
    timestamp: str,
    extracted_fields: dict | None = None,
    deterministic_rule: str | None = None,
    confidence_score: float = 0.9,
) -> dict:
    """
    یک ShadowEmitPayload کامل طبق api-contract.md می‌سازد.

    Args:
        chat_id: chat ID بله (بدون پیشوند — خودش اضافه می‌شود)
        user_message: متن اصلی پیام کاربر
        proposed_reply: پاسخ پیشنهادی ربات
        timestamp: ISO 8601 UTC (مثلاً از datetime.now(UTC).isoformat())
        extracted_fields: خروجی LLMExtractedFields.to_json_dict() یا None
        deterministic_rule: شناسه قانون keyword اعمال‌شده یا None
        confidence_score: امتیاز اطمینان LLM (0–1)
    """
    risk_level = _map_risk_level(extracted_fields)

    return {
        "engine_id": _ENGINE_ID,
        "shadow_item": {
            "id": _generate_shadow_id(),
            "sessionId": f"bale-{chat_id}",
            "channel": "bale",
            "senderDisplay": f"bale-{chat_id}",
            "userMessage": user_message,
            "proposedReply": proposed_reply,
            "timestamp": timestamp,
            "confidenceScore": confidence_score,
            "riskLevel": risk_level,
            "status": "pending",
            "deterministicRuleApplied": deterministic_rule,
            "auditNote": None,
            "editedReply": None,
        },
    }


# ---------------------------------------------------------------------------
# ارسال به پنل
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EmitResult:
    """نتیجه ارسال shadow record."""

    success: bool
    skipped: bool
    status_code: int | None
    error: str | None


def emit_shadow_record(
    payload: dict,
    *,
    settings: EmitterSettings | None = None,
) -> EmitResult:
    """
    Shadow record را به bale-panel POST می‌کند.

    **هرگز exception نمی‌اندازد** — شکست emit روی پردازش اصلی تأثیر نمی‌گذارد.
    خطاها فقط log می‌شوند.

    Args:
        payload: خروجی build_shadow_payload()
        settings: در صورت None از get_emitter_settings() خوانده می‌شود

    Returns:
        EmitResult با جزئیات نتیجه ارسال
    """
    cfg = settings or get_emitter_settings()

    if not cfg.enabled:
        logger.debug("panel_emit_skipped reason=disabled")
        return EmitResult(success=False, skipped=True, status_code=None, error=None)

    if not cfg.token:
        logger.warning("panel_emit_skipped reason=missing_token")
        return EmitResult(
            success=False,
            skipped=True,
            status_code=None,
            error="PANEL_OPERATOR_TOKEN not set",
        )

    url = f"{cfg.base_url}{_ENDPOINT}"
    shadow_id = payload.get("shadow_item", {}).get("id", "unknown")

    try:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {cfg.token}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=cfg.timeout_seconds) as resp:
            status_code: int = resp.status

        if 200 <= status_code < 300:
            logger.info(
                "panel_emit_ok shadow_id=%s status=%s",
                shadow_id,
                status_code,
            )
            return EmitResult(
                success=True,
                skipped=False,
                status_code=status_code,
                error=None,
            )

        logger.warning(
            "panel_emit_failed shadow_id=%s status=%s",
            shadow_id,
            status_code,
        )
        return EmitResult(
            success=False,
            skipped=False,
            status_code=status_code,
            error=f"HTTP {status_code}",
        )

    except urllib.error.HTTPError as exc:
        logger.warning(
            "panel_emit_failed shadow_id=%s status=%s body=%.200s",
            shadow_id,
            exc.code,
            exc.read().decode("utf-8", errors="replace"),
        )
        return EmitResult(success=False, skipped=False, status_code=exc.code, error=f"HTTP {exc.code}")

    except TimeoutError:
        logger.warning("panel_emit_timeout shadow_id=%s url=%s", shadow_id, url)
        return EmitResult(success=False, skipped=False, status_code=None, error="timeout")

    except urllib.error.URLError as exc:
        logger.warning("panel_emit_error shadow_id=%s error=%s", shadow_id, exc.reason)
        return EmitResult(success=False, skipped=False, status_code=None, error=str(exc.reason))

    except Exception as exc:  # noqa: BLE001
        logger.exception("panel_emit_unexpected shadow_id=%s", shadow_id)
        return EmitResult(
            success=False, skipped=False, status_code=None, error=f"unexpected: {exc}"
        )
