#!/usr/bin/env python3
"""Test Ollama Cloud connectivity from VPS (no secrets printed)."""
from __future__ import annotations

import json
import os
import sys

os.chdir("/opt/bale-bot")
sys.path.insert(0, "/opt/bale-bot")

import httpx

from app.config import get_settings

settings = get_settings()
print(f"base_url={settings.bale_llm_api_base_url}")
print(f"model={settings.bale_llm_model}")
print(f"key_len={len(settings.bale_llm_api_key)}")
print(f"llm_enabled={settings.bale_enable_llm}")

url = f"{settings.bale_llm_api_base_url.rstrip('/')}/chat/completions"
headers = {
    "Authorization": f"Bearer {settings.bale_llm_api_key}",
    "Content-Type": "application/json",
}

# Test 1: list models
models_url = f"{settings.bale_llm_api_base_url.rstrip('/')}/models"
try:
    with httpx.Client(timeout=30.0) as client:
        r = client.get(models_url, headers=headers)
        print(f"models_status={r.status_code}")
        if r.status_code == 200:
            data = r.json()
            ids = [m.get("id") for m in data.get("data", [])[:8]]
            print(f"sample_models={ids}")
        else:
            print(f"models_error={r.text[:200]}")
except Exception as exc:
    print(f"models_exception={exc}")

# Test 2: chat without json_object (Ollama may reject response_format)
body_plain = {
    "model": settings.bale_llm_model,
    "temperature": 0,
    "messages": [{"role": "user", "content": "Return JSON: {\"ok\": true}"}],
}
try:
    with httpx.Client(timeout=60.0) as client:
        r = client.post(url, headers=headers, json=body_plain)
        print(f"chat_plain_status={r.status_code}")
        if r.status_code != 200:
            print(f"chat_plain_error={r.text[:300]}")
        else:
            content = r.json()["choices"][0]["message"]["content"]
            print(f"chat_plain_ok len={len(content)}")
except Exception as exc:
    print(f"chat_plain_exception={exc}")

# Test 3: chat with json_object (what BaleMed sends)
body_json = {
    **body_plain,
    "response_format": {"type": "json_object"},
}
try:
    with httpx.Client(timeout=60.0) as client:
        r = client.post(url, headers=headers, json=body_json)
        print(f"chat_json_status={r.status_code}")
        if r.status_code != 200:
            print(f"chat_json_error={r.text[:300]}")
        else:
            content = r.json()["choices"][0]["message"]["content"]
            print(f"chat_json_ok preview={content[:120]}")
except Exception as exc:
    print(f"chat_json_exception={exc}")
