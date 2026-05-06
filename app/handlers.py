import logging
from typing import Any

from .bale_client import BaleAPIError, BaleClient
from .config import get_settings
from .database import save_incoming_message
from .models import IncomingMessage
from .replies import build_safe_reply

logger = logging.getLogger(__name__)

COMMAND_REPLIES = {
    "/start": (
        "Hello. I am a pharmacy message intake assistant. "
        "I can receive your message for pharmacy review, but I am not a medical advisor."
    ),
    "/help": "Available commands: /start, /help, /status",
    "/status": "Bot is running and ready to receive pharmacy intake messages.",
}


def get_reply_text(message_text: str | None, default_reply_text: str) -> str:
    if message_text is None:
        return default_reply_text

    command = message_text.strip().split(maxsplit=1)[0].lower()
    if command in COMMAND_REPLIES:
        return COMMAND_REPLIES[command]

    return build_safe_reply(message_text, default_reply_text)


def route_update(update: dict[str, Any]) -> dict[str, Any]:
    incoming = IncomingMessage.from_update(update)
    saved_id = save_incoming_message(incoming)
    settings = get_settings()

    reply_result = None
    can_prepare_reply = incoming.chat_id is not None and incoming.text is not None
    reply_text = get_reply_text(incoming.text, settings.bale_reply_text)

    if can_prepare_reply and not settings.bale_enable_sending:
        reply_result = {
            "ok": False,
            "skipped": True,
            "reason": "Sending is disabled. Set BALE_ENABLE_SENDING=true to enable.",
            "chat_id": incoming.chat_id,
            "text": reply_text,
        }
        logger.info("Prepared reply but sending is disabled for chat_id=%s", incoming.chat_id)
    elif can_prepare_reply and settings.bale_enable_sending:
        client = BaleClient(settings)
        try:
            reply_result = client.send_message(
                chat_id=incoming.chat_id,
                text=reply_text,
            )
        except (BaleAPIError, ValueError) as exc:
            logger.exception("Failed to send Bale message for chat_id=%s", incoming.chat_id)
            reply_result = {
                "ok": False,
                "skipped": False,
                "error": str(exc),
            }

    return {
        "ok": True,
        "stored_message_id": saved_id,
        "reply_prepared": reply_result is not None,
        "reply_result": reply_result,
    }
