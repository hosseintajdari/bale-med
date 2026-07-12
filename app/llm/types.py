from dataclasses import dataclass
from typing import Any

ALLOWED_AGE_BANDS = frozenset({"child", "adult", "elderly", "unknown"})
RISK_FLAG_KEYS = (
    "allergy",
    "pregnancy_lactation",
    "pediatric",
    "urgent_symptoms",
    "dose_interaction_mention",
)


@dataclass(frozen=True)
class LLMExtractedFields:
    needs_review: bool
    drug_name: str | None
    main_question_topic: str | None
    risk_flags: dict[str, bool]
    approximate_age_band: str | None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "needs_review": self.needs_review,
            "drug_name": self.drug_name,
            "main_question_topic": self.main_question_topic,
            "risk_flags": dict(self.risk_flags),
            "approximate_age_band": self.approximate_age_band,
        }


@dataclass(frozen=True)
class LLMAuditMetadata:
    model_id: str | None
    latency_ms: int | None
    validation_pass: bool
    status: str

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "llm_model_id": self.model_id,
            "llm_latency_ms": self.latency_ms,
            "llm_validation_pass": self.validation_pass,
            "llm_status": self.status,
        }
