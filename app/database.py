import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from .config import get_settings
from .models import IncomingMessage


def get_connection() -> sqlite3.Connection:
    settings = get_settings()
    db_path = Path(settings.database_path)
    return sqlite3.connect(db_path)


def init_db() -> None:
    with closing(get_connection()) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS incoming_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    received_at TEXT NOT NULL,
                    chat_id TEXT,
                    message_id TEXT,
                    text TEXT,
                    raw_update TEXT NOT NULL,
                    needs_review INTEGER NOT NULL DEFAULT 0,
                    review_reason TEXT,
                    review_status TEXT NOT NULL DEFAULT 'not_required'
                )
                """
            )
            existing_columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(incoming_messages)").fetchall()
            }
            if "needs_review" not in existing_columns:
                connection.execute("ALTER TABLE incoming_messages ADD COLUMN needs_review INTEGER NOT NULL DEFAULT 0")
            if "review_reason" not in existing_columns:
                connection.execute("ALTER TABLE incoming_messages ADD COLUMN review_reason TEXT")
            if "review_status" not in existing_columns:
                connection.execute(
                    "ALTER TABLE incoming_messages ADD COLUMN review_status TEXT NOT NULL DEFAULT 'not_required'"
                )


def save_incoming_message(
    message: IncomingMessage,
    needs_review: bool = False,
    review_reason: str | None = None,
    review_status: str = "not_required",
) -> int:
    settings = get_settings()
    received_at = datetime.now(timezone.utc).isoformat()
    raw_payload = message.raw_update if settings.bale_store_raw_updates else {"raw_update_storage": "disabled"}
    raw_update = json.dumps(raw_payload, ensure_ascii=False)

    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO incoming_messages (
                    received_at,
                    chat_id,
                    message_id,
                    text,
                    raw_update,
                    needs_review,
                    review_reason,
                    review_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    received_at,
                    message.chat_id,
                    message.message_id,
                    message.text,
                    raw_update,
                    int(needs_review),
                    review_reason,
                    review_status,
                ),
            )
            return int(cursor.lastrowid)
