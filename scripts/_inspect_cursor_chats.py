"""Temporary script to inspect Cursor workspace chat storage."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

OLD_WS = Path(
    r"C:\Users\hosse\AppData\Roaming\Cursor\User\workspaceStorage"
    r"\e03e37de1472758d799e23baa163f34e\state.vscdb"
)
MAIN_WS = Path(
    r"C:\Users\hosse\AppData\Roaming\Cursor\User\workspaceStorage"
    r"\763d8b679bbecca980b3c7f764435df5\state.vscdb"
)
GLOBAL = Path(
    r"C:\Users\hosse\AppData\Roaming\Cursor\User\globalStorage\state.vscdb"
)
OLD_PROJECT = Path(
    r"C:\Users\hosse\.cursor\projects\c-Users-hosse-Documents-BaleMed"
)
MAIN_PROJECT = Path(
    r"C:\Users\hosse\.cursor\projects\c-Users-hosse-OneDrive-Documents-BaleMed"
)


def inspect_db(path: Path, label: str) -> None:
    print(f"\n=== {label}: {path} ===")
    if not path.exists():
        print("NOT FOUND")
        return
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    print("tables:", tables)
    for table in tables:
        cur.execute(f'SELECT COUNT(*) FROM "{table}"')
        count = cur.fetchone()[0]
        print(f"  {table}: {count} rows")
        if table == "ItemTable":
            cur.execute(
                'SELECT key FROM "ItemTable" WHERE key LIKE "%composer%" '
                'OR key LIKE "%chat%" OR key LIKE "%agent%" OR key LIKE "%conversation%" '
                'LIMIT 30'
            )
            keys = [row[0] for row in cur.fetchall()]
            if keys:
                print("  sample keys:", keys[:15])
    conn.close()


def list_project_transcripts(path: Path, label: str) -> None:
    print(f"\n=== {label} project transcripts: {path} ===")
    transcripts = path / "agent-transcripts"
    if not transcripts.exists():
        print("no agent-transcripts folder")
        return
    files = list(transcripts.rglob("*.jsonl"))
    print(f"count: {len(files)}")
    for file in sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
        print(f"  {file.name} ({file.stat().st_size} bytes)")


def main() -> None:
    inspect_db(OLD_WS, "OLD workspace")
    inspect_db(MAIN_WS, "MAIN workspace")
    inspect_db(GLOBAL, "GLOBAL storage")
    list_project_transcripts(OLD_PROJECT, "OLD")
    list_project_transcripts(MAIN_PROJECT, "MAIN")


if __name__ == "__main__":
    main()
