from typing import Protocol

from ..config import Settings


def minimize_message_snippet(
    message_text: str,
    settings: Settings,
    chat_id: str | None,
    max_chars: int = 280,
) -> str:
    compact = " ".join(message_text.split())
    redacted = _redact_known_sensitive_values(compact, settings, chat_id)
    if len(redacted) <= max_chars:
        return redacted
    return f"{redacted[: max_chars - 3].rstrip()}..."


def _redact_known_sensitive_values(text: str, settings: Settings, chat_id: str | None) -> str:
    redacted = text
    for value in (
        settings.bale_bot_token,
        settings.bale_webhook_secret,
        settings.bale_admin_chat_id,
        settings.bale_llm_api_key,
        chat_id,
    ):
        if value:
            redacted = redacted.replace(str(value), "[redacted]")
    return redacted


class LLMClient(Protocol):
    def classify_message(self, snippet: str) -> dict:
        """Return provider JSON payload with a structured classification object."""


CLASSIFICATION_SYSTEM_PROMPT = (
    "You classify pharmacy patient messages for internal pharmacist workflow only. "
    "Return JSON only. Never diagnose, dose, recommend medication changes, or give emergency triage. "
    "Set needs_review=true when the message is ambiguous, high-risk, or needs pharmacist judgment."
)

CLASSIFICATION_USER_TEMPLATE = (
    "Classify this minimized patient message snippet and return JSON with keys: "
    "needs_review (boolean), drug_name (string|null), main_question_topic (string|null), "
    "risk_flags (object with boolean keys allergy, pregnancy_lactation, pediatric, "
    "urgent_symptoms, dose_interaction_mention), approximate_age_band "
    "(child|adult|elderly|unknown|null). "
    "Do not include advice, diagnosis, or dosing instructions in any string field.\n\n"
    "Snippet:\n{snippet}"
)
