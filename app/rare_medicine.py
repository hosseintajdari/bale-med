"""Rare Medicine Query Service Module for BaleMed.

Provides querying, filtering, and patient procurement guidance for rare and
special-disease medicines (داروهای خاص و کمیاب) in Iran, tracking designated
distribution pharmacies (هلال احمر، ۲۹ فروردین، ۱۳ آبان و غیره), required
documentation, and official health ministry inquiry channels (سامانه ۱۹۰).
"""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import closing
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DesignatedPharmacy:
    name: str
    province: str
    city: str
    address: str
    phone: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class RareMedicineItem:
    id: str
    generic_name: str
    brand_names: list[str]
    category: str
    dosage_form: str
    strength: str
    scarcity_level: str  # "critical" | "scarce" | "monitored"
    supply_status: str  # "available_limited" | "inquiry_required" | "central_pharmacy_only" | "out_of_stock"
    designated_pharmacies: list[DesignatedPharmacy]
    required_documents: list[str]
    inquiry_channel: str = "سامانه ۱۹۰ - اطلاعات دارویی و کمبودهای وزارت بهداشت"
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "generic_name": self.generic_name,
            "brand_names": list(self.brand_names),
            "category": self.category,
            "dosage_form": self.dosage_form,
            "strength": self.strength,
            "scarcity_level": self.scarcity_level,
            "supply_status": self.supply_status,
            "designated_pharmacies": [p.to_dict() for p in self.designated_pharmacies],
            "required_documents": list(self.required_documents),
            "inquiry_channel": self.inquiry_channel,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RareMedicineItem:
        pharmacies = [
            DesignatedPharmacy(**p) if isinstance(p, dict) else p
            for p in data.get("designated_pharmacies", [])
        ]
        return cls(
            id=str(data["id"]),
            generic_name=str(data["generic_name"]),
            brand_names=list(data.get("brand_names", [])),
            category=str(data.get("category", "سایر")),
            dosage_form=str(data.get("dosage_form", "")),
            strength=str(data.get("strength", "")),
            scarcity_level=str(data.get("scarcity_level", "monitored")),
            supply_status=str(data.get("supply_status", "inquiry_required")),
            designated_pharmacies=pharmacies,
            required_documents=list(data.get("required_documents", [])),
            inquiry_channel=str(data.get("inquiry_channel", "سامانه ۱۹۰")),
            notes=data.get("notes"),
        )


@dataclass(frozen=True)
class RareMedicineQueryResult:
    query: str
    total: int
    matched_count: int
    items: list[RareMedicineItem]
    official_guidance: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "total": self.total,
            "matched_count": self.matched_count,
            "items": [item.to_dict() for item in self.items],
            "official_guidance": self.official_guidance,
        }


# Curated Seed Data representing representative Iranian rare & specialty drugs
DEFAULT_RARE_MEDICINE_CATALOG: list[RareMedicineItem] = [
    RareMedicineItem(
        id="rare-ivig",
        generic_name="ایمونوگلوبولین وریدی (IVIG)",
        brand_names=["اکتوگام", "Octagam", "Flebogamma", "Privigen", "فلبوگاما"],
        category="ایمونولوژی و بیماری‌های خاص",
        dosage_form="ویال تزریقی",
        strength="5g/100ml (5%)",
        scarcity_level="critical",
        supply_status="available_limited",
        designated_pharmacies=[
            DesignatedPharmacy(
                name="داروخانه ۲۹ فروردین",
                province="تهران",
                city="تهران",
                address="خیابان کارگر جنوبی، میدان حر",
                phone="021-66400000",
            ),
            DesignatedPharmacy(
                name="داروخانه هلال احمر مرکزی",
                province="تهران",
                city="تهران",
                address="خیابان آیت‌الله طالقانی، تقاطع سپهبد قرنی",
                phone="021-88803875",
            ),
            DesignatedPharmacy(
                name="داروخانه ۱۳ آبان",
                province="تهران",
                city="تهران",
                address="خیابان کریمخان زند، نبش خیابان خردمند جنوبی",
                phone="021-88849041",
            ),
            DesignatedPharmacy(
                name="داروخانه ۲۲ بهمن مشهد",
                province="خراسان رضوی",
                city="مشهد",
                address="خیابان دانشگاه، نبش دانشگاه ۱۶",
                phone="051-38540000",
            ),
            DesignatedPharmacy(
                name="داروخانه هلال احمر اصفهان",
                province="اصفهان",
                city="اصفهان",
                address="خیابان آیت‌الله کاشانی، نبش کوچه ۲۸",
                phone="031-32330000",
            ),
        ],
        required_documents=[
            "نسخه الکترونیک پزشک متخصص مغز و اعصاب / ایمونولوژی",
            "تاییدیه پرونده نشان بیماری خاص در سامانه بیمه سلامت یا تامین اجتماعی",
            "اصل کارت ملی بیمار",
        ],
        inquiry_channel="سامانه ۱۹۰ - اطلاعات دارویی وزارت بهداشت",
        notes="توزیع صرفاً سهمیه‌ای و با ثبت کد ملی در سامانه TTAC انجام می‌پذیرد.",
    ),
    RareMedicineItem(
        id="rare-trastuzumab",
        generic_name="تراستوزوماب (Trastuzumab)",
        brand_names=["هرسپتین", "Herceptin", "آریوتراست", "AryoTrust", "زیترووان"],
        category="انکولوژی (سرطان)",
        dosage_form="ویال پودر جهت محلول غلیظ برای انفوزیون",
        strength="440mg",
        scarcity_level="scarce",
        supply_status="available_limited",
        designated_pharmacies=[
            DesignatedPharmacy(
                name="داروخانه ۱۳ آبان",
                province="تهران",
                city="تهران",
                address="خیابان کریمخان زند، نبش خردمند جنوبی",
                phone="021-88849041",
            ),
            DesignatedPharmacy(
                name="داروخانه شهید نظری",
                province="تهران",
                city="تهران",
                address="خیابان ولیعصر، تقاطع مطهری",
                phone="021-88902500",
            ),
            DesignatedPharmacy(
                name="داروخانه هلال احمر شیراز",
                province="فارس",
                city="شیراز",
                address="خیابان کریمخان زند، روبروی بیمارستان شهید فقیهی",
                phone="071-32300000",
            ),
            DesignatedPharmacy(
                name="داروخانه هلال احمر تبریز",
                province="آذربایجان شرقی",
                city="تبریز",
                address="خیابان ارتش جنوبی، روبروی اداره پست",
                phone="041-35550000",
            ),
        ],
        required_documents=[
            "نسخه الکترونیک انکولوژیست",
            "پاتولوژی تایید وضعیت گیرنده HER2 مثبت",
            "تاییدیه کمیته بیماران خاص اداره بیمه",
        ],
        inquiry_channel="سامانه ۱۹۰ - اطلاعات دارویی وزارت بهداشت",
        notes="زنجیره سرد (۲ تا ۸ درجه سانتی‌گراد) جهت دریافت الزامی است.",
    ),
    RareMedicineItem(
        id="rare-temozolomide",
        generic_name="تموزولامید (Temozolomide)",
        brand_names=["تمودال", "Temodal", "تموزول", "Temozol"],
        category="انکولوژی (تومورهای مغزی)",
        dosage_form="کپسول خوراکی",
        strength="100mg",
        scarcity_level="monitored",
        supply_status="central_pharmacy_only",
        designated_pharmacies=[
            DesignatedPharmacy(
                name="داروخانه ۲۹ فروردین",
                province="تهران",
                city="تهران",
                address="خیابان کارگر جنوبی، میدان حر",
                phone="021-66400000",
            ),
            DesignatedPharmacy(
                name="داروخانه هلال احمر مرکزی",
                province="تهران",
                city="تهران",
                address="خیابان آیت‌الله طالقانی",
                phone="021-88803875",
            ),
        ],
        required_documents=[
            "نسخه الکترونیک متخصص رادیوانکولوژی یا جراح مغز و اعصاب",
            "برگ صورتحساب بیمه درمانی",
        ],
        inquiry_channel="سامانه ۱۹۰",
        notes="بررسی موجودی روزانه قبل از مراجعه حضوری توصیه می‌شود.",
    ),
    RareMedicineItem(
        id="rare-factor-viii",
        generic_name="فاکتور هشت انعقادی (Factor VIII)",
        brand_names=["اموکلات", "Emoclot", "Kogenate", "کوژنات", "آفستین"],
        category="هموفیلی و اختلالات خونی",
        dosage_form="ویال پودر و حلال تزریقی",
        strength="500IU",
        scarcity_level="critical",
        supply_status="available_limited",
        designated_pharmacies=[
            DesignatedPharmacy(
                name="داروخانه کانون هموفیلی ایران",
                province="تهران",
                city="تهران",
                address="خیابان فلسطین شمالی، خیابان ایتالیا، پلاک ۲۴",
                phone="021-88950000",
            ),
            DesignatedPharmacy(
                name="داروخانه ۲۹ فروردین",
                province="تهران",
                city="تهران",
                address="خیابان کارگر جنوبی، میدان حر",
                phone="021-66400000",
            ),
        ],
        required_documents=[
            "کارت پرونده بیماری خاص (هموفیلی)",
            "نسخه متخصص خون و انکولوژی",
            "کارت ملی بیمار",
        ],
        inquiry_channel="سامانه ۱۹۰ و کانون هموفیلی ایران",
        notes="تحویل رایگان در قالب حمایت از بیماران خاص با حواله معتبر.",
    ),
    RareMedicineItem(
        id="rare-somatropin",
        generic_name="سوماتروپین (Somatropin)",
        brand_names=["نوردیتروپین", "Norditropin", "اومنی‌تروپ", "Omnitrope", "ژنتروپین", "Genotropin"],
        category="غدد و متابولیک",
        dosage_form="قلم آماده تزریق",
        strength="10mg (30IU) / 1.5ml",
        scarcity_level="monitored",
        supply_status="available_limited",
        designated_pharmacies=[
            DesignatedPharmacy(
                name="داروخانه ۱۳ آبان",
                province="تهران",
                city="تهران",
                address="خیابان کریمخان زند، نبش خردمند جنوبی",
                phone="021-88849041",
            ),
            DesignatedPharmacy(
                name="داروخانه هلال احمر مرکزی",
                province="تهران",
                city="تهران",
                address="خیابان آیت‌الله طالقانی",
                phone="021-88803875",
            ),
        ],
        required_documents=[
            "پرونده تاییدیه کمیسیون پزشکی غدد اطفال یا بزرگسالان",
            "نسخه معتبر در سامانه نسخه الکترونیک",
        ],
        inquiry_channel="سامانه ۱۹۰",
        notes="تحویل دارو به همراه کیف خنک‌کننده انجام می‌گیرد.",
    ),
    RareMedicineItem(
        id="rare-tacrolimus",
        generic_name="تاکرولیموس (Tacrolimus)",
        brand_names=["پروگراف", "Prograf", "ادواگراف", "Advagraf", "تاکرولین"],
        category="پیوند اعضا و ایمونوساپرسیو",
        dosage_form="کپسول خوراکی",
        strength="1mg",
        scarcity_level="monitored",
        supply_status="available_limited",
        designated_pharmacies=[
            DesignatedPharmacy(
                name="داروخانه شهید کاظمی",
                province="تهران",
                city="تهران",
                address="خیابان رسالت، نرسیده به اتوبان شهید صیاد شیرازی",
                phone="021-22500000",
            ),
            DesignatedPharmacy(
                name="داروخانه ۱۳ آبان",
                province="تهران",
                city="تهران",
                address="خیابان کریمخان زند",
                phone="021-88849041",
            ),
        ],
        required_documents=[
            "کارت پیوند عضو معتبر",
            "نسخه الکترونیک فوق تخصص نفرولوژی یا گوارش/پیوند",
        ],
        inquiry_channel="سامانه ۱۹۰",
        notes="توزیع مداوم برای بیماران ثبت‌شده در سامانه پیوند.",
    ),
    RareMedicineItem(
        id="rare-pirfenidone",
        generic_name="پیرفنیدون (Pirfenidone)",
        brand_names=["اسبریت", "Esbriet", "پیرفنکس", "Pirfenex"],
        category="ریه و فیبروز ریوی",
        dosage_form="قرص روکش‌دار",
        strength="267mg",
        scarcity_level="scarce",
        supply_status="inquiry_required",
        designated_pharmacies=[
            DesignatedPharmacy(
                name="داروخانه هلال احمر مرکزی",
                province="تهران",
                city="تهران",
                address="خیابان آیت‌الله طالقانی",
                phone="021-88803875",
            ),
            DesignatedPharmacy(
                name="داروخانه ۲۹ فروردین",
                province="تهران",
                city="تهران",
                address="خیابان کارگر جنوبی",
                phone="021-66400000",
            ),
        ],
        required_documents=[
            "نسخه فوق تخصص ریه",
            "سی‌تی اسکن و تست عملکرد ریوی (PFT)",
            "تاییدیه بیمه برای بیماری خاص ریوی",
        ],
        inquiry_channel="سامانه ۱۹۰",
        notes="درخواست ابتدا از طریق سامانه استعلام کمبودهای ۱۹۰ ثبت گردد.",
    ),
]


def normalize_query_text(text: str | None) -> str:
    """Normalize Persian and Latin text for flexible, typo-tolerant search."""
    if not text:
        return ""

    s = text.strip()
    # Unify Arabic and Persian characters
    s = s.replace("ي", "ی").replace("ك", "ک").replace("ة", "ه").replace("ۀ", "ه")
    # Remove kashida and diacritics
    s = re.sub(r"[\u064B-\u065F\u0670\u0640]", "", s)
    # Normalize Persian/Arabic digits to ASCII
    persian_arabic_digits = "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩"
    ascii_digits = "01234567890123456789"
    trans = str.maketrans(persian_arabic_digits, ascii_digits)
    s = s.translate(trans)
    # Remove non-alphanumeric punctuation for token comparison while preserving spaces
    s = re.sub(r"[\-_/\\(),.:;!؟?\[\]]", " ", s)
    # Compress whitespaces and lowercase
    s = " ".join(s.split()).lower()
    return s


def build_patient_guidance_text() -> str:
    return (
        "راهنمای دریافت داروهای کمیاب و خاص:\n"
        "۱. تهیه نسخه الکترونیک معتبر توسط پزشک متخصص مرتبط با بیماری.\n"
        "۲. همراه داشتن اصل کارت ملی و در صورت نیاز کارت/پرونده نشان بیماری خاص.\n"
        "۳. پیش از مراجعه حضوری به داروخانه‌های منتخب، از طریق سامانه ۱۹۰ یا تلفن داروخانه از موجودی سهمیه اطمینان حاصل فرمایید.\n"
        "۴. ثبت استعلام و رهگیری در سامانه TTAC وزارت بهداشت الزامی می‌باشد."
    )


class RareMedicineQueryService:
    """Service handling catalog searches, filtering, SQLite persistence, and reply formatting."""

    def __init__(
        self,
        catalog: list[RareMedicineItem] | None = None,
        connection: sqlite3.Connection | None = None,
    ):
        self._items: dict[str, RareMedicineItem] = {}
        items_to_load = catalog if catalog is not None else DEFAULT_RARE_MEDICINE_CATALOG
        for item in items_to_load:
            self._items[item.id] = item

        if connection is not None:
            self.init_table(connection)
            self.seed_table(connection)
            self.load_from_db(connection)

    @property
    def total_count(self) -> int:
        return len(self._items)

    def get_by_id(self, item_id: str) -> RareMedicineItem | None:
        return self._items.get(item_id)

    def add_or_update(self, item: RareMedicineItem) -> None:
        self._items[item.id] = item

    def list_all(self) -> list[RareMedicineItem]:
        return list(self._items.values())

    def list_categories(self) -> list[str]:
        categories = {item.category for item in self._items.values() if item.category}
        return sorted(categories)

    def list_provinces(self) -> list[str]:
        provinces = set()
        for item in self._items.values():
            for p in item.designated_pharmacies:
                if p.province:
                    provinces.add(p.province)
        return sorted(provinces)

    def list_pharmacies(self, province: str | None = None) -> list[dict[str, str]]:
        seen = set()
        result: list[dict[str, str]] = []
        normalized_prov = normalize_query_text(province) if province else None

        for item in self._items.values():
            for p in item.designated_pharmacies:
                if normalized_prov and normalize_query_text(p.province) != normalized_prov:
                    continue
                key = (p.name, p.province, p.city)
                if key not in seen:
                    seen.add(key)
                    result.append(p.to_dict())

        return sorted(result, key=lambda x: (x["province"], x["name"]))

    def search(
        self,
        query: str | None = None,
        province: str | None = None,
        category: str | None = None,
        scarcity_level: str | None = None,
        supply_status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> RareMedicineQueryResult:
        clean_query = normalize_query_text(query)
        clean_province = normalize_query_text(province) if province else None
        clean_category = normalize_query_text(category) if category else None
        clean_scarcity = normalize_query_text(scarcity_level) if scarcity_level else None
        clean_status = normalize_query_text(supply_status) if supply_status else None

        candidates: list[tuple[int, RareMedicineItem]] = []

        for item in self._items.values():
            # Filter by province
            if clean_province:
                matches_prov = any(
                    clean_province in normalize_query_text(p.province)
                    or clean_province in normalize_query_text(p.city)
                    for p in item.designated_pharmacies
                )
                if not matches_prov:
                    continue

            # Filter by category
            if clean_category:
                if clean_category not in normalize_query_text(item.category):
                    continue

            # Filter by scarcity level
            if clean_scarcity:
                if clean_scarcity != normalize_query_text(item.scarcity_level):
                    continue

            # Filter by supply status
            if clean_status:
                if clean_status != normalize_query_text(item.supply_status):
                    continue

            # Text query match scoring
            if not clean_query:
                score = 1
            else:
                score = self._compute_match_score(item, clean_query)
                if score <= 0:
                    continue

            candidates.append((score, item))

        # Sort by match score descending, then by generic_name
        candidates.sort(key=lambda x: (-x[0], x[1].generic_name))

        matched_items = [c[1] for c in candidates]
        total_matched = len(matched_items)

        # Slice limit/offset
        safe_offset = max(0, offset)
        safe_limit = max(1, min(limit, 100))
        paged_items = matched_items[safe_offset : safe_offset + safe_limit]

        return RareMedicineQueryResult(
            query=query or "",
            total=self.total_count,
            matched_count=total_matched,
            items=paged_items,
            official_guidance=build_patient_guidance_text(),
        )

    def _compute_match_score(self, item: RareMedicineItem, clean_query: str) -> int:
        norm_generic = normalize_query_text(item.generic_name)
        norm_brands = [normalize_query_text(b) for b in item.brand_names]
        norm_category = normalize_query_text(item.category)
        norm_id = normalize_query_text(item.id)

        # Exact match
        if clean_query == norm_generic:
            return 100
        for b in norm_brands:
            if clean_query == b:
                return 95

        # Prefix match
        if norm_generic.startswith(clean_query):
            return 80
        for b in norm_brands:
            if b.startswith(clean_query):
                return 75

        # Substring in generic or brands
        if clean_query in norm_generic:
            return 60
        for b in norm_brands:
            if clean_query in b:
                return 55

        # ID or category match
        if clean_query in norm_id:
            return 40
        if clean_query in norm_category:
            return 30

        # Token match
        query_tokens = clean_query.split()
        if len(query_tokens) > 1:
            all_target_text = f"{norm_generic} {' '.join(norm_brands)} {norm_category}"
            if all(token in all_target_text for token in query_tokens):
                return 25

        return 0

    def format_detail_reply(self, item: RareMedicineItem) -> str:
        scarcity_fa = {
            "critical": "بسیار بحرانی (سهمیه‌ای ویژه)",
            "scarce": "کمیاب (سهمیه‌ای استانی)",
            "monitored": "تحت رصد و توزیع کنترل‌شده",
        }.get(item.scarcity_level, item.scarcity_level)

        supply_fa = {
            "available_limited": "موجود محدود در مراکز سهمیه‌ای",
            "inquiry_required": "نیازمند استعلام روزانه از سامانه ۱۹۰",
            "central_pharmacy_only": "صرفاً در داروخانه‌های مرجع مرکزی",
            "out_of_stock": "ناموجود موقت در انبار توزیع",
        }.get(item.supply_status, item.supply_status)

        pharmacies_lines = []
        for p in item.designated_pharmacies[:4]:
            pharmacies_lines.append(f"• {p.name} ({p.province} - {p.city}): {p.phone}")

        docs_lines = [f"• {doc}" for doc in item.required_documents]

        lines = [
            f"🔍 اطلاعات داروی کمیاب: {item.generic_name}",
            f"نام‌های تجاری: {', '.join(item.brand_names)}",
            f"شکل دارویی و دوز: {item.dosage_form} ({item.strength})",
            f"دسته درمانی: {item.category}",
            f"وضعیت کمیابی: {scarcity_fa}",
            f"وضعیت تامین: {supply_fa}",
            "",
            "🏥 داروخانه‌های توزیع‌کننده منتخب:",
            *pharmacies_lines,
            "",
            "📋 مدارک لازم جهت دریافت:",
            *docs_lines,
            "",
            f"📞 درگاه رسمی استعلام: {item.inquiry_channel}",
        ]
        if item.notes:
            lines.extend(["", f"⚠️ نکته مهم: {item.notes}"])

        lines.extend([
            "",
            "توجه: این اطلاعات صرفاً جهت راهنمایی مراجعین برای تهیه داروست. "
            "هیچ دارویی بدون نسخه رسمی پزشک و تایید سامانه تحویل نمی‌گردد."
        ])
        return "\n".join(lines)

    def format_search_summary_reply(self, result: RareMedicineQueryResult) -> str:
        if result.matched_count == 0:
            return (
                f"برای جستجوی «{result.query}» داروی کمیاب ثبت‌شده‌ای یافت نشد.\n\n"
                "جهت استعلام دقیق‌تر کمبودهای دارویی سراسر کشور با سامانه تلفنی ۱۹۰ (داخلی ۳ - اطلاعات دارویی) تماس حاصل فرمایید."
            )

        if result.matched_count == 1:
            return self.format_detail_reply(result.items[0])

        lines = [
            f"نتایج جستجوی داروی کمیاب برای «{result.query}» ({result.matched_count} مورد):",
            "",
        ]
        for i, item in enumerate(result.items, 1):
            lines.append(
                f"{i}. {item.generic_name} ({', '.join(item.brand_names[:2])}) - {item.dosage_form}"
            )

        lines.extend([
            "",
            "برای دریافت جزییات دقیق و داروخانه‌های توزیع، نام کامل دارو را وارد نمایید یا دستور /rare <نام_دارو> را ارسال کنید.",
            "استعلام سامانه وزارت بهداشت: سامانه ۱۹۰",
        ])
        return "\n".join(lines)

    # SQLite Database Methods
    @staticmethod
    def init_table(connection: sqlite3.Connection) -> None:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS rare_medicines (
                    id TEXT PRIMARY KEY,
                    generic_name TEXT NOT NULL,
                    brand_names_json TEXT NOT NULL,
                    category TEXT NOT NULL,
                    dosage_form TEXT NOT NULL,
                    strength TEXT NOT NULL,
                    scarcity_level TEXT NOT NULL,
                    supply_status TEXT NOT NULL,
                    pharmacies_json TEXT NOT NULL,
                    documents_json TEXT NOT NULL,
                    inquiry_channel TEXT NOT NULL,
                    notes TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_rare_medicines_category
                ON rare_medicines (category)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_rare_medicines_scarcity
                ON rare_medicines (scarcity_level)
                """
            )

    def seed_table(self, connection: sqlite3.Connection) -> int:
        self.init_table(connection)
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM rare_medicines")
            count = cursor.fetchone()[0]
            if count > 0:
                return 0

            seeded = 0
            for item in self._items.values():
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO rare_medicines (
                        id, generic_name, brand_names_json, category, dosage_form,
                        strength, scarcity_level, supply_status, pharmacies_json,
                        documents_json, inquiry_channel, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item.id,
                        item.generic_name,
                        json.dumps(item.brand_names, ensure_ascii=False),
                        item.category,
                        item.dosage_form,
                        item.strength,
                        item.scarcity_level,
                        item.supply_status,
                        json.dumps([p.to_dict() for p in item.designated_pharmacies], ensure_ascii=False),
                        json.dumps(item.required_documents, ensure_ascii=False),
                        item.inquiry_channel,
                        item.notes,
                    ),
                )
                seeded += 1
            return seeded

    def load_from_db(self, connection: sqlite3.Connection) -> int:
        self.init_table(connection)
        with connection:
            cursor = connection.cursor()
            rows = cursor.execute("SELECT * FROM rare_medicines").fetchall()
            loaded = 0
            for row in rows:
                (
                    m_id,
                    generic_name,
                    brand_names_json,
                    category,
                    dosage_form,
                    strength,
                    scarcity_level,
                    supply_status,
                    pharmacies_json,
                    documents_json,
                    inquiry_channel,
                    notes,
                ) = row
                item = RareMedicineItem(
                    id=m_id,
                    generic_name=generic_name,
                    brand_names=json.loads(brand_names_json),
                    category=category,
                    dosage_form=dosage_form,
                    strength=strength,
                    scarcity_level=scarcity_level,
                    supply_status=supply_status,
                    designated_pharmacies=[
                        DesignatedPharmacy(**p) for p in json.loads(pharmacies_json)
                    ],
                    required_documents=json.loads(documents_json),
                    inquiry_channel=inquiry_channel,
                    notes=notes,
                )
                self._items[item.id] = item
                loaded += 1
            return loaded


# Global singleton instance
_rare_medicine_service: RareMedicineQueryService | None = None


def get_rare_medicine_service(connection: sqlite3.Connection | None = None) -> RareMedicineQueryService:
    global _rare_medicine_service
    if connection is not None:
        return RareMedicineQueryService(connection=connection)

    # Read the persisted catalog on every call so operator edits are reflected
    # in API responses and bot queries instead of serving a stale code snapshot.
    from .config import get_settings

    with closing(sqlite3.connect(get_settings().database_path)) as database:
        return RareMedicineQueryService(connection=database)


def reset_rare_medicine_service_for_test() -> None:
    global _rare_medicine_service
    _rare_medicine_service = None
