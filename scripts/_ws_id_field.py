import json
import sqlite3
from pathlib import Path

OLD = "e03e37de1472758d799e23baa163f34e"
GLOBAL = Path(r"C:\Users\hosse\AppData\Roaming\Cursor\User\globalStorage\state.vscdb")

conn = sqlite3.connect(f"file:{GLOBAL}?mode=ro", uri=True)
cur = conn.cursor()
cur.execute(
    "SELECT value FROM composerHeaders WHERE workspaceId = ? LIMIT 1",
    (OLD,),
)
value = json.loads(cur.fetchone()[0])
print("workspaceIdentifier:", json.dumps(value.get("workspaceIdentifier"), indent=2))
print("trackedGitRepos:", value.get("trackedGitRepos"))

conn.close()
