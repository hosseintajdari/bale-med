"""Inspect composer chat data tied to each BaleMed workspace."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

OLD_WS_ID = "e03e37de1472758d799e23baa163f34e"
MAIN_WS_ID = "763d8b679bbecca980b3c7f764435df5"

PATHS = {
    "old_ws": Path(
        rf"C:\Users\hosse\AppData\Roaming\Cursor\User\workspaceStorage\{OLD_WS_ID}\state.vscdb"
    ),
    "main_ws": Path(
        rf"C:\Users\hosse\AppData\Roaming\Cursor\User\workspaceStorage\{MAIN_WS_ID}\state.vscdb"
    ),
    "global": Path(
        r"C:\Users\hosse\AppData\Roaming\Cursor\User\globalStorage\state.vscdb"
    ),
}


def read_item(path: Path, key: str) -> object | None:
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute('SELECT value FROM "ItemTable" WHERE key = ?', (key,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    try:
        return json.loads(row[0])
    except json.JSONDecodeError:
        return row[0]


def summarize_composer_data(data: object, label: str) -> None:
    print(f"\n--- {label} composer.composerData ---")
    if data is None:
        print("missing")
        return
    if isinstance(data, dict):
        print("top keys:", list(data.keys())[:20])
        for key in ("allComposers", "composers", "composerData", "tabs"):
            if key in data:
                value = data[key]
                if isinstance(value, list):
                    print(f"  {key}: {len(value)} items")
                    for item in value[:3]:
                        if isinstance(item, dict):
                            print(
                                "    sample:",
                                {
                                    k: item.get(k)
                                    for k in (
                                        "composerId",
                                        "id",
                                        "name",
                                        "title",
                                        "createdAt",
                                        "lastUpdatedAt",
                                    )
                                    if k in item
                                },
                            )
                elif isinstance(value, dict):
                    print(f"  {key}: dict keys {list(value.keys())[:10]}")


def count_global_refs(ws_id: str, label: str) -> None:
    path = PATHS["global"]
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute(
        'SELECT COUNT(*) FROM "ItemTable" WHERE key LIKE ?',
        (f"%{ws_id}%",),
    )
    item_count = cur.fetchone()[0]
    cur.execute(
        'SELECT COUNT(*) FROM cursorDiskKV WHERE key LIKE ?',
        (f"%{ws_id}%",),
    )
    kv_count = cur.fetchone()[0]
    cur.execute(
        'SELECT COUNT(*) FROM composerHeaders WHERE workspaceId = ?',
        (ws_id,),
    )
    header_count = cur.fetchone()[0]
    conn.close()
    print(
        f"{label}: ItemTable={item_count}, cursorDiskKV={kv_count}, "
        f"composerHeaders={header_count}"
    )


def sample_composer_headers(ws_id: str, label: str, limit: int = 5) -> None:
    path = PATHS["global"]
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute(
        "SELECT composerId, name, createdAt, lastUpdatedAt FROM composerHeaders "
        "WHERE workspaceId = ? ORDER BY lastUpdatedAt DESC LIMIT ?",
        (ws_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    print(f"\n--- {label} composerHeaders ({len(rows)} shown) ---")
    for row in rows:
        print(" ", row)


def main() -> None:
    for label, ws_id in (("OLD", OLD_WS_ID), ("MAIN", MAIN_WS_ID)):
        count_global_refs(ws_id, label)
        summarize_composer_data(
            read_item(PATHS[f"{label.lower()}_ws"], "composer.composerData"),
            label,
        )
        sample_composer_headers(ws_id, label)


if __name__ == "__main__":
    main()
