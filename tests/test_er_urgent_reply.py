import unittest

from app.handlers import get_review_metadata
from app.replies import (
    ER_URGENT_REPLY,
    ESCALATION_REPLY,
    SAFE_INTAKE_REPLY,
    build_safe_reply,
    determine_disposition,
    is_emergency_urgent,
    needs_pharmacist_review,
)


class TestERUrgentReplyD2(unittest.TestCase):
    """TDD test suite for Issue #50: P1 implement and validate ER_URGENT_REPLY D2."""

    def test_positive_emergency_cases_trigger_d2_and_urgent_reply(self):
        emergency_messages = [
            "بیمار اوردوز کرده لطفا کمک کنید",
            "درد قفسه سینه شدید دارم و به دست چپم می‌زنه",
            "تنگی نفس ناگهانی دارم",
            "تشنج کرده و بیهوش شده",
            "Patient has severe allergy and shortness of breath",
            "Suspected overdose on medication",
            "Severe chest pain since an hour ago",
        ]
        for msg in emergency_messages:
            with self.subTest(msg=msg):
                self.assertTrue(is_emergency_urgent(msg))
                self.assertEqual(determine_disposition(msg), "D2")
                reply = build_safe_reply(msg, "default")
                self.assertEqual(reply, ER_URGENT_REPLY)
                self.assertIn("۱۱۵", reply)
                self.assertIn("اورژانس", reply)
                # Ensure no diagnosis or prescription
                self.assertNotIn("مصرف کنید", reply)
                self.assertNotIn("قرص", reply)
                self.assertNotIn("تجویز", reply)

    def test_d2_escalates_to_pharmacist_review_without_bypass(self):
        msg = "بیمار درد قفسه سینه دارد"
        metadata = get_review_metadata(msg)
        self.assertTrue(metadata["needs_review"])
        self.assertEqual(metadata["review_status"], "pending")
        self.assertEqual(metadata["review_reason"], "er_urgent_redline")
        self.assertEqual(metadata["disposition"], "D2")

    def test_negative_cases_trigger_d0_safe_intake(self):
        safe_messages = [
            "سلام وقت بخیر قیمت داروی استامینوفن چنده؟",
            "ساعت کار داروخانه تا چه ساعتیه؟",
            "آیا داروی سرماخوردگی موجود دارید؟",
            "Hello, what are the pharmacy opening hours?",
        ]
        for msg in safe_messages:
            with self.subTest(msg=msg):
                self.assertFalse(is_emergency_urgent(msg))
                self.assertEqual(determine_disposition(msg), "D0")
                reply = build_safe_reply(msg, "default")
                self.assertEqual(reply, SAFE_INTAKE_REPLY)
                metadata = get_review_metadata(msg)
                self.assertFalse(metadata["needs_review"])
                self.assertEqual(metadata["review_status"], "not_required")
                self.assertEqual(metadata["disposition"], "D0")

    def test_ambiguous_non_emergency_clinical_cases_trigger_d1_escalation(self):
        standard_escalation_messages = [
            "من باردار هستم آیا این شربت برای جنین ضرر دارد؟",
            "دوز مصرف شربت برای کودک چقدر است؟",
            "آیا این دو قرص تداخل دارویی دارند؟",
            "Can I change medication while breastfeeding?",
        ]
        for msg in standard_escalation_messages:
            with self.subTest(msg=msg):
                self.assertFalse(is_emergency_urgent(msg))
                self.assertTrue(needs_pharmacist_review(msg))
                self.assertEqual(determine_disposition(msg), "D1")
                reply = build_safe_reply(msg, "default")
                self.assertEqual(reply, ESCALATION_REPLY)
                metadata = get_review_metadata(msg)
                self.assertTrue(metadata["needs_review"])
                self.assertEqual(metadata["review_reason"], "pharmacist_review_required")
                self.assertEqual(metadata["disposition"], "D1")

    def test_empty_or_none_input_handled_safely(self):
        self.assertEqual(determine_disposition(None), "D0")
        self.assertEqual(determine_disposition("   "), "D0")
        self.assertEqual(build_safe_reply(None, "default_fallback"), "default_fallback")
        self.assertEqual(build_safe_reply("", "default_fallback"), "default_fallback")


if __name__ == "__main__":
    unittest.main()
