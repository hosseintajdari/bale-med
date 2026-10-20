from .drug_lexicon import normalize_persian_text

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
    "اوردوز",
    "خودکشی",
    "درد قفسه سینه",
    "تنگی نفس",
    "حساسیت شدید",
    "حساسیت",
    "آلرژی",
    "باردار",
    "بارداری",
    "شیردهی",
    "کودک",
    "بچه",
    "نوزاد",
    "دوز",
    "مقدار مصرف",
    "تداخل",
    "عارضه",
    "عوارض",
    "قطع دارو",
    "تغییر دارو",
    "شروع دارو",
)

SAFE_INTAKE_REPLY = (
    "پیام شما دریافت شد.\n"
    "لطفا این اطلاعات را بفرستید:\n"
    "نام دارو\n"
    "سن بیمار\n"
    "پرسش اصلی یا علامت اصلی\n"
    "آیا حساسیت، بارداری، شیردهی، مصرف برای کودک، یا عارضه جدی وجود دارد؟\n\n"
    "تصمیم‌های دارویی باید توسط داروساز بررسی شود."
)

ESCALATION_REPLY = (
    "پیام شما دریافت شد و نیاز به بررسی داروساز دارد.\n"
    "مواردی مثل حساسیت، بارداری، شیردهی، علائم شدید، یا مصرف برای کودک باید با داروساز بررسی شود.\n"
    "این ربات تشخیص، دوز، تداخل دارویی، یا توصیه برای شروع، قطع، یا تغییر دارو ارائه نمی‌کند.\n"
    "لطفا منتظر بررسی داروساز بمانید.\n"
    "اگر علائم شدید یا فوری است، برای دریافت مراقبت پزشکی فوری یا اورژانس اقدام کنید."
)

EMERGENCY_REDLINE_KEYWORDS = (
    "overdose",
    "suicide",
    "chest pain",
    "shortness of breath",
    "severe allergy",
    "anaphylaxis",
    "seizure",
    "unconscious",
    "اوردوز",
    "خودکشی",
    "درد قفسه سینه",
    "تنگی نفس",
    "حساسیت شدید",
    "بیهوشی",
    "تشنج",
    "خونریزی شدید",
    "شوک",
)

ER_URGENT_REPLY = (
    "هشدار فوری پزشکی:\n"
    "علائم ارائه‌شده ممکن است نشان‌دهنده یک وضعیت اضطراری و خطرناک پزشکی باشند.\n"
    "این سامانه قابلیت ارائه خدمات اورژانسی ندارد.\n"
    "لطفا فوراً با اورژانس (شماره ۱۱۵) تماس بگیرید یا به نزدیک‌ترین مرکز فوریت‌های پزشکی/بیمارستان مراجعه نمایید.\n\n"
    "پیام شما همزمان برای بررسی داروساز نیز ثبت گردید."
)


def is_emergency_urgent(message_text: str) -> bool:
    normalized = normalize_persian_text(message_text)
    return any(keyword in normalized for keyword in EMERGENCY_REDLINE_KEYWORDS)


def needs_pharmacist_review(message_text: str) -> bool:
    normalized = normalize_persian_text(message_text)
    return any(keyword in normalized for keyword in HIGH_RISK_KEYWORDS)


def determine_disposition(message_text: str | None) -> str:
    """Determine clinical intake disposition (D0 / D1 / D2).
    D0: Normal intake (no review required)
    D1: Pharmacist review required
    D2: Emergency red flag (immediate 115 / ER guidance + pharmacist escalation)
    """
    if message_text is None or not message_text.strip():
        return "D0"
    if is_emergency_urgent(message_text):
        return "D2"
    if needs_pharmacist_review(message_text):
        return "D1"
    return "D0"


def build_safe_reply(message_text: str | None, default_reply_text: str) -> str:
    if message_text is None or not message_text.strip():
        return default_reply_text

    disposition = determine_disposition(message_text)
    if disposition == "D2":
        return ER_URGENT_REPLY
    if disposition == "D1":
        return ESCALATION_REPLY

    return SAFE_INTAKE_REPLY

