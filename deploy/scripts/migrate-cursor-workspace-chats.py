#!/usr/bin/env python3
"""Migrate Cursor agent chats from old Documents/BaleMed workspace to OneDrive path."""
from __future__ import annotations

import json
import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

OLD_WS_ID = "e03e37de1472758d799e23baa163f34e"
MAIN_WS_ID = "763d8b679bbecca980b3c7f764435df5"

OLD_FOLDER = Path(r"C:\Users\hosse\Documents\BaleMed")
MAIN_FOLDER = Path(r"C:\Users\hosse\OneDrive\Documents\BaleMed")

GLOBAL_DB = Path(
    r"C:\Users\hosse\AppData\Roaming\Cursor\User\globalStorage\state.vscdb"
)
OLD_WS_DIR = Path(
    rf"C:\Users\hosse\AppData\Roaming\Cursor\User\workspaceStorage\{OLD_WS_ID}"
)
MAIN_WS_DIR = Path(
    rf"C:\Users\hosse\AppData\Roaming\Cursor\User\workspaceStorage\{MAIN_WS_ID}"
)
OLD_PROJECT_DIR = Path(
    r"C:\Users\hosse\.cursor\projects\c-Users-hosse-Documents-BaleMed"
)

PATH_REPLACEMENTS = (
    (r"C:\Users\hosse\Documents\BaleMed", r"C:\Users\hosse\OneDrive\Documents\BaleMed"),
    ("c:\\Users\\hosse\\Documents\\BaleMed", "c:\\Users\\hosse\\OneDrive\\Documents\\BaleMed"),
    ("c:/Users/hosse/Documents/BaleMed", "c:/Users/hosse/OneDrive/Documents/BaleMed"),
    ("/c:/Users/hosse/Documents/BaleMed", "/c:/Users/hosse/OneDrive/Documents/BaleMed"),
    ("file:///c%3A/Users/hosse/Documents/BaleMed", "file:///c%3A/Users/hosse/OneDrive/Documents/BaleMed"),
)


def replace_paths(text: str) -> str:
    updated = text
    for old, new in PATH_REPLACEMENTS:
        updated = updated.replace(old, new)
    return updated.replace(OLD_WS_ID, MAIN_WS_ID)


def backup_file(path: Path, backup_root: Path) -> Path:
    target = backup_root / path.name
    shutil.copy2(path, target)
    for suffix in ("-shm", "-wal"):
        sidecar = Path(str(path) + suffix)
        if sidecar.exists() and sidecar.stat().st_size > 0:
            shutil.copy2(sidecar, backup_root / sidecar.name)
    return target


def checkpoint_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.commit()
    conn.close()


def migrate_composer_headers(conn: sqlite3.Connection) -> int:
    cur = conn.cursor()
    cur.execute(
        "SELECT composerId, value FROM composerHeaders WHERE workspaceId = ?",
        (OLD_WS_ID,),
    )
    rows = cur.fetchall()
    migrated = 0
    for composer_id, value in rows:
        if not value:
            updated_value = value
        else:
            parsed = json.loads(value)
            workspace_identifier = parsed.get("workspaceIdentifier")
            if isinstance(workspace_identifier, dict):
                workspace_identifier["id"] = MAIN_WS_ID
                uri = workspace_identifier.get("uri")
                if isinstance(uri, dict):
                    for key in ("fsPath", "external", "path"):
                        if isinstance(uri.get(key), str):
                            uri[key] = replace_paths(uri[key])
            updated_value = replace_paths(json.dumps(parsed, ensure_ascii=False))
        cur.execute(
            "UPDATE composerHeaders SET workspaceId = ?, value = ? WHERE composerId = ?",
            (MAIN_WS_ID, updated_value, composer_id),
        )
        migrated += 1
    return migrated


def migrate_item_table(conn: sqlite3.Connection, table: str = "ItemTable") -> tuple[int, int]:
    cur = conn.cursor()
    cur.execute(f'SELECT key, value FROM "{table}"')
    rows = cur.fetchall()
    updated_rows = 0
    deleted_rows = 0
    existing_keys = {key for key, _ in rows}

    for key, value in rows:
        if OLD_WS_ID not in key and (not value or "Documents/BaleMed" not in value):
            continue
        new_key = replace_paths(key)
        new_value = replace_paths(value) if isinstance(value, str) else value

        if new_key != key and new_key in existing_keys and new_key != key:
            cur.execute(f'DELETE FROM "{table}" WHERE key = ?', (key,))
            deleted_rows += 1
            continue

        if new_key == key and new_value == value:
            continue

        cur.execute(f'DELETE FROM "{table}" WHERE key = ?', (key,))
        cur.execute(
            f'INSERT OR REPLACE INTO "{table}" (key, value) VALUES (?, ?)',
            (new_key, new_value),
        )
        updated_rows += 1
        existing_keys.add(new_key)

    return updated_rows, deleted_rows


def migrate_cursor_disk_kv(conn: sqlite3.Connection) -> int:
    cur = conn.cursor()
    cur.execute("SELECT key, value FROM cursorDiskKV")
    rows = cur.fetchall()
    updated = 0
    for key, value in rows:
        if OLD_WS_ID not in key:
            continue
        new_key = replace_paths(key)
        cur.execute("DELETE FROM cursorDiskKV WHERE key = ?", (key,))
        cur.execute(
            "INSERT OR REPLACE INTO cursorDiskKV (key, value) VALUES (?, ?)",
            (new_key, value),
        )
        updated += 1
    return updated


def remove_old_artifacts() -> list[str]:
    removed: list[str] = []
    if OLD_FOLDER.exists():
        shutil.rmtree(OLD_FOLDER)
        removed.append(str(OLD_FOLDER))
    if OLD_WS_DIR.exists():
        shutil.rmtree(OLD_WS_DIR)
        removed.append(str(OLD_WS_DIR))
    if OLD_PROJECT_DIR.exists():
        shutil.rmtree(OLD_PROJECT_DIR)
        removed.append(str(OLD_PROJECT_DIR))
    return removed


def main() -> None:
    if not MAIN_FOLDER.exists():
        raise SystemExit(f"Main folder missing: {MAIN_FOLDER}")
    if not GLOBAL_DB.exists():
        raise SystemExit(f"Global Cursor DB missing: {GLOBAL_DB}")

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    backup_root = MAIN_FOLDER / ".cursor-backups" / f"workspace-chat-migration-{timestamp}"
    backup_root.mkdir(parents=True, exist_ok=True)

    checkpoint_db(GLOBAL_DB)
    backup_file(GLOBAL_DB, backup_root)
    if OLD_WS_DIR.joinpath("state.vscdb").exists():
        checkpoint_db(OLD_WS_DIR / "state.vscdb")
        backup_file(OLD_WS_DIR / "state.vscdb", backup_root)
    if MAIN_WS_DIR.joinpath("state.vscdb").exists():
        backup_file(MAIN_WS_DIR / "state.vscdb", backup_root)

    conn = sqlite3.connect(GLOBAL_DB)
    try:
        composer_count = migrate_composer_headers(conn)
        item_updates, item_deletes = migrate_item_table(conn)
        kv_updates = migrate_cursor_disk_kv(conn)
        conn.commit()
    finally:
        conn.close()

    removed = remove_old_artifacts()

    summary = {
        "backup_dir": str(backup_root),
        "composer_headers_migrated": composer_count,
        "item_table_updates": item_updates,
        "item_table_deletes": item_deletes,
        "cursor_disk_kv_updates": kv_updates,
        "removed_paths": removed,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
