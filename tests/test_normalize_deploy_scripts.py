"""Tests for deploy/scripts/normalize-deploy-scripts.py (CRLF → LF for Linux)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "deploy" / "scripts" / "normalize-deploy-scripts.py"


class NormalizeDeployScriptsTests(unittest.TestCase):
    def test_crlf_shell_script_becomes_bash_safe_after_normalize(self) -> None:
        crlf_body = (
            b"#!/usr/bin/env bash\r\n"
            b"set -euo pipefail\r\n"
            b'log() { printf "%s\\n" "$1"; }\r\n'
            b'log "ok"\r\n'
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            scripts_dir = Path(temp_dir)
            script_path = scripts_dir / "00-preflight.sh"
            script_path.write_bytes(crlf_body)

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(scripts_dir)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)

            normalized = script_path.read_bytes()
            self.assertNotIn(b"\r", normalized)
            self.assertIn(b"set -euo pipefail\n", normalized)

            if shutil.which("bash") and os.name != "nt":
                syntax = subprocess.run(
                    ["bash", "-n", str(script_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(syntax.returncode, 0, msg=syntax.stderr)

                run = subprocess.run(
                    ["bash", str(script_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(run.returncode, 0, msg=run.stderr)
                self.assertEqual(run.stdout.strip(), "ok")

    def test_lf_only_script_is_left_unchanged(self) -> None:
        lf_body = b"#!/usr/bin/env bash\nset -euo pipefail\n"
        with tempfile.TemporaryDirectory() as temp_dir:
            scripts_dir = Path(temp_dir)
            script_path = scripts_dir / "install.sh"
            script_path.write_bytes(lf_body)
            before = script_path.read_bytes()

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(scripts_dir)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(script_path.read_bytes(), before)
            self.assertIn("no CRLF changes needed", result.stdout)

    def test_only_shell_scripts_are_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            scripts_dir = Path(temp_dir)
            shell_path = scripts_dir / "01-hardening.sh"
            other_path = scripts_dir / "notes.txt"
            shell_path.write_bytes(b"#!/usr/bin/env bash\r\n")
            other_path.write_bytes(b"keep\r\n")

            subprocess.run(
                [sys.executable, str(SCRIPT), str(scripts_dir)],
                check=True,
            )

            self.assertNotIn(b"\r", shell_path.read_bytes())
            self.assertIn(b"\r\n", other_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
