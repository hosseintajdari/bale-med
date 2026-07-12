#!/usr/bin/env python3
"""Post local test webhooks to exercise shadow LLM on real handler path."""
from __future__ import annotations

import os
import sys
import time

import httpx

os.chdir("/opt/bale-bot")
sys.path.insert(0, "/opt/bale-bot")

from app.config import get_settings

settings = get_settings()
url = f"http://127.0.0.1:8000/webhook/bale/{settings.bale_webhook_secret}"

for i in range(1, 6):
    message_id = 900_000 + i
    text = f"shadow verify test message {i} - need acetaminophen"
    response = httpx.post(
        url,
        json={
            "message": {
                "message_id": message_id,
                "chat": {"id": "shadow-test-chat"},
                "text": text,
            }
        },
        timeout=120.0,
    )
    payload = response.json()
    print(f"msg{i}: http={response.status_code} ok={payload.get('ok')}")
    time.sleep(3)
