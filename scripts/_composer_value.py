import json
import sqlite3
from pathlib import Path

OLD = "e03e37de1472758d799e23baa163f34e"
GLOBAL = Path(r"C:\Users\hosse\AppData\Roaming\Cursor\User\globalStorage\state.vscdb")

conn = sqlite3.connect(f"file:{GLOBAL}?mode=ro", uri=True)
cur = conn.cursor()
cur.execute(
    "SELECT composerId, value FROM composerHeaders WHERE workspaceId = ? LIMIT 1",
    (OLD,),
)
composer_id, value = cur.fetchone()
parsed = json.loads(value)
print("composerId:", composer_id)
print("value top keys:", list(parsed.keys()))
print("sample fields:", {k: parsed.get(k) for k in list(parsed.keys())[:15]})

# find blob refs
text = json.dumps(parsed)
if "agentKv" in text or "blob" in text:
    print("contains agentKv/blob refs")

cur.execute("SELECT COUNT(*) FROM composerHeaders WHERE workspaceId = ?", (OLD,))
print("old count:", cur.fetchone()[0])

cur.execute(
    "SELECT composerId FROM composerHeaders WHERE workspaceId = ?",
    ("763d8b679bbecca980b3c7f764435df5",),
)
main_ids = {row[0] for row in cur.fetchall()}
cur.execute("SELECT composerId FROM composerHeaders WHERE workspaceId = ?", (OLD,))
old_ids = {row[0] for row in cur.fetchall()}
print("overlap ids:", old_ids & main_ids)

# path refs in values
cur.execute("SELECT composerId, value FROM composerHeaders WHERE workspaceId = ?", (OLD,))
path_hits = 0
for cid, val in cur.fetchall():
    if val and "Documents/BaleMed" in val and "OneDrive" not in val:
        path_hits += 1
print("values with old Documents/BaleMed path:", path_hits)

conn.close()
