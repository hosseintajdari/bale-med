import json
import shutil
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .config import get_settings
from .models import IncomingMessage


@dataclass(frozen=True)
class SaveMessageResult:
    stored_message_id: int
    inserted: bool


@dataclass(frozen=True)
class LLMStorageFields:
    extracted_json: str | None = None
    model_id: str | None = None
    latency_ms: int | None = None
    validation_pass: bool | None = None
    status: str | None = None


@dataclass(frozen=True)
class BackupResult:
    source_path: Path
    backup_path: Path
    created: bool


@dataclass(frozen=True)
class RestoreResult:
    backup_path: Path
    restored_path: Path
    restored: bool


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
                    external_event_id TEXT,
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
            if "external_event_id" not in existing_columns:
                connection.execute(
                    "ALTER TABLE incoming_messages ADD COLUMN external_event_id TEXT"
                )
            if "needs_review" not in existing_columns:
                connection.execute(
                    "ALTER TABLE incoming_messages ADD COLUMN needs_review INTEGER NOT NULL DEFAULT 0"
                )
            if "review_reason" not in existing_columns:
                connection.execute("ALTER TABLE incoming_messages ADD COLUMN review_reason TEXT")
            if "review_status" not in existing_columns:
                connection.execute(
                    "ALTER TABLE incoming_messages ADD COLUMN review_status TEXT NOT NULL DEFAULT 'not_required'"
                )
            llm_columns = {
                "llm_extracted_json": "TEXT",
                "llm_model_id": "TEXT",
                "llm_latency_ms": "INTEGER",
                "llm_validation_pass": "INTEGER",
                "llm_status": "TEXT",
            }
            for column_name, column_type in llm_columns.items():
                if column_name not in existing_columns:
                    connection.execute(
                        f"ALTER TABLE incoming_messages ADD COLUMN {column_name} {column_type}"
                    )
            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_incoming_messages_external_event_id
                ON incoming_messages (external_event_id)
                WHERE external_event_id IS NOT NULL
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS shadow_review_annotations (
                    message_id INTEGER PRIMARY KEY,
                    annotated_at TEXT NOT NULL,
                    needs_review_ok INTEGER,
                    drug_name_ok INTEGER,
                    corrected_drug_name TEXT,
                    owner_notes TEXT,
                    FOREIGN KEY (message_id) REFERENCES incoming_messages(id)
                )
                """
            )


def save_incoming_message(
    message: IncomingMessage,
    needs_review: bool = False,
    review_reason: str | None = None,
    review_status: str = "not_required",
    llm_fields: LLMStorageFields | None = None,
) -> SaveMessageResult:
    settings = get_settings()
    received_at = datetime.now(UTC).isoformat()
    raw_payload = (
        message.raw_update
        if settings.bale_store_raw_updates
        else {"raw_update_storage": "disabled"}
    )
    raw_update = json.dumps(raw_payload, ensure_ascii=False)
    llm_storage = llm_fields or LLMStorageFields()
    validation_pass_value = None
    if llm_storage.validation_pass is not None:
        validation_pass_value = int(llm_storage.validation_pass)

    with closing(get_connection()) as connection:
        with connection:
            if message.external_event_id is not None:
                existing = connection.execute(
                    "SELECT id FROM incoming_messages WHERE external_event_id = ?",
                    (message.external_event_id,),
                ).fetchone()
                if existing is not None:
                    return SaveMessageResult(stored_message_id=int(existing[0]), inserted=False)

            try:
                cursor = connection.execute(
                    """
                    INSERT INTO incoming_messages (
                        received_at,
                        chat_id,
                        message_id,
                        external_event_id,
                        text,
                        raw_update,
                        needs_review,
                        review_reason,
                        review_status,
                        llm_extracted_json,
                        llm_model_id,
                        llm_latency_ms,
                        llm_validation_pass,
                        llm_status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        received_at,
                        message.chat_id,
                        message.message_id,
                        message.external_event_id,
                        message.text,
                        raw_update,
                        int(needs_review),
                        review_reason,
                        review_status,
                        llm_storage.extracted_json,
                        llm_storage.model_id,
                        llm_storage.latency_ms,
                        validation_pass_value,
                        llm_storage.status,
                    ),
                )
            except sqlite3.IntegrityError:
                if message.external_event_id is None:
                    raise
                existing = connection.execute(
                    "SELECT id FROM incoming_messages WHERE external_event_id = ?",
                    (message.external_event_id,),
                ).fetchone()
                if existing is None:
                    raise
                return SaveMessageResult(stored_message_id=int(existing[0]), inserted=False)
            return SaveMessageResult(stored_message_id=int(cursor.lastrowid), inserted=True)


def _build_review_item_dict(row: sqlite3.Row) -> dict[str, str | int | None | bool | dict]:
    item = dict(row)
    extracted_json = item.pop("llm_extracted_json", None)
    item["llm_model_id"] = item.pop("llm_model_id", None)
    item["llm_latency_ms"] = item.pop("llm_latency_ms", None)
    validation_pass = item.pop("llm_validation_pass", None)
    item["llm_validation_pass"] = None if validation_pass is None else bool(validation_pass)
    item["llm_status"] = item.pop("llm_status", None)
    if extracted_json:
        item["llm_extracted"] = json.loads(extracted_json)
    else:
        item["llm_extracted"] = None
    return item


def list_pending_review_items() -> list[dict[str, str | int | None | bool | dict]]:
    with closing(get_connection()) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                id,
                received_at,
                chat_id,
                message_id,
                text,
                review_reason,
                review_status,
                llm_extracted_json,
                llm_model_id,
                llm_latency_ms,
                llm_validation_pass,
                llm_status
            FROM incoming_messages
            WHERE needs_review = 1
              AND review_status = 'pending'
            ORDER BY id ASC
            """
        ).fetchall()

    return [_build_review_item_dict(row) for row in rows]


def _build_shadow_review_item_dict(row: sqlite3.Row) -> dict[str, str | int | None | bool | dict]:
    item = _build_review_item_dict(row)
    needs_review_ok = row["needs_review_ok"]
    drug_name_ok = row["drug_name_ok"]
    item["annotation"] = None
    if row["annotated_at"] is not None:
        item["annotation"] = {
            "annotated_at": row["annotated_at"],
            "needs_review_ok": None if needs_review_ok is None else bool(needs_review_ok),
            "drug_name_ok": None if drug_name_ok is None else bool(drug_name_ok),
            "corrected_drug_name": row["corrected_drug_name"],
            "owner_notes": row["owner_notes"],
        }
    return item


def list_shadow_review_items(limit: int = 50) -> list[dict[str, str | int | None | bool | dict]]:
    with closing(get_connection()) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                incoming_messages.id,
                incoming_messages.received_at,
                incoming_messages.message_id,
                incoming_messages.text,
                incoming_messages.llm_extracted_json,
                incoming_messages.llm_model_id,
                incoming_messages.llm_latency_ms,
                incoming_messages.llm_validation_pass,
                incoming_messages.llm_status,
                shadow_review_annotations.annotated_at,
                shadow_review_annotations.needs_review_ok,
                shadow_review_annotations.drug_name_ok,
                shadow_review_annotations.corrected_drug_name,
                shadow_review_annotations.owner_notes
            FROM incoming_messages
            LEFT JOIN shadow_review_annotations
                ON shadow_review_annotations.message_id = incoming_messages.id
            WHERE incoming_messages.llm_status = 'shadow_ok'
            ORDER BY incoming_messages.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [_build_shadow_review_item_dict(row) for row in rows]


def upsert_shadow_review_annotation(
    message_id: int,
    *,
    needs_review_ok: bool | None,
    drug_name_ok: bool | None,
    corrected_drug_name: str | None,
    owner_notes: str | None,
) -> dict[str, str | int | bool | None] | None:
    with closing(get_connection()) as connection:
        with connection:
            message_row = connection.execute(
                """
                SELECT id
                FROM incoming_messages
                WHERE id = ?
                  AND llm_status = 'shadow_ok'
                """,
                (message_id,),
            ).fetchone()
            if message_row is None:
                return None

            annotated_at = datetime.now(UTC).isoformat()
            needs_review_ok_value = None if needs_review_ok is None else int(needs_review_ok)
            drug_name_ok_value = None if drug_name_ok is None else int(drug_name_ok)

            connection.execute(
                """
                INSERT INTO shadow_review_annotations (
                    message_id,
                    annotated_at,
                    needs_review_ok,
                    drug_name_ok,
                    corrected_drug_name,
                    owner_notes
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(message_id) DO UPDATE SET
                    annotated_at = excluded.annotated_at,
                    needs_review_ok = excluded.needs_review_ok,
                    drug_name_ok = excluded.drug_name_ok,
                    corrected_drug_name = excluded.corrected_drug_name,
                    owner_notes = excluded.owner_notes
                """,
                (
                    message_id,
                    annotated_at,
                    needs_review_ok_value,
                    drug_name_ok_value,
                    corrected_drug_name,
                    owner_notes,
                ),
            )

            return {
                "ok": True,
                "message_id": message_id,
                "annotated_at": annotated_at,
                "needs_review_ok": needs_review_ok,
                "drug_name_ok": drug_name_ok,
                "corrected_drug_name": corrected_drug_name,
                "owner_notes": owner_notes,
            }


def mark_review_item_reviewed(message_id: int) -> dict[str, str | int | bool] | None:
    with closing(get_connection()) as connection:
        with connection:
            row = connection.execute(
                """
                SELECT id, review_status
                FROM incoming_messages
                WHERE id = ?
                """,
                (message_id,),
            ).fetchone()

            if row is None:
                return None

            current_status = str(row[1])
            if current_status != "pending":
                return {
                    "ok": True,
                    "message_id": int(row[0]),
                    "review_status": current_status,
                    "changed": False,
                }

            connection.execute(
                """
                UPDATE incoming_messages
                SET review_status = 'reviewed'
                WHERE id = ?
                  AND review_status = 'pending'
                """,
                (message_id,),
            )

            return {
                "ok": True,
                "message_id": int(row[0]),
                "review_status": "reviewed",
                "changed": True,
            }


def create_sqlite_backup(backup_dir: str | Path = "backups") -> BackupResult:
    settings = get_settings()
    source_path = Path(settings.database_path)
    if not source_path.is_file():
        raise FileNotFoundError(f"SQLite database file was not found: {source_path}")

    destination_dir = Path(backup_dir)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    backup_name = f"{source_path.stem}-{timestamp}{source_path.suffix or '.db'}"
    backup_path = destination_dir / backup_name

    destination_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, backup_path)

    return BackupResult(source_path=source_path, backup_path=backup_path, created=True)


def restore_sqlite_backup(backup_path: str | Path, overwrite: bool = False) -> RestoreResult:
    source_path = Path(backup_path)
    if not source_path.is_file():
        raise FileNotFoundError(f"SQLite backup file was not found: {source_path}")

    settings = get_settings()
    destination_path = Path(settings.database_path)
    if destination_path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing SQLite database: {destination_path}")

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination_path)

    return RestoreResult(backup_path=source_path, restored_path=destination_path, restored=True)
