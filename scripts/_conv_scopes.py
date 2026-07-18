import sqlite3
from pathlib import Path

db = Path(r"C:\Users\hosse\AppData\Roaming\Cursor\User\globalStorage\conversation-search.db")
conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
cur = conn.cursor()
cur.execute("SELECT scope, COUNT(*) FROM conversations GROUP BY scope ORDER BY COUNT(*) DESC LIMIT 20")
print("scopes:")
for scope, count in cur.fetchall():
    print(f"  {scope}: {count}")

cur.execute(
    "SELECT id, title, scope FROM conversations WHERE scope LIKE '%e03e37%' OR scope LIKE '%Documents/BaleMed%' LIMIT 10"
)
rows = cur.fetchall()
print("\nold workspace rows:", len(rows))
for row in rows:
    print(" ", row)
conn.close()
