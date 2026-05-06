import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.database import init_db
from app.handlers import route_update


class HandlerTests(unittest.TestCase):
    def test_route_update_stores_message_and_prepares_dry_run_reply(self):
        original_cwd = Path.cwd()
        original_values = {
            key: os.environ.get(key)
            for key in (
                "BALE_BOT_TOKEN",
                "BALE_API_BASE_URL",
                "BALE_ENABLE_SENDING",
                "DATABASE_PATH",
                "BALE_REPLY_TEXT",
            )
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                for key in original_values:
                    os.environ.pop(key, None)

                Path(".env").write_text(
                    "\n".join(
                        [
                            "BALE_BOT_TOKEN=test-token",
                            "BALE_API_BASE_URL=https://example.test",
                            "BALE_ENABLE_SENDING=false",
                            "DATABASE_PATH=test.db",
                            "BALE_REPLY_TEXT=سلام حسین جان!",
                        ]
                    ),
                    encoding="utf-8",
                )

                init_db()
                result = route_update(
                    {
                        "message": {
                            "message_id": 123,
                            "chat": {"id": "demo-chat"},
                            "text": "Hello pharmacy",
                        }
                    }
                )

                connection = sqlite3.connect("test.db")
                try:
                    row = connection.execute(
                        "SELECT chat_id, message_id, text FROM incoming_messages"
                    ).fetchone()
                finally:
                    connection.close()
            finally:
                os.chdir(original_cwd)
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

        self.assertTrue(result["ok"])
        self.assertTrue(result["reply_prepared"])
        self.assertTrue(result["reply_result"]["skipped"])
        self.assertEqual(result["reply_result"]["text"], "سلام حسین جان!")
        self.assertEqual(row, ("demo-chat", "123", "Hello pharmacy"))


if __name__ == "__main__":
    unittest.main()
