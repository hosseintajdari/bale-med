import sqlite3
from pathlib import Path

OLD = "e03e37de1472758d799e23baa163f34e"
MAIN = "763d8b679bbecca980b3c7f764435df5"
GLOBAL = Path(r"C:\Users\hosse\AppData\Roaming\Cursor\User\globalStorage\state.vscdb")

conn = sqlite3.connect(f"file:{GLOBAL}?mode=ro", uri=True)
cur = conn.cursor()
cur.execute('SELECT key FROM "ItemTable" WHERE key LIKE ?', (f"%{OLD}%",))
old_keys = {row[0] for row in cur.fetchall()}
cur.execute('SELECT key FROM "ItemTable" WHERE key LIKE ?', (f"%{MAIN}%",))
main_keys = {row[0] for row in cur.fetchall()}

def remap(key: str) -> str:
    return key.replace(OLD, MAIN).replace(
        "Documents/BaleMed", "OneDrive/Documents/BaleMed"
    ).replace(
        "documents/balemed", "OneDrive/Documents/BaleMed"
    )

conflicts = []
for key in old_keys:
    new_key = remap(key)
    if new_key in main_keys:
        conflicts.append((key, new_key))

print("old keys:", len(old_keys))
print("main keys:", len(main_keys))
print("conflicts:", len(conflicts))
for old, new in conflicts[:10]:
    print(" ", old, "->", new)

conn.close()
