import logging
from typing import Any

from .bale_client import BaleAPIError, BaleClient
from .config import Settings, get_settings
from .database import LLMStorageFields, save_incoming_message
from .llm import classify_message_text, merge_review_metadata
from .llm.service import should_run_llm_for_message
from .models import IncomingMessage
from .replies import (
    build_safe_reply,
    is_emergency_urgent,
    needs_pharmacist_review,
)

logger = logging.getLogger(__name__)

COMMAND_REPLIES = {
    "/start": (
        "سلام.\n"
        "من دستیار دریافت پیام داروخانه هستم.\n"
        "پیام شما را برای بررسی داروساز ثبت می‌کنم.\n"
        "این ربات جایگزین نظر داروساز یا پزشک نیست."
    ),
    "/help": (
        "دستورهای قابل استفاده:\n"
        "/start\n"
        "/help\n"
        "/status\n\n"
        "برای پرسش دارویی، پیام خود را کوتاه و روشن بنویسید."
    ),
}


def get_status_reply(bale_enable_sending: bool) -> str:
    if bale_enable_sending:
        return "ربات فعال است.\nارسال پیام واقعی روشن است.\nممکن است پاسخ واقعی در بله ارسال شود."
    return "ربات فعال است.\nارسال پیام واقعی خاموش است.\nربات در حالت آزمایشی کار می‌کند."


def get_reply_text(
    message_text: str | None,
    default_reply_text: str,
    bale_enable_sending: bool = False,
) -> str:
    if message_text is None:
        return default_reply_text

    command = message_text.strip().split(maxsplit=1)[0].lower()
    if command == "/status":
        return get_status_reply(bale_enable_sending)
    if command == "/rare":
        from .rare_medicine import get_rare_medicine_service
        service = get_rare_medicine_service()
        parts = message_text.strip().split(maxsplit=1)
        subquery = parts[1].strip() if len(parts) > 1 else ""
        if not subquery:
            return (
                "راهنمای جستجوی داروی کمیاب:\n"
                "جهت استعلام موجودی سهمیه‌ای و داروخانه‌های توزیع، نام دارو را به همراه دستور ارسال کنید:\n"
                "مثال: /rare هرسپتین یا /rare IVIG\n\n"
                "سامانه تلفنی کمبودهای دارویی وزارت بهداشت: سامانه ۱۹۰"
            )
        result = service.search(query=subquery)
        return service.format_search_summary_reply(result)
    if command in COMMAND_REPLIES:
        return COMMAND_REPLIES[command]

    return build_safe_reply(message_text, default_reply_text)


def get_review_metadata(message_text: str | None) -> dict[str, str | bool | None]:
    if message_text is None:
        return {
            "needs_review": False,
            "review_reason": None,
            "review_status": "not_required",
        }

    command = message_text.strip().split(maxsplit=1)[0].lower()
    if command in COMMAND_REPLIES or command == "/rare":
        return {
            "needs_review": False,
            "review_reason": None,
            "review_status": "not_required",
        }

    if is_emergency_urgent(message_text):
        return {
            "needs_review": True,
            "review_reason": "er_urgent_redline",
            "review_status": "pending",
            "disposition": "D2",
        }

    if needs_pharmacist_review(message_text):
        return {
            "needs_review": True,
            "review_reason": "pharmacist_review_required",
            "review_status": "pending",
            "disposition": "D1",
        }

    return {
        "needs_review": False,
        "review_reason": None,
        "review_status": "not_required",
        "disposition": "D0",
    }


def _redact_known_sensitive_values(text: str, settings: Settings, chat_id: str | None) -> str:
    redacted = text
    for value in (
        settings.bale_bot_token,
        settings.bale_webhook_secret,
        settings.bale_admin_chat_id,
        chat_id,
    ):
        if value:
            redacted = redacted.replace(str(value), "[redacted]")
    return redacted


def _build_text_preview(message_text: str | None, settings: Settings, chat_id: str | None) -> str:
    if not message_text:
        return ""

    compact = " ".join(message_text.split())
    redacted = _redact_known_sensitive_values(compact, settings, chat_id)
    return f"[redacted message: {len(redacted)} chars]"


def build_admin_review_notification_text(
    stored_message_id: int,
    review_reason: str,
    message_text: str | None,
    settings: Settings,
    chat_id: str | None,
) -> str:
    preview = _build_text_preview(message_text, settings, chat_id)
    lines = [
        "Pharmacist review needed.",
        f"stored_message_id={stored_message_id}",
        f"review_reason={review_reason}",
    ]
    if preview:
        lines.append(f"text_preview={preview}")
    lines.append("Check local pending review list: /local/reviews/pending")
    return "\n".join(lines)


def prepare_admin_review_notification(
    stored_message_id: int,
    review_reason: str,
    message_text: str | None,
    settings: Settings,
    chat_id: str | None,
) -> dict[str, Any]:
    notification_text = build_admin_review_notification_text(
        stored_message_id=stored_message_id,
        review_reason=review_reason,
        message_text=message_text,
        settings=settings,
        chat_id=chat_id,
    )

    base_result: dict[str, Any] = {
        "ok": False,
        "skipped": True,
        "stored_message_id": stored_message_id,
        "review_reason": review_reason,
        "text": notification_text,
    }

    if not settings.bale_enable_admin_notifications:
        return {
            **base_result,
            "reason": "Admin notifications are disabled.",
        }
    if not settings.bale_admin_chat_id.strip():
        return {
            **base_result,
            "reason": "BALE_ADMIN_CHAT_ID is not configured.",
        }
    if not settings.bale_enable_sending:
        return {
            **base_result,
            "reason": "Admin notifications require BALE_ENABLE_SENDING=true.",
        }

    try:
        send_result = BaleClient(settings).send_message(
            chat_id=settings.bale_admin_chat_id,
            text=notification_text,
        )
    except (BaleAPIError, ValueError) as exc:
        logger.exception("admin_notification_send_failed stored_message_id=%s", stored_message_id)
        return {
            **base_result,
            "skipped": False,
            "error": str(exc),
        }

    return {
        **base_result,
        "ok": True,
        "skipped": False,
        "send_result": send_result,
    }


def build_public_reply_result(reply_result: dict[str, Any] | None) -> dict[str, Any] | None:
    if reply_result is None:
        return None

    public_result: dict[str, Any] = {
        "ok": reply_result.get("ok", False),
        "skipped": reply_result.get("skipped", False),
    }
    if "reason" in reply_result:
        public_result["reason"] = reply_result["reason"]
    if "error" in reply_result:
        public_result["error"] = reply_result["error"]
    if "text" in reply_result:
        public_result["text"] = reply_result["text"]
    return public_result


def build_public_admin_notification_result(
    notification_result: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if notification_result is None:
        return None

    public_result = {
        "ok": notification_result.get("ok", False),
        "skipped": notification_result.get("skipped", True),
        "stored_message_id": notification_result.get("stored_message_id"),
        "review_reason": notification_result.get("review_reason"),
    }
    if "reason" in notification_result:
        public_result["reason"] = notification_result["reason"]
    if "error" in notification_result:
        public_result["error"] = notification_result["error"]
    return public_result


def build_llm_storage_fields(llm_result) -> LLMStorageFields | None:
    if llm_result.audit.status == "disabled":
        return None
    return LLMStorageFields(
        extracted_json=llm_result.extracted_json,
        model_id=llm_result.audit.model_id,
        latency_ms=llm_result.audit.latency_ms,
        validation_pass=llm_result.audit.validation_pass,
        status=llm_result.audit.status,
    )

def emit_shadow_trace(incoming, saved_id, review_metadata, llm_result):
    import json
    import os
    import threading
    import urllib.request
    from datetime import UTC, datetime
    
    payload = {
        "engine_id": "bale-med",
        "shadow_item": {
            "id": f"bmed-{saved_id}",
            "sessionId": str(incoming.chat_id or "unknown"),
            "channel": "bale",
            "senderDisplay": str(incoming.chat_id or "unknown"),
            "userMessage": incoming.text or "",
            "proposedReply": "نیاز به بررسی تخصصی داروساز",
            "timestamp": datetime.now(UTC).isoformat(),
            "confidenceScore": 0.85,
            "riskLevel": "redline" if review_metadata.get("disposition") == "D2" or review_metadata.get("review_reason") == "er_urgent_redline" else ("caution" if review_metadata.get("needs_review") else "safe"),
            "status": "pending",
            "deterministicRuleApplied": str(review_metadata.get("review_reason") or "")
        },
        "pipeline_traces": [
            {
                "stage": "GATEWAY_INGEST",
                "title": "Received via Bale Webhook",
                "status": "passed",
                "detail": "Parsed successfully",
                "durationMs": 5
            }
        ]
    }

    def _send():
        try:
            panel_url = os.environ.get(
                "PANEL_SHADOW_TRACE_URL",
                "http://localhost:3001/api/pipeline/ingest/shadow-trace",
            )
            req = urllib.request.Request(
                panel_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=1)
        except Exception:
            pass

    threading.Thread(target=_send, daemon=True).start()


def route_update(update: dict[str, Any]) -> dict[str, Any]:
    incoming = IncomingMessage.from_update(update)
    settings = get_settings()
    keyword_review_metadata = get_review_metadata(incoming.text)

    llm_result = None
    if settings.bale_enable_llm and should_run_llm_for_message(incoming.text):
        llm_result = classify_message_text(
            incoming.text or "",
            settings,
            incoming.chat_id,
        )

    review_metadata = (
        merge_review_metadata(keyword_review_metadata, llm_result, settings)
        if llm_result is not None
        else keyword_review_metadata
    )

    save_result = save_incoming_message(
        incoming,
        needs_review=bool(review_metadata["needs_review"]),
        review_reason=review_metadata["review_reason"],
        review_status=str(review_metadata["review_status"]),
        llm_fields=build_llm_storage_fields(llm_result) if llm_result is not None else None,
    )
    saved_id = save_result.stored_message_id
    has_text = incoming.text is not None
    text_length = len(incoming.text) if incoming.text is not None else 0

    if save_result.inserted:
        logger.info(
            "webhook_update_received stored_message_id=%s has_chat_id=%s has_message_id=%s "
            "has_external_event_id=%s has_text=%s text_length=%s needs_review=%s review_status=%s "
            "llm_enabled=%s llm_mode=%s llm_status=%s",
            saved_id,
            incoming.chat_id is not None,
            incoming.message_id is not None,
            incoming.external_event_id is not None,
            has_text,
            text_length,
            bool(review_metadata["needs_review"]),
            review_metadata["review_status"],
            settings.bale_enable_llm,
            settings.bale_llm_mode if settings.bale_enable_llm else "off",
            llm_result.audit.status if llm_result is not None else "not_run",
        )
    else:
        logger.info(
            "duplicate_webhook_update_received stored_message_id=%s has_external_event_id=%s",
            saved_id,
            incoming.external_event_id is not None,
        )

    reply_result = None
    admin_notification_result = None
    can_prepare_reply = incoming.chat_id is not None and incoming.text is not None
    reply_text = get_reply_text(
        incoming.text,
        settings.bale_reply_text,
        bale_enable_sending=settings.bale_enable_sending,
    )

    if not save_result.inserted:
        can_prepare_reply = False

    if can_prepare_reply and not settings.bale_enable_sending:
        reply_result = {
            "ok": False,
            "skipped": True,
            "reason": "Sending is disabled. Set BALE_ENABLE_SENDING=true to enable.",
            "chat_id": incoming.chat_id,
            "text": reply_text,
        }
        logger.info(
            "reply_prepared stored_message_id=%s sending_enabled=%s skipped=%s review_status=%s",
            saved_id,
            settings.bale_enable_sending,
            True,
            review_metadata["review_status"],
        )
    elif can_prepare_reply and settings.bale_enable_sending:
        client = BaleClient(settings)
        try:
            reply_result = client.send_message(
                chat_id=incoming.chat_id,
                text=reply_text,
            )
            logger.info(
                "reply_prepared stored_message_id=%s sending_enabled=%s skipped=%s review_status=%s",
                saved_id,
                settings.bale_enable_sending,
                False,
                review_metadata["review_status"],
            )
        except (BaleAPIError, ValueError) as exc:
            logger.exception("reply_send_failed stored_message_id=%s", saved_id)
            reply_result = {
                "ok": False,
                "skipped": False,
                "error": str(exc),
            }

    can_prepare_admin_notification = bool(review_metadata["needs_review"]) and save_result.inserted
    if can_prepare_admin_notification:
        admin_notification_result = prepare_admin_review_notification(
            stored_message_id=saved_id,
            review_reason=str(review_metadata["review_reason"]),
            message_text=incoming.text,
            settings=settings,
            chat_id=incoming.chat_id,
        )
        logger.info(
            "admin_notification_prepared stored_message_id=%s skipped=%s review_status=%s",
            saved_id,
            admin_notification_result.get("skipped"),
            review_metadata["review_status"],
        )

    emit_shadow_trace(incoming, saved_id, review_metadata, llm_result)

    return {
        "ok": True,
        "stored_message_id": saved_id,
        "message_inserted": save_result.inserted,
        "duplicate_delivery": not save_result.inserted,
        "reply_prepared": reply_result is not None,
        "reply_result": build_public_reply_result(reply_result),
        "admin_notification_prepared": admin_notification_result is not None,
        "admin_notification_result": build_public_admin_notification_result(
            admin_notification_result
        ),
    }
