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
                    raw_update TEXT NOT NULL
                )
                """
            )


def save_incoming_message(message: IncomingMessage) -> int:
    received_at = datetime.now(timezone.utc).isoformat()
    raw_update = json.dumps(message.raw_update, ensure_ascii=False)

    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
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
                (
                    received_at,
                    message.chat_id,
                    message.message_id,
                    message.text,
                    raw_update,
                ),
            )
            return int(cursor.lastrowid)
