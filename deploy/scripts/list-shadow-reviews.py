#!/usr/bin/env python3
"""List recent shadow_ok messages with LLM extracted fields (P2 owner review)."""
from __future__ import annotations

import json
import os
import sqlite3
import sys

os.chdir("/opt/bale-bot")
sys.path.insert(0, "/opt/bale-bot")

DB_PATH = "/opt/bale-bot/data/bale_bot.db"
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 50


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT id, received_at, message_id, text, llm_status, llm_extracted_json
        FROM incoming_messages
        WHERE llm_status = 'shadow_ok'
        ORDER BY id DESC
        LIMIT ?
        """,
        (LIMIT,),
    ).fetchall()
    conn.close()

    print(f"shadow_ok_count={len(rows)} limit={LIMIT}")
    for row in rows:
        row_id, received_at, message_id, text, llm_status, extracted_json = row
        preview = (text or "")[:80].replace("\n", " ")
        extracted = json.loads(extracted_json) if extracted_json else None
        print(
            json.dumps(
                {
                    "id": row_id,
                    "received_at": received_at,
                    "message_id": message_id,
                    "text_preview": preview,
                    "llm_status": llm_status,
                    "llm_extracted": extracted,
                },
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
