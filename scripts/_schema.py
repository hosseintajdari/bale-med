import sqlite3
from pathlib import Path

path = Path(r"C:\Users\hosse\AppData\Roaming\Cursor\User\globalStorage\state.vscdb")
conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
cur = conn.cursor()
cur.execute("PRAGMA table_info(composerHeaders)")
print("composerHeaders columns:", cur.fetchall())
cur.execute("SELECT * FROM composerHeaders LIMIT 1")
row = cur.fetchone()
print("sample row keys count:", len(row) if row else 0)
cur.execute("PRAGMA table_info(cursorDiskKV)")
print("cursorDiskKV columns:", cur.fetchall())
cur.execute("SELECT key FROM cursorDiskKV WHERE key LIKE '%e03e37de1472758d799e23baa163f34e%' LIMIT 10")
print("old ws kv keys:", [r[0] for r in cur.fetchall()])
cur.execute("SELECT key FROM cursorDiskKV LIMIT 5")
print("sample kv keys:", [r[0] for r in cur.fetchall()])
conn.close()
