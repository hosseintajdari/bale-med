#!/usr/bin/env python3
"""Test LLM provider from VPS (no secrets printed)."""
from __future__ import annotations

import os
import sys

os.chdir("/opt/bale-bot")
sys.path.insert(0, "/opt/bale-bot")

import httpx

from app.config import get_settings

settings = get_settings()
base = settings.bale_llm_api_base_url.rstrip("/")
url = f"{base}/chat/completions"
headers = {
    "Authorization": f"Bearer {settings.bale_llm_api_key}",
    "Content-Type": "application/json",
}

print(f"base_len={len(base)}")
print(f"model={settings.bale_llm_model}")
print(f"key_len={len(settings.bale_llm_api_key)}")

body = {
    "model": settings.bale_llm_model,
    "temperature": 0,
    "messages": [{"role": "user", "content": 'Return only JSON: {"ok": true}'}],
}

try:
    with httpx.Client(timeout=60.0) as client:
        r = client.post(url, headers=headers, json=body)
        print(f"status={r.status_code}")
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            print(f"ok content_len={len(content)}")
        else:
            print(f"error={r.text[:250]}")
except Exception as exc:
    print(f"exception={exc}")

# Test with json_object like BaleMed
body_json = {**body, "response_format": {"type": "json_object"}}
try:
    with httpx.Client(timeout=60.0) as client:
        r = client.post(url, headers=headers, json=body_json)
        print(f"json_status={r.status_code}")
        if r.status_code != 200:
            print(f"json_error={r.text[:250]}")
        else:
            content = r.json()["choices"][0]["message"]["content"]
            print(f"json_ok preview={content[:120]}")
except Exception as exc:
    print(f"json_exception={exc}")
