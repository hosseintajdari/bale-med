import re
from typing import Any

from .types import ALLOWED_AGE_BANDS, RISK_FLAG_KEYS, LLMExtractedFields

BANNED_OUTPUT_PATTERNS = (
    r"\bdiagnos(e|is|ed|ing)\b",
    r"\byou should take\b",
    r"\brecommend(ed|s)? (taking|using)\b",
    r"\b(increase|decrease|adjust) (the )?dose\b",
    r"\bstop (taking|using)\b",
    r"\bstart (taking|using)\b",
    r"\bchange (your )?medication\b",
    r"\bemergency triage\b",
    r"\bcall 911\b",
    r"\bتشخیص\b",
    r"\bدوز.*(پیشنهاد|توصیه)\b",
    r"\b(شروع|قطع|تغییر) دارو\b",
    r"\bاورژانس.*(تماس|اقدام)\b",
)

BANNED_OUTPUT_REGEXES = tuple(
    re.compile(pattern, re.IGNORECASE) for pattern in BANNED_OUTPUT_PATTERNS
)


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _contains_banned_advice(text: str) -> bool:
    return any(regex.search(text) for regex in BANNED_OUTPUT_REGEXES)


def _validate_optional_string_field(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string or null")
    cleaned = value.strip()
    if not cleaned:
        return None
    if _contains_banned_advice(cleaned):
        raise ValueError(f"{field_name} contains banned clinical advice")
    return cleaned


def validate_llm_payload(payload: dict[str, Any]) -> LLMExtractedFields:
    if not isinstance(payload, dict):
        raise ValueError("LLM payload must be a JSON object")

    if "needs_review" not in payload or not isinstance(payload["needs_review"], bool):
        raise ValueError("needs_review must be a boolean")

    risk_flags_raw = payload.get("risk_flags")
    if not isinstance(risk_flags_raw, dict):
        raise ValueError("risk_flags must be an object")

    risk_flags: dict[str, bool] = {}
    for key in RISK_FLAG_KEYS:
        value = risk_flags_raw.get(key, False)
        if not isinstance(value, bool):
            raise ValueError(f"risk_flags.{key} must be a boolean")
        risk_flags[key] = value

    age_band = payload.get("approximate_age_band")
    if age_band is not None:
        if not isinstance(age_band, str):
            raise ValueError("approximate_age_band must be a string or null")
        normalized_age_band = age_band.strip().lower()
        if normalized_age_band and normalized_age_band not in ALLOWED_AGE_BANDS:
            raise ValueError("approximate_age_band has an unsupported value")
        age_band = normalized_age_band or None

    drug_name = _validate_optional_string_field(payload.get("drug_name"), "drug_name")
    main_question_topic = _validate_optional_string_field(
        payload.get("main_question_topic"),
        "main_question_topic",
    )

    return LLMExtractedFields(
        needs_review=payload["needs_review"],
        drug_name=drug_name,
        main_question_topic=main_question_topic,
        risk_flags=risk_flags,
        approximate_age_band=age_band,
    )
