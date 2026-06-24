import unittest

from app.bidi import LRI, PDI, format_mixed_direction_text


class BidiFormattingTests(unittest.TestCase):
    def test_persian_only_text_is_unchanged(self):
        text = "پیام شما دریافت شد.\nلطفا نام دارو را بفرستید."
        self.assertEqual(format_mixed_direction_text(text), text)

    def test_slash_commands_are_isolated(self):
        text = format_mixed_direction_text("دستورها:\n/start\n/help\n/status")
        self.assertIn(f"{LRI}/start{PDI}", text)
        self.assertIn(f"{LRI}/help{PDI}", text)
        self.assertIn(f"{LRI}/status{PDI}", text)

    def test_latin_path_is_isolated(self):
        text = format_mixed_direction_text("لیست بررسی: /local/reviews/pending")
        self.assertIn(f"{LRI}/local/reviews/pending{PDI}", text)

    def test_mixed_persian_and_english_phrase_is_isolated(self):
        text = format_mixed_direction_text("نام دارو: Amoxicillin")
        self.assertIn(f"{LRI}Amoxicillin{PDI}", text)
        self.assertTrue(text.index("نام دارو") < text.index(LRI))
