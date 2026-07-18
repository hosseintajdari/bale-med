import sqlite3
from pathlib import Path

db = Path(r"C:\Users\hosse\AppData\Roaming\Cursor\User\globalStorage\conversation-search.db")
if not db.exists():
    print("conversation-search.db not found")
    raise SystemExit(0)

conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("tables:", [r[0] for r in cur.fetchall()])
for table in ("conversations", "chunks", "documents", "meta"):
    try:
        cur.execute(f"PRAGMA table_info({table})")
        cols = cur.fetchall()
        if cols:
            print(f"\n{table} columns:", [c[1] for c in cols])
    except sqlite3.Error:
        pass

for needle in ("Documents/BaleMed", "e03e37de1472758d799e23baa163f34e"):
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    for (table,) in cur.fetchall():
        cur.execute(f"PRAGMA table_info({table})")
        text_cols = [c[1] for c in cur.fetchall() if c[2].upper().startswith("TEXT")]
        for col in text_cols:
            try:
                cur.execute(
                    f'SELECT COUNT(*) FROM "{table}" WHERE "{col}" LIKE ?',
                    (f"%{needle}%",),
                )
                count = cur.fetchone()[0]
                if count:
                    print(f"hits {table}.{col} for {needle}: {count}")
            except sqlite3.Error:
                pass

conn.close()
