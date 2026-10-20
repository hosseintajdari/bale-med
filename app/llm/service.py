import json
import logging
from dataclasses import dataclass
from typing import Any

from ..config import Settings
from .client import minimize_message_snippet
from .provider import build_llm_client, measure_llm_call
from .types import LLMAuditMetadata, LLMExtractedFields
from .validator import validate_llm_payload

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMRunResult:
    extracted: LLMExtractedFields | None
    audit: LLMAuditMetadata
    extracted_json: str | None

    def to_public_dict(self) -> dict[str, Any]:
        public = self.audit.to_public_dict()
        if self.extracted is not None:
            public["llm_extracted"] = self.extracted.to_json_dict()
        return public


def should_run_llm_for_message(message_text: str | None) -> bool:
    if message_text is None or not message_text.strip():
        return False

    command = message_text.strip().split(maxsplit=1)[0].lower()
    return not command.startswith("/")


def classify_message_text(
    message_text: str,
    settings: Settings,
    chat_id: str | None,
    *,
    client: Any | None = None,
) -> LLMRunResult:
    if not settings.bale_enable_llm:
        return LLMRunResult(
            extracted=None,
            audit=LLMAuditMetadata(
                model_id=None,
                latency_ms=None,
                validation_pass=False,
                status="disabled",
            ),
            extracted_json=None,
        )

    snippet = minimize_message_snippet(message_text, settings, chat_id)
    llm_client = client or build_llm_client(settings)
    model_id = settings.bale_llm_model

    try:
        raw_payload, latency_ms = measure_llm_call(llm_client, snippet)
        extracted = validate_llm_payload(raw_payload)
        status = "shadow_ok" if settings.bale_llm_mode == "shadow" else "live_ok"
        extracted_json = json.dumps(extracted.to_json_dict(), ensure_ascii=False)
        return LLMRunResult(
            extracted=extracted,
            audit=LLMAuditMetadata(
                model_id=model_id,
                latency_ms=latency_ms,
                validation_pass=True,
                status=status,
            ),
            extracted_json=extracted_json,
        )
    except Exception as exc:
        logger.exception("llm_classification_failed")
        status = _failure_status(settings, exc)
        return LLMRunResult(
            extracted=None,
            audit=LLMAuditMetadata(
                model_id=model_id,
                latency_ms=None,
                validation_pass=False,
                status=status,
            ),
            extracted_json=None,
        )


def _failure_status(settings: Settings, exc: Exception) -> str:
    if isinstance(exc, ValueError):
        return "validation_failed"
    if settings.bale_llm_mode == "shadow":
        return "shadow_error"
    return "live_error"


def merge_review_metadata(
    keyword_metadata: dict[str, str | bool | None],
    llm_result: LLMRunResult,
    settings: Settings,
) -> dict[str, str | bool | None]:
    if not settings.bale_enable_llm or settings.bale_llm_mode == "shadow":
        return dict(keyword_metadata)

    keyword_needs_review = bool(keyword_metadata.get("needs_review"))
    if keyword_needs_review:
        return dict(keyword_metadata)

    llm_needs_review = bool(llm_result.extracted.needs_review) if llm_result.extracted else False
    llm_failed = not llm_result.audit.validation_pass

    if llm_needs_review or llm_failed:
        reason = "llm_review_required" if llm_needs_review else "llm_fail_safe"
        return {
            "needs_review": True,
            "review_reason": reason,
            "review_status": "pending",
            "disposition": "D1",
        }

    return dict(keyword_metadata)
