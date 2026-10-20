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
    bale_local_review_token: str
    bale_store_raw_updates: bool
    bale_admin_chat_id: str
    bale_enable_admin_notifications: bool
    bale_enable_llm: bool
    bale_llm_mode: str
    bale_llm_api_base_url: str
    bale_llm_api_key: str
    bale_llm_model: str
    bale_llm_timeout_seconds: float


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_float(value: str | None, default: float) -> float:
    if value is None or not value.strip():
        return default
    return float(value.strip())


def _normalize_llm_mode(value: str | None) -> str:
    if value is None:
        return "shadow"
    normalized = value.strip().lower()
    if normalized not in {"shadow", "live"}:
        return "shadow"
    return normalized


def get_settings() -> Settings:
    load_dotenv(dotenv_path=Path.cwd() / ".env")

    default_reply_text = (
        "پیام شما دریافت شد.\n"
        "این ربات جایگزین نظر داروساز یا پزشک نیست.\n"
        "در صورت نیاز، پیام شما توسط داروساز بررسی می‌شود."
    )

    return Settings(
        bale_bot_token=os.getenv("BALE_BOT_TOKEN", ""),
        bale_api_base_url=os.getenv("BALE_API_BASE_URL", "https://tapi.bale.ai"),
        bale_enable_sending=_to_bool(os.getenv("BALE_ENABLE_SENDING"), default=False),
        database_path=os.getenv("DATABASE_PATH", "bale_bot.db"),
        bale_reply_text=os.getenv("BALE_REPLY_TEXT", default_reply_text),
        bale_webhook_secret=os.getenv("BALE_WEBHOOK_SECRET", ""),
        bale_local_review_token=os.getenv("BALE_LOCAL_REVIEW_TOKEN", ""),
        bale_store_raw_updates=_to_bool(os.getenv("BALE_STORE_RAW_UPDATES"), default=False),
        bale_admin_chat_id=os.getenv("BALE_ADMIN_CHAT_ID", ""),
        bale_enable_admin_notifications=_to_bool(
            os.getenv("BALE_ENABLE_ADMIN_NOTIFICATIONS"),
            default=False,
        ),
        bale_enable_llm=_to_bool(os.getenv("BALE_ENABLE_LLM"), default=False),
        bale_llm_mode=_normalize_llm_mode(os.getenv("BALE_LLM_MODE")),
        bale_llm_api_base_url=os.getenv("BALE_LLM_API_BASE_URL", ""),
        bale_llm_api_key=os.getenv("BALE_LLM_API_KEY", ""),
        bale_llm_model=os.getenv("BALE_LLM_MODEL", "gpt-4o-mini"),
        bale_llm_timeout_seconds=_to_float(os.getenv("BALE_LLM_TIMEOUT_SECONDS"), default=10.0),
    )
