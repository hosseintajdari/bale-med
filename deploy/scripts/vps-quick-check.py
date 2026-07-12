#!/usr/bin/env python3
from __future__ import annotations

import os
import sqlite3
import sys

os.chdir("/opt/bale-bot")
sys.path.insert(0, "/opt/bale-bot")

from app.config import get_settings

settings = get_settings()
print(f"BALE_ENABLE_SENDING={settings.bale_enable_sending}")
print(f"BALE_ENABLE_LLM={settings.bale_enable_llm}")
print(f"token_len={len(settings.bale_bot_token)}")

conn = sqlite3.connect("/opt/bale-bot/data/bale_bot.db")
rows = conn.execute(
    """
    SELECT id, message_id, external_event_id, llm_status
    FROM incoming_messages
    ORDER BY id DESC
    LIMIT 8
    """
).fetchall()
print("recent_messages=", rows)
conn.close()
