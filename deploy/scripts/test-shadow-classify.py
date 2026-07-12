#!/usr/bin/env python3
"""Run one shadow LLM classification using app settings (no secrets printed)."""
from __future__ import annotations

import os
import sys

os.chdir("/opt/bale-bot")
sys.path.insert(0, "/opt/bale-bot")

from app.config import get_settings
from app.llm.service import classify_message_text

settings = get_settings()
result = classify_message_text(
    "shadow verify - need acetaminophen for headache",
    settings,
    "shadow-verify-chat",
)
print(f"status={result.audit.status}")
print(f"validation_pass={result.audit.validation_pass}")
print(f"latency_ms={result.audit.latency_ms}")
print(f"has_extracted={result.extracted is not None}")
if result.extracted is not None:
    print(f"needs_review={result.extracted.needs_review}")
