"""Smoke tests for Milestone 8 deploy assets (no server required)."""

from __future__ import annotations

import os
import stat
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOY = REPO_ROOT / "deploy"


class DeployAssetsTests(unittest.TestCase):
    def test_deploy_readme_exists(self) -> None:
        self.assertTrue((DEPLOY / "README.md").is_file())

    def test_server_info_checklist_exists(self) -> None:
        self.assertTrue((DEPLOY / "server-info-checklist.md").is_file())

    def test_templates_exist(self) -> None:
        templates = DEPLOY / "templates"
        for name in ("bale-bot.service", "Caddyfile", "env.production.example"):
            self.assertTrue((templates / name).is_file(), name)

    def test_scripts_exist_and_executable(self) -> None:
        scripts = DEPLOY / "scripts"
        names = [
            "common.sh",
            "00-preflight.sh",
            "01-hardening.sh",
            "02-bootstrap.sh",
            "03-configure-env.sh",
            "04-manual-test.sh",
            "05-systemd.sh",
            "06-caddy.sh",
            "07-smoke-tests.sh",
            "08-register-webhook.sh",
            "09-monitor-dry-run.sh",
            "fix-env-reply-text.py",
            "normalize-deploy-scripts.py",
            "install.sh",
        ]
        for name in names:
            path = scripts / name
            self.assertTrue(path.is_file(), name)
            if os.name == "nt":
                # Windows checkouts do not preserve Unix executable bits.
                first_line = path.read_text(encoding="utf-8").splitlines()[0]
                self.assertTrue(first_line.startswith("#!/"), f"{name} should have shebang")
            else:
                mode = path.stat().st_mode
                self.assertTrue(mode & stat.S_IXUSR, f"{name} should be executable")

    def test_production_env_template_keeps_sending_disabled(self) -> None:
        text = (DEPLOY / "templates" / "env.production.example").read_text(encoding="utf-8")
        self.assertIn("BALE_ENABLE_SENDING=false", text)
        self.assertIn("BALE_ENABLE_ADMIN_NOTIFICATIONS=false", text)
        self.assertIn("BALE_STORE_RAW_UPDATES=false", text)

    def test_smoke_tests_script_blocks_local_routes_publicly(self) -> None:
        text = (DEPLOY / "scripts" / "07-smoke-tests.sh").read_text(encoding="utf-8")
        self.assertIn("/local/reviews/pending", text)
        self.assertIn('[[ "$local_status" == "404" ]]', text)

    def test_configure_env_script_quotes_reply_text_for_bash(self) -> None:
        text = (DEPLOY / "scripts" / "03-configure-env.sh").read_text(encoding="utf-8")
        self.assertIn("fix-env-reply-text.py", text)

    def test_install_script_normalizes_crlf_before_running_steps(self) -> None:
        text = (DEPLOY / "scripts" / "install.sh").read_text(encoding="utf-8")
        self.assertIn("normalize-deploy-scripts.py", text)


if __name__ == "__main__":
    unittest.main()
