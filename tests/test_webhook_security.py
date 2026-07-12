import os
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


class WebhookSecurityTests(unittest.TestCase):
    def test_correct_secret_accepts_webhook(self):
        project_root = Path(__file__).resolve().parents[1]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        original_cwd = Path.cwd()
        original_values = {
            key: os.environ.get(key) for key in ("DATABASE_PATH", "BALE_WEBHOOK_SECRET")
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                for key in original_values:
                    os.environ.pop(key, None)

                Path(".env").write_text(
                    "\n".join(
                        [
                            "DATABASE_PATH=test.db",
                            "BALE_ENABLE_SENDING=false",
                            "BALE_WEBHOOK_SECRET=correct-secret",
                        ]
                    ),
                    encoding="utf-8",
                )

                sys.modules.pop("app.main", None)
                import app.main as main

                with TestClient(main.app) as client:
                    response = client.post(
                        "/webhook/bale/correct-secret",
                        json={"message": {"chat": {"id": "demo-chat"}, "text": "Hello pharmacy"}},
                    )

                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["ok"])
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    def test_missing_webhook_secret_returns_service_unavailable(self):
        project_root = Path(__file__).resolve().parents[1]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        original_cwd = Path.cwd()
        original_values = {
            key: os.environ.get(key) for key in ("DATABASE_PATH", "BALE_WEBHOOK_SECRET")
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                for key in original_values:
                    os.environ.pop(key, None)

                Path(".env").write_text(
                    "\n".join(
                        [
                            "DATABASE_PATH=test.db",
                            "BALE_ENABLE_SENDING=false",
                        ]
                    ),
                    encoding="utf-8",
                )

                sys.modules.pop("app.main", None)
                import app.main as main

                with TestClient(main.app) as client:
                    response = client.post(
                        "/webhook/bale/any-secret",
                        json={"message": {"chat": {"id": "demo-chat"}, "text": "Hello pharmacy"}},
                    )

                self.assertEqual(response.status_code, 503)
                self.assertIn("BALE_WEBHOOK_SECRET", response.json()["detail"])
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    def test_wrong_secret_rejects_webhook(self):
        project_root = Path(__file__).resolve().parents[1]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        original_cwd = Path.cwd()
        original_values = {
            key: os.environ.get(key) for key in ("DATABASE_PATH", "BALE_WEBHOOK_SECRET")
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                for key in original_values:
                    os.environ.pop(key, None)

                Path(".env").write_text(
                    "\n".join(
                        [
                            "DATABASE_PATH=test.db",
                            "BALE_ENABLE_SENDING=false",
                            "BALE_WEBHOOK_SECRET=correct-secret",
                        ]
                    ),
                    encoding="utf-8",
                )

                sys.modules.pop("app.main", None)
                import app.main as main

                with TestClient(main.app) as client:
                    response = client.post(
                        "/webhook/bale/wrong-secret",
                        json={"message": {"chat": {"id": "demo-chat"}, "text": "Hello pharmacy"}},
                    )

                self.assertEqual(response.status_code, 404)
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
