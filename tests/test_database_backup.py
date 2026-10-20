import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.database import create_sqlite_backup, init_db, restore_sqlite_backup


class DatabaseBackupTests(unittest.TestCase):
    ENV_KEYS = (
        "BALE_BOT_TOKEN",
        "BALE_API_BASE_URL",
        "BALE_ENABLE_SENDING",
        "DATABASE_PATH",
        "BALE_REPLY_TEXT",
        "BALE_WEBHOOK_SECRET",
        "BALE_STORE_RAW_UPDATES",
    )

    def setUp(self):
        self.original_cwd = Path.cwd()
        self.original_values = {key: os.environ.get(key) for key in self.ENV_KEYS}
        self.temp_dir = tempfile.TemporaryDirectory()
        os.chdir(self.temp_dir.name)
        for key in self.ENV_KEYS:
            os.environ.pop(key, None)
        os.environ["DATABASE_PATH"] = "test.db"

    def tearDown(self):
        os.chdir(self.original_cwd)
        for key, value in self.original_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.temp_dir.cleanup()

    def test_create_sqlite_backup_creates_timestamped_backup_file(self):
        init_db()

        result = create_sqlite_backup()

        self.assertTrue(result.created)
        self.assertEqual(result.source_path, Path("test.db"))
        self.assertEqual(result.backup_path.parent, Path("backups"))
        self.assertTrue(result.backup_path.name.startswith("test-"))
        self.assertEqual(result.backup_path.suffix, ".db")
        self.assertTrue(result.backup_path.exists())

        connection = sqlite3.connect(result.backup_path)
        try:
            row = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'incoming_messages'"
            ).fetchone()
        finally:
            connection.close()

        self.assertEqual(row, ("incoming_messages",))

    def test_create_sqlite_backup_creates_backup_directory_if_missing(self):
        init_db()
        self.assertFalse(Path("backups").exists())

        result = create_sqlite_backup()

        self.assertTrue(Path("backups").is_dir())
        self.assertTrue(result.backup_path.exists())

    def test_create_sqlite_backup_raises_controlled_error_when_database_is_missing(self):
        with self.assertRaises(FileNotFoundError) as captured:
            create_sqlite_backup()

        self.assertIn("SQLite database file was not found", str(captured.exception))
        self.assertFalse(Path("backups").exists())

    def test_create_sqlite_backup_does_not_copy_env_file(self):
        init_db()
        Path(".env").write_text("BALE_BOT_TOKEN=secret-token", encoding="utf-8")

        create_sqlite_backup()

        self.assertFalse(Path("backups/.env").exists())
        self.assertEqual(len(list(Path("backups").glob("*"))), 1)

    def test_restore_sqlite_backup_restores_database_from_backup_file(self):
        init_db()
        connection = sqlite3.connect("test.db")
        try:
            connection.execute(
                """
                INSERT INTO incoming_messages (
                    received_at,
                    chat_id,
                    message_id,
                    text,
                    raw_update
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                ("2026-05-08T00:00:00+00:00", "demo-chat", "123", "Hello pharmacy", "{}"),
            )
            connection.commit()
        finally:
            connection.close()

        backup = create_sqlite_backup()
        Path("test.db").unlink()

        result = restore_sqlite_backup(backup.backup_path)

        self.assertTrue(result.restored)
        self.assertEqual(result.backup_path, backup.backup_path)
        self.assertEqual(result.restored_path, Path("test.db"))
        connection = sqlite3.connect("test.db")
        try:
            row = connection.execute(
                "SELECT chat_id, message_id, text FROM incoming_messages"
            ).fetchone()
        finally:
            connection.close()

        self.assertEqual(row, ("demo-chat", "123", "Hello pharmacy"))

    def test_restore_updates_database_through_existing_sqlite_connection(self):
        init_db()
        with sqlite3.connect("test.db") as connection:
            connection.execute(
                "INSERT INTO incoming_messages (received_at, chat_id, message_id, raw_update) "
                "VALUES ('now', 'demo-chat', 'before', '{}')"
            )
        backup = create_sqlite_backup()
        with sqlite3.connect(backup.backup_path) as connection:
            connection.execute("DELETE FROM incoming_messages")

        with sqlite3.connect("test.db") as live_connection:
            restore_sqlite_backup(backup.backup_path, overwrite=True)
            count = live_connection.execute(
                "SELECT COUNT(*) FROM incoming_messages"
            ).fetchone()[0]

        self.assertEqual(count, 0)

    def test_restore_sqlite_backup_creates_database_parent_directory(self):
        init_db()
        backup = create_sqlite_backup()
        os.environ["DATABASE_PATH"] = "data/restored.db"

        result = restore_sqlite_backup(backup.backup_path)

        self.assertEqual(result.restored_path, Path("data/restored.db"))
        self.assertTrue(Path("data").is_dir())
        self.assertTrue(Path("data/restored.db").exists())

    def test_restore_sqlite_backup_refuses_to_overwrite_existing_database_by_default(self):
        init_db()
        backup = create_sqlite_backup()

        with self.assertRaises(FileExistsError) as captured:
            restore_sqlite_backup(backup.backup_path)

        self.assertIn("Refusing to overwrite existing SQLite database", str(captured.exception))

    def test_restore_sqlite_backup_raises_controlled_error_when_backup_is_missing(self):
        with self.assertRaises(FileNotFoundError) as captured:
            restore_sqlite_backup("backups/missing.db")

        self.assertIn("SQLite backup file was not found", str(captured.exception))


if __name__ == "__main__":
    unittest.main()
