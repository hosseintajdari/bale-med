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


def needs_pharmacist_review(message_text: str) -> bool:
    normalized = message_text.lower()
    return any(keyword in normalized for keyword in HIGH_RISK_KEYWORDS)


def build_safe_reply(message_text: str | None, default_reply_text: str) -> str:
    if message_text is None or not message_text.strip():
        return default_reply_text

    if needs_pharmacist_review(message_text):
        return ESCALATION_REPLY

    return SAFE_INTAKE_REPLY
