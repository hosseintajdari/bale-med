"""Drug Lexicon & Fuzzy Matcher Module for BaleMed (Phase 4 / Milestone 10).

Fulfills ADR-0002 requirements:
- Resolves Persian and Latin typos, phonetic misspellings, and brand names for
  common border and primary care medications.
- Computes similarity confidence scores to separate verified matches from
  ambiguous inputs requiring structured confirmation.
- Detects controlled/psychotropic substances requiring redline pharmacist escalation.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass
from typing import Any


def normalize_persian_text(text: str) -> str:
    """Normalize Persian and Arabic characters, spaces, and punctuation."""
    if not text:
        return ""
    # Normalize unicode
    t = unicodedata.normalize("NFKC", text.strip().lower())
    # Replace Arabic kaf and yeh with Persian equivalents
    t = t.replace("ك", "ک").replace("ي", "ی").replace("ى", "ی")
    # Replace Persian half-space / zero-width non-joiner with standard space
    t = t.replace("\u200c", " ")
    # Remove Arabic tatweel / kashida
    t = t.replace("\u0640", "")
    # Remove excessive whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def similarity_ratio(s1: str, s2: str) -> float:
    """Compute a normalized similarity ratio [0.0, 1.0] between two strings."""
    s1_clean = s1.strip().lower()
    s2_clean = s2.strip().lower()
    if s1_clean == s2_clean:
        return 1.0
    max_len = max(len(s1_clean), len(s2_clean))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(s1_clean, s2_clean)
    return round(max(0.0, 1.0 - (dist / max_len)), 4)


@dataclass(frozen=True)
class DrugLexiconEntry:
    id: str
    generic_name: str
    persian_name: str
    category: str
    brand_names: list[str]
    aliases_fa: list[str]
    aliases_en: list[str]
    is_controlled: bool = False
    warning_notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DrugMatchResult:
    query: str
    matched: bool
    canonical_entry: DrugLexiconEntry | None
    matched_term: str | None
    confidence: float
    is_controlled: bool
    needs_confirmation: bool
    clarification_prompt: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "matched": self.matched,
            "canonical_entry": self.canonical_entry.to_dict() if self.canonical_entry else None,
            "matched_term": self.matched_term,
            "confidence": self.confidence,
            "is_controlled": self.is_controlled,
            "needs_confirmation": self.needs_confirmation,
            "clarification_prompt": self.clarification_prompt,
        }


# Comprehensive border-formulary catalog (analgesics, antibiotics, chronic care, controlled)
BORDER_DRUG_CATALOG: list[DrugLexiconEntry] = [
    DrugLexiconEntry(
        id="DRUG-001",
        generic_name="Acetaminophen",
        persian_name="استامینوفن",
        category="analgesic_antipyretic",
        brand_names=["Paracetamol", "Tylenol", "Panadol"],
        aliases_fa=["استامینوفن ساده", "پاراستامول", "استامنفن", "استامینوفن ۳۲۵", "استامینوفن ۵۰۰"],
        aliases_en=["paracetamol", "acetaminophen", "tylenol", "panadol"],
    ),
    DrugLexiconEntry(
        id="DRUG-002",
        generic_name="Acetaminophen Codeine",
        persian_name="استامینوفن کدئین",
        category="analgesic_opioid_combination",
        brand_names=["Acetaminophen Codeine"],
        aliases_fa=["استامینوفن کدیین", "استامینوفن کدئین دار", "کدئین"],
        aliases_en=["acetaminophen codeine", "co-codamol", "tylenol 3"],
        is_controlled=True,
        warning_notes="داروی حاوی مخدر (کدئین) — نیازمند نسخه و نظارت داروساز",
    ),
    DrugLexiconEntry(
        id="DRUG-003",
        generic_name="Ibuprofen",
        persian_name="ایبوپروفن",
        category="nsaid",
        brand_names=["Gelofen", "Advil", "Brufen", "Motrin"],
        aliases_fa=["ژلوفن", "بروفن", "ایبوپرفن", "ژلوفن ۴۰۰", "ایبوپروفن ۴۰۰"],
        aliases_en=["ibuprofen", "gelofen", "advil", "brufen", "motrin"],
    ),
    DrugLexiconEntry(
        id="DRUG-004",
        generic_name="Amoxicillin",
        persian_name="آموکسی‌سیلین",
        category="antibiotic_penicillin",
        brand_names=["Amoxil", "Farmentin"],
        aliases_fa=["اموکسی سیلین", "اموکسیلین", "آموکسی سیلین ۵۰۰", "کپسول آموکسی سیلین"],
        aliases_en=["amoxicillin", "amoxil", "amoxycillin"],
    ),
    DrugLexiconEntry(
        id="DRUG-005",
        generic_name="Co-Amoxiclav",
        persian_name="کوآموکسی‌کلاو",
        category="antibiotic_combination",
        brand_names=["Augmentin", "Farmentin BD", "Klavunat"],
        aliases_fa=["کواموکسی کلاو", "آگمنتین", "فارمنتین", "کو اموکسی کلاو ۶۲۵"],
        aliases_en=["co-amoxiclav", "augmentin", "amoxicillin clavulanate"],
    ),
    DrugLexiconEntry(
        id="DRUG-006",
        generic_name="Azithromycin",
        persian_name="آزیترومایسین",
        category="antibiotic_macrolide",
        brand_names=["Zithromax", "Zmax"],
        aliases_fa=["ازیترومایسین", "آزیترو", "کپسول آزیترومایسین ۲۵۰", "شربت آزیترومایسین"],
        aliases_en=["azithromycin", "zithromax", "azithro"],
    ),
    DrugLexiconEntry(
        id="DRUG-007",
        generic_name="Cefixime",
        persian_name="سفیکسیم",
        category="antibiotic_cephalosporin",
        brand_names=["Suprax", "Farxime"],
        aliases_fa=["سفکسیم", "سفیکسیم ۴۰۰", "شربت سفیکسیم", "فارکسیم"],
        aliases_en=["cefixime", "suprax", "cefixim"],
    ),
    DrugLexiconEntry(
        id="DRUG-008",
        generic_name="Metformin",
        persian_name="متفورمین",
        category="antidiabetic_biguanide",
        brand_names=["Glucophage", "Apo-Metformin", "Glaston"],
        aliases_fa=["متفورمن", "گلوکوفاژ", "قرص قند", "متفورمین ۵۰۰", "متفورمین ۱۰۰۰"],
        aliases_en=["metformin", "glucophage", "apometformin"],
    ),
    DrugLexiconEntry(
        id="DRUG-009",
        generic_name="Losartan",
        persian_name="لوزارتان",
        category="antihypertensive_arb",
        brand_names=["Cozaar", "Pozarex", "Lozar"],
        aliases_fa=["لوزارتان پتاسیم", "پوزارکس", "قرص فشار لوزارتان", "لوزار ۲۵"],
        aliases_en=["losartan", "cozaar", "losartan potassium"],
    ),
    DrugLexiconEntry(
        id="DRUG-010",
        generic_name="Atorvastatin",
        persian_name="آتورواستاتین",
        category="lipid_lowering_statin",
        brand_names=["Lipitor", "Lipofix", "Atorvast"],
        aliases_fa=["اتورواستاتین", "لیپوفیکس", "قرص چربی", "آتورواستاتین ۲۰"],
        aliases_en=["atorvastatin", "lipitor", "lipofix"],
    ),
    DrugLexiconEntry(
        id="DRUG-011",
        generic_name="Omeprazole",
        persian_name="امپرازول",
        category="gastrointestinal_ppi",
        brand_names=["Prilosec", "Losec", "Omezer"],
        aliases_fa=["امپرازول ۲۰", "امپرازول", "قرص معده امپرازول", "کپسول امپرازول"],
        aliases_en=["omeprazole", "losec", "prilosec"],
    ),
    DrugLexiconEntry(
        id="DRUG-012",
        generic_name="Diphenhydramine",
        persian_name="دیفن‌هیدرامین",
        category="antihistamine_antitussive",
        brand_names=["Benadryl"],
        aliases_fa=["دیفن هیدرامین", "دیفین هیدرامین", "دیفن کامپاند", "شربت دیفن"],
        aliases_en=["diphenhydramine", "benadryl", "diphenhydramine compound"],
    ),
    DrugLexiconEntry(
        id="DRUG-013",
        generic_name="Dexamethasone",
        persian_name="دگزامتازون",
        category="corticosteroid",
        brand_names=["Decadron"],
        aliases_fa=["دگزامتازون", "آمپول دگزا", "دگزا", "دگزامتازون شیری"],
        aliases_en=["dexamethasone", "decadron", "dexa"],
        warning_notes="کورتیکواستروئید قوی — مصرف خودسرانه خطرناک است",
    ),
    DrugLexiconEntry(
        id="DRUG-014",
        generic_name="Diazepam",
        persian_name="دیازپام",
        category="benzodiazepine_controlled",
        brand_names=["Valium"],
        aliases_fa=["دیازپام", "والیوم", "والیوم ۱۰", "دیازپام ۲", "دیازپام ۱۰"],
        aliases_en=["diazepam", "valium"],
        is_controlled=True,
        warning_notes="داروی تحت کنترل (بنزودیازپین) — ارجاع فوری به داروساز",
    ),
    DrugLexiconEntry(
        id="DRUG-015",
        generic_name="Clonazepam",
        persian_name="کلونازپام",
        category="benzodiazepine_controlled",
        brand_names=["Klonopin", "Rivotril"],
        aliases_fa=["کلونازپام", "ریووپام", "ریووپریل", "کلونازپام ۱", "کلونازپام ۲"],
        aliases_en=["clonazepam", "klonopin", "rivotril"],
        is_controlled=True,
        warning_notes="داروی تحت کنترل (بنزودیازپین) — ارجاع فوری به داروساز",
    ),
]


class DrugLexiconService:
    """High-performance fuzzy matching and classification service for drug queries."""

    def __init__(self, catalog: list[DrugLexiconEntry] | None = None) -> None:
        self.catalog = catalog or list(BORDER_DRUG_CATALOG)

    def match_drug(self, user_query: str, min_confidence: float = 0.60) -> DrugMatchResult:
        """Find the closest matching drug entry for a user search string.

        Args:
            user_query: Raw user message or drug string
            min_confidence: Minimum similarity threshold (default 0.60)

        Returns:
            DrugMatchResult with confidence, classification, and confirmation hints
        """
        clean_query = normalize_persian_text(user_query)
        if not clean_query:
            return DrugMatchResult(
                query=user_query,
                matched=False,
                canonical_entry=None,
                matched_term=None,
                confidence=0.0,
                is_controlled=False,
                needs_confirmation=False,
            )

        best_entry: DrugLexiconEntry | None = None
        best_term: str | None = None
        highest_score = 0.0

        for entry in self.catalog:
            # Build search targets: generic, persian, brands, aliases
            all_targets = [
                entry.generic_name,
                entry.persian_name,
                *entry.brand_names,
                *entry.aliases_fa,
                *entry.aliases_en,
            ]

            for target in all_targets:
                norm_target = normalize_persian_text(target)

                # Exact match
                if clean_query == norm_target:
                    return DrugMatchResult(
                        query=user_query,
                        matched=True,
                        canonical_entry=entry,
                        matched_term=target,
                        confidence=1.0,
                        is_controlled=entry.is_controlled,
                        needs_confirmation=False,
                        clarification_prompt=None,
                    )

                # Substring containment match
                if len(clean_query) >= 3 and (clean_query in norm_target or norm_target in clean_query):
                    ratio = 0.84
                    if ratio > highest_score:
                        highest_score = ratio
                        best_entry = entry
                        best_term = target
                    # Keep ambiguous containment matches below the structured
                    # confirmation threshold; fuzzy similarity must not raise it.
                    continue

                # Fuzzy similarity
                sim = similarity_ratio(clean_query, norm_target)
                if sim > highest_score:
                    highest_score = sim
                    best_entry = entry
                    best_term = target

        if highest_score >= min_confidence and best_entry is not None:
            # Needs confirmation if confidence is between 0.60 and 0.84 (ADR-0002 structured confirmation)
            needs_confirm = 0.60 <= highest_score < 0.85
            prompt = None
            if needs_confirm:
                prompt = (
                    f"آیا منظور شما داروی «{best_entry.persian_name}» ({best_entry.generic_name}) است؟ "
                    f"لطفاً پیش از بررسی بیشتر، نام دارو را تایید نمایید."
                )

            return DrugMatchResult(
                query=user_query,
                matched=True,
                canonical_entry=best_entry,
                matched_term=best_term,
                confidence=round(highest_score, 4),
                is_controlled=best_entry.is_controlled,
                needs_confirmation=needs_confirm,
                clarification_prompt=prompt,
            )

        return DrugMatchResult(
            query=user_query,
            matched=False,
            canonical_entry=None,
            matched_term=None,
            confidence=round(highest_score, 4),
            is_controlled=False,
            needs_confirmation=False,
            clarification_prompt=None,
        )

    def get_controlled_drugs(self) -> list[DrugLexiconEntry]:
        """Return all controlled / psychotropic substances in the catalog."""
        return [entry for entry in self.catalog if entry.is_controlled]

    def match_controlled_drug(
        self, user_query: str, min_confidence: float = 0.60
    ) -> DrugMatchResult:
        """Match only controlled entries so non-controlled prefixes cannot win."""
        controlled_service = DrugLexiconService(catalog=self.get_controlled_drugs())
        return controlled_service.match_drug(user_query, min_confidence=min_confidence)


_drug_lexicon_service: DrugLexiconService | None = None


def get_drug_lexicon_service() -> DrugLexiconService:
    global _drug_lexicon_service
    if _drug_lexicon_service is None:
        _drug_lexicon_service = DrugLexiconService()
    return _drug_lexicon_service

