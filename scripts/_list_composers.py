import json
import sqlite3
from pathlib import Path

OLD = "e03e37de1472758d799e23baa163f34e"
MAIN = "763d8b679bbecca980b3c7f764435df5"
GLOBAL = Path(r"C:\Users\hosse\AppData\Roaming\Cursor\User\globalStorage\state.vscdb")

conn = sqlite3.connect(f"file:{GLOBAL}?mode=ro", uri=True)
cur = conn.cursor()

for ws_id, label in ((OLD, "OLD"), (MAIN, "MAIN")):
    cur.execute(
        "SELECT composerId, createdAt, lastUpdatedAt, isArchived, value "
        "FROM composerHeaders WHERE workspaceId = ? ORDER BY lastUpdatedAt DESC",
        (ws_id,),
    )
    rows = cur.fetchall()
    print(f"\n=== {label}: {len(rows)} composers ===")
    for composer_id, created, updated, archived, value in rows[:8]:
        title = "?"
        if value:
            try:
                parsed = json.loads(value)
                title = parsed.get("name") or parsed.get("title") or parsed.get("text", "")[:60]
            except json.JSONDecodeError:
                title = value[:60]
        print(f"  {composer_id[:8]}... archived={archived} title={title!r}")

cur.execute(
    'SELECT key FROM "ItemTable" WHERE key LIKE ?',
    (f"%{OLD}%",),
)
print("\nOLD ItemTable keys with ws id:")
for (key,) in cur.fetchall():
    print(" ", key)

cur.execute('SELECT key, value FROM "ItemTable" WHERE key = "composer.composerData"')
print("\nNo global composer.composerData rows")

conn.close()

for label, ws_id, path in (
    (
        "OLD",
        OLD,
        Path(
            rf"C:\Users\hosse\AppData\Roaming\Cursor\User\workspaceStorage\{OLD}\state.vscdb"
        ),
    ),
    (
        "MAIN",
        MAIN,
        Path(
            rf"C:\Users\hosse\AppData\Roaming\Cursor\User\workspaceStorage\{MAIN}\state.vscdb"
        ),
    ),
):
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute('SELECT value FROM "ItemTable" WHERE key = "composer.composerData"')
    row = cur.fetchone()
    conn.close()
    print(f"\n{label} workspace composer.composerData:")
    if row:
        data = json.loads(row[0])
        print(json.dumps(data, indent=2)[:2000])
