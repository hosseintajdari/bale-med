import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bale_bot_token: str
    bale_api_base_url: str
    bale_enable_sending: bool
    database_path: str
    bale_reply_text: str
    bale_webhook_secret: str


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    load_dotenv(dotenv_path=Path.cwd() / ".env")

    default_reply_text = (
        "پیام شما دریافت شد. این ربات جایگزین نظر داروساز نیست و در صورت نیاز توسط داروساز بررسی میشود."
    )

    return Settings(
        bale_bot_token=os.getenv("BALE_BOT_TOKEN", ""),
        bale_api_base_url=os.getenv("BALE_API_BASE_URL", "https://tapi.bale.ai"),
        bale_enable_sending=_to_bool(os.getenv("BALE_ENABLE_SENDING"), default=False),
        database_path=os.getenv("DATABASE_PATH", "bale_bot.db"),
        bale_reply_text=os.getenv("BALE_REPLY_TEXT", default_reply_text),
        bale_webhook_secret=os.getenv("BALE_WEBHOOK_SECRET", ""),
    )
