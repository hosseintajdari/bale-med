from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IncomingMessage:
    chat_id: str | None
    message_id: str | None
    text: str | None
    external_event_id: str | None
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
        update_id = update.get("update_id")

        normalized_chat_id = str(chat_id) if chat_id is not None else None
        normalized_message_id = str(message_id) if message_id is not None else None
        external_event_id = None
        if update_id is not None:
            external_event_id = f"update:{update_id}"
        elif normalized_chat_id is not None and normalized_message_id is not None:
            external_event_id = f"message:{normalized_chat_id}:{normalized_message_id}"

        return cls(
            chat_id=normalized_chat_id,
            message_id=normalized_message_id,
            text=str(text) if text is not None else None,
            external_event_id=external_event_id,
            raw_update=update,
        )
