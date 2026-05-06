from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IncomingMessage:
    chat_id: str | None
    message_id: str | None
    text: str | None
    raw_update: dict[str, Any]

    @classmethod
    def from_update(cls, update: dict[str, Any]) -> "IncomingMessage":
        # TODO: Confirm exact Bale webhook fields. These optional lookups are based
        # on Telegram-like structure because Bale Bot API is described as similar.
        message = update.get("message") if isinstance(update.get("message"), dict) else {}
        chat = message.get("chat") if isinstance(message.get("chat"), dict) else {}

        chat_id = chat.get("id")
        message_id = message.get("message_id")
        text = message.get("text")

        return cls(
            chat_id=str(chat_id) if chat_id is not None else None,
            message_id=str(message_id) if message_id is not None else None,
            text=str(text) if text is not None else None,
            raw_update=update,
        )
