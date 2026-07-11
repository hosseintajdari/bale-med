"""Tests for deploy/scripts/fix-env-reply-text.py (bash-safe .env quoting)."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "deploy" / "scripts" / "fix-env-reply-text.py"


class FixEnvReplyTextTests(unittest.TestCase):
    def test_unquoted_persian_reply_text_is_wrapped_for_bash(self) -> None:
        persian = (
            "پیام شما دریافت شد. این ربات جایگزین نظر داروساز یا پزشک نیست. "
            "در صورت نیاز، پیام شما توسط داروساز بررسی می‌شود."
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "BALE_BOT_TOKEN=secret-token",
                        f"BALE_REPLY_TEXT={persian}",
                        "BALE_ENABLE_SENDING=false",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(env_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)

            fixed = env_path.read_text(encoding="utf-8")
            reply_line = next(
                line for line in fixed.splitlines() if line.startswith("BALE_REPLY_TEXT=")
            )
            self.assertTrue(
                reply_line.startswith('BALE_REPLY_TEXT="') and reply_line.endswith('"'),
                msg=reply_line,
            )
            self.assertIn(persian, reply_line)

            if os.name != "nt":
                source = subprocess.run(
                    ["bash", "-c", f'source "{env_path}" && printf "%s" "$BALE_REPLY_TEXT"'],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(source.returncode, 0, msg=source.stderr)
                self.assertEqual(source.stdout, persian)

    def test_already_quoted_reply_text_is_left_unchanged(self) -> None:
        quoted = '"سلام حسین جان!"'
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(f"BALE_REPLY_TEXT={quoted}\n", encoding="utf-8")
            before = env_path.read_text(encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(env_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(env_path.read_text(encoding="utf-8"), before)

    def test_other_env_lines_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            original = "\n".join(
                [
                    "BALE_BOT_TOKEN=secret-token",
                    "BALE_REPLY_TEXT=پیام تست",
                    "BALE_ENABLE_SENDING=false",
                    "DATABASE_PATH=/opt/bale-bot/data/bale_bot.db",
                ]
            ) + "\n"
            env_path.write_text(original, encoding="utf-8")

            subprocess.run(
                [sys.executable, str(SCRIPT), str(env_path)],
                check=True,
            )

            fixed_lines = env_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(fixed_lines[0], "BALE_BOT_TOKEN=secret-token")
            self.assertTrue(fixed_lines[1].startswith('BALE_REPLY_TEXT="'))
            self.assertEqual(fixed_lines[2], "BALE_ENABLE_SENDING=false")
            self.assertEqual(fixed_lines[3], "DATABASE_PATH=/opt/bale-bot/data/bale_bot.db")

    def test_internal_double_quotes_in_reply_text_are_escaped_for_bash(self) -> None:
        reply = 'گفت: "سلام" — تست'
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(f"BALE_REPLY_TEXT={reply}\n", encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), str(env_path)], check=True)

            fixed = env_path.read_text(encoding="utf-8")
            reply_line = next(
                line for line in fixed.splitlines() if line.startswith("BALE_REPLY_TEXT=")
            )
            self.assertIn('\\"', reply_line)

            if os.name != "nt":
                source = subprocess.run(
                    ["bash", "-c", f'source "{env_path}" && printf "%s" "$BALE_REPLY_TEXT"'],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(source.returncode, 0, msg=source.stderr)
                self.assertEqual(source.stdout, reply)


if __name__ == "__main__":
    unittest.main()
