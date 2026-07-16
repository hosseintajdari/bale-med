from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

MAX_OWNER_NOTES_LENGTH = 500
MAX_CORRECTED_DRUG_NAME_LENGTH = 120
DEFAULT_SHADOW_REVIEW_LIMIT = 50
MAX_SHADOW_REVIEW_LIMIT = 200

TriStateChoice = Literal["yes", "no", "skip"]


@dataclass(frozen=True)
class ShadowReviewAnnotationInput:
    needs_review_ok: bool | None
    drug_name_ok: bool | None
    corrected_drug_name: str | None
    owner_notes: str | None


class ShadowReviewAnnotationPayload(BaseModel):
    needs_review_ok: bool | None = None
    drug_name_ok: bool | None = None
    corrected_drug_name: str | None = Field(default=None, max_length=MAX_CORRECTED_DRUG_NAME_LENGTH)
    owner_notes: str | None = Field(default=None, max_length=MAX_OWNER_NOTES_LENGTH)

    @field_validator("corrected_drug_name", "owner_notes", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("text fields must be strings or null")
        cleaned = value.strip()
        return cleaned or None


def parse_tristate_choice(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"", "skip", "unknown"}:
        return None
    if normalized in {"yes", "true", "1"}:
        return True
    if normalized in {"no", "false", "0"}:
        return False
    raise ValueError("tristate fields must be yes, no, or skip")


def payload_to_annotation_input(
    payload: ShadowReviewAnnotationPayload,
) -> ShadowReviewAnnotationInput:
    return ShadowReviewAnnotationInput(
        needs_review_ok=payload.needs_review_ok,
        drug_name_ok=payload.drug_name_ok,
        corrected_drug_name=payload.corrected_drug_name,
        owner_notes=payload.owner_notes,
    )


def form_to_annotation_input(form_data: dict[str, str]) -> ShadowReviewAnnotationInput:
    return ShadowReviewAnnotationInput(
        needs_review_ok=parse_tristate_choice(form_data.get("needs_review_ok")),
        drug_name_ok=parse_tristate_choice(form_data.get("drug_name_ok")),
        corrected_drug_name=_clean_optional_text(form_data.get("corrected_drug_name")),
        owner_notes=_clean_optional_text(form_data.get("owner_notes")),
    )


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return cleaned


def clamp_shadow_review_limit(limit: int | None) -> int:
    if limit is None:
        return DEFAULT_SHADOW_REVIEW_LIMIT
    if limit < 1:
        return 1
    if limit > MAX_SHADOW_REVIEW_LIMIT:
        return MAX_SHADOW_REVIEW_LIMIT
    return limit
