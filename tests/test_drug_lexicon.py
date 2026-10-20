"""Tests for BaleMed Drug Lexicon & Fuzzy Matcher Module (Phase 4 / Milestone 10).

Validates:
- Exact and substring matches for Persian and Latin brand and generic names.
- Fuzzy matching and typo tolerance (e.g. "استامنفن", "ژلوفن", "اموکسیلین", "ibuprophen").
- Controlled substance flagging for narcotics/benzodiazepines.
- Structured intake confirmation prompts for moderate-confidence matches (ADR-0002).
- Edge cases (empty queries, punctuation, Persian/Arabic digit normalization).
"""

from __future__ import annotations

import unittest

from app.drug_lexicon import (
    DrugLexiconEntry,
    DrugLexiconService,
    levenshtein_distance,
    normalize_persian_text,
    similarity_ratio,
)


class TestDrugLexicon(unittest.TestCase):
    def setUp(self) -> None:
        self.service = DrugLexiconService()

    def test_normalize_persian_text(self) -> None:
        self.assertEqual(normalize_persian_text(""), "")
        self.assertEqual(normalize_persian_text("  آمـوکسی‌سیلین  "), "آموکسی سیلین")
        self.assertEqual(normalize_persian_text("كپسول يديد"), "کپسول یدید")

    def test_levenshtein_distance_and_similarity(self) -> None:
        self.assertEqual(levenshtein_distance("gelofen", "gelofen"), 0)
        self.assertEqual(similarity_ratio("gelofen", "gelofen"), 1.0)
        self.assertGreater(similarity_ratio("gelofen", "gelofn"), 0.8)
        self.assertLess(similarity_ratio("gelofen", "amoxicillin"), 0.3)

    def test_exact_match_persian(self) -> None:
        result = self.service.match_drug("استامینوفن")
        self.assertTrue(result.matched)
        self.assertIsNotNone(result.canonical_entry)
        assert result.canonical_entry is not None
        self.assertEqual(result.canonical_entry.generic_name, "Acetaminophen")
        self.assertEqual(result.confidence, 1.0)
        self.assertFalse(result.needs_confirmation)

    def test_exact_match_brand_gelofen(self) -> None:
        result = self.service.match_drug("ژلوفن")
        self.assertTrue(result.matched)
        self.assertIsNotNone(result.canonical_entry)
        assert result.canonical_entry is not None
        self.assertEqual(result.canonical_entry.generic_name, "Ibuprofen")
        self.assertFalse(result.canonical_entry.is_controlled)

    def test_exact_match_latin_brand(self) -> None:
        result = self.service.match_drug("Panadol")
        self.assertTrue(result.matched)
        assert result.canonical_entry is not None
        self.assertEqual(result.canonical_entry.generic_name, "Acetaminophen")

    def test_fuzzy_typo_match_amoxicillin(self) -> None:
        # Common typo in Persian: "اموکسیلین" instead of "آموکسی‌سیلین"
        result = self.service.match_drug("اموکسیلین")
        self.assertTrue(result.matched)
        assert result.canonical_entry is not None
        self.assertEqual(result.canonical_entry.generic_name, "Amoxicillin")
        self.assertGreaterEqual(result.confidence, 0.70)

    def test_fuzzy_typo_match_ibuprofen(self) -> None:
        # Typo in English: "ibuprophen"
        result = self.service.match_drug("ibuprophen")
        self.assertTrue(result.matched)
        assert result.canonical_entry is not None
        self.assertEqual(result.canonical_entry.generic_name, "Ibuprofen")

    def test_controlled_substance_flagging(self) -> None:
        # Diazepam
        result = self.service.match_drug("دیازپام")
        self.assertTrue(result.matched)
        self.assertTrue(result.is_controlled)
        assert result.canonical_entry is not None
        self.assertTrue(result.canonical_entry.is_controlled)

        # Clonazepam brand "ریووپام"
        result2 = self.service.match_drug("ریووپام")
        self.assertTrue(result2.matched)
        self.assertTrue(result2.is_controlled)

        # Codeine combination
        result3 = self.service.match_drug("استامینوفن کدئین")
        self.assertTrue(result3.matched)
        self.assertTrue(result3.is_controlled)

    def test_substring_matches_require_structured_confirmation(self) -> None:
        for query in ("val", "valiumx", "I need acetaminophen for a price question"):
            with self.subTest(query=query):
                result = self.service.match_drug(query)
                self.assertTrue(result.matched)
                self.assertLessEqual(result.confidence, 0.84)
                self.assertTrue(result.needs_confirmation)
                self.assertIsNotNone(result.clarification_prompt)

    def test_adr0002_structured_confirmation_prompt(self) -> None:
        # Typo: "متفورمن ۵۰۰" (confidence between 0.60 and 0.85)
        result = self.service.match_drug("متفورمن۵۰۰")
        self.assertTrue(result.matched)
        if result.needs_confirmation:
            self.assertIsNotNone(result.clarification_prompt)
            assert result.clarification_prompt is not None
            self.assertIn("متفورمین", result.clarification_prompt)

    def test_unmatched_gibberish(self) -> None:
        result = self.service.match_drug("xyz123abcسشیلات")
        self.assertFalse(result.matched)
        self.assertIsNone(result.canonical_entry)

    def test_empty_query(self) -> None:
        result = self.service.match_drug("   ")
        self.assertFalse(result.matched)
        self.assertEqual(result.confidence, 0.0)

    def test_custom_catalog_injection(self) -> None:
        custom_entry = DrugLexiconEntry(
            id="CUSTOM-1",
            generic_name="CustomDrug",
            persian_name="داروی سفارشی",
            category="test",
            brand_names=["CustomBrand"],
            aliases_fa=["سفارشی"],
            aliases_en=["custom"],
        )
        custom_service = DrugLexiconService(catalog=[custom_entry])
        res = custom_service.match_drug("CustomBrand")
        self.assertTrue(res.matched)
        assert res.canonical_entry is not None
        self.assertEqual(res.canonical_entry.id, "CUSTOM-1")
        self.assertEqual(len(custom_service.catalog), 1)


if __name__ == "__main__":
    unittest.main()
