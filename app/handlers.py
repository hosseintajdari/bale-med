import logging
from typing import Any

from .bale_client import BaleAPIError, BaleClient
from .config import get_settings
from .database import save_incoming_message
from .models import IncomingMessage
from .replies import build_safe_reply, needs_pharmacist_review

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
        return (
            "ربات فعال است.\n"
            "ارسال پیام واقعی روشن است.\n"
            "ممکن است پاسخ واقعی در بله ارسال شود."
        )
    return (
        "ربات فعال است.\n"
        "ارسال پیام واقعی خاموش است.\n"
        "ربات در حالت آزمایشی کار می‌کند."
    )


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
    if command in COMMAND_REPLIES:
        return {
            "needs_review": False,
            "review_reason": None,
            "review_status": "not_required",
        }

    if needs_pharmacist_review(message_text):
        return {
            "needs_review": True,
            "review_reason": "pharmacist_review_required",
            "review_status": "pending",
        }

    return {
        "needs_review": False,
        "review_reason": None,
        "review_status": "not_required",
    }


def route_update(update: dict[str, Any]) -> dict[str, Any]:
    incoming = IncomingMessage.from_update(update)
    review_metadata = get_review_metadata(incoming.text)
    save_result = save_incoming_message(
        incoming,
        needs_review=bool(review_metadata["needs_review"]),
        review_reason=review_metadata["review_reason"],
        review_status=str(review_metadata["review_status"]),
    )
    saved_id = save_result.stored_message_id
    settings = get_settings()
    has_text = incoming.text is not None
    text_length = len(incoming.text) if incoming.text is not None else 0

    if save_result.inserted:
        logger.info(
            "webhook_update_received stored_message_id=%s has_chat_id=%s has_message_id=%s "
            "has_external_event_id=%s has_text=%s text_length=%s needs_review=%s review_status=%s",
            saved_id,
            incoming.chat_id is not None,
            incoming.message_id is not None,
            incoming.external_event_id is not None,
            has_text,
            text_length,
            bool(review_metadata["needs_review"]),
            review_metadata["review_status"],
        )
    else:
        logger.info(
            "duplicate_webhook_update_received stored_message_id=%s has_external_event_id=%s",
            saved_id,
            incoming.external_event_id is not None,
        )

    reply_result = None
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

    return {
        "ok": True,
        "stored_message_id": saved_id,
        "message_inserted": save_result.inserted,
        "duplicate_delivery": not save_result.inserted,
        "reply_prepared": reply_result is not None,
        "reply_result": reply_result,
    }
