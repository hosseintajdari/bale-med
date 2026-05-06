HIGH_RISK_KEYWORDS = (
    "overdose",
    "suicide",
    "chest pain",
    "shortness of breath",
    "severe allergy",
    "allergy",
    "allergic",
    "pregnant",
    "pregnancy",
    "breastfeeding",
    "child",
    "baby",
    "infant",
    "dosage",
    "dose",
    "interaction",
    "side effect",
    "stop medication",
    "change medication",
    "start medication",
)

SAFE_INTAKE_REPLY = (
    "Thanks. Your message was received by the pharmacy. "
    "Please send the medicine name, patient age range, the main question or symptom, "
    "and any allergy, pregnancy, breastfeeding, child use, or serious side-effect information. "
    "A pharmacist should review medical questions before any decision."
)

ESCALATION_REPLY = (
    "Thanks. Your message may need pharmacist review. "
    "This bot cannot give diagnosis, dosage, interaction, or medication-change advice. "
    "Please wait for pharmacist review. If symptoms are severe or urgent, seek emergency medical care."
)


def needs_pharmacist_review(message_text: str) -> bool:
    normalized = message_text.lower()
    return any(keyword in normalized for keyword in HIGH_RISK_KEYWORDS)


def build_safe_reply(message_text: str | None, default_reply_text: str) -> str:
    if message_text is None or not message_text.strip():
        return default_reply_text

    if needs_pharmacist_review(message_text):
        return ESCALATION_REPLY

    return SAFE_INTAKE_REPLY
