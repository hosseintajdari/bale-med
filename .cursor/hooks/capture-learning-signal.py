#!/usr/bin/env python3
"""Capture lightweight learning signals from Cursor agent sessions (local queue)."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

QUEUE_DIR = Path(".cursor/learning-queue")
BLIND_SPOT_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bhow does\b|\bhow do i\b|\bwhere is\b|\bwhy does\b", "architecture_gap"),
    (r"\berror\b|\bfail(ed|ure)?\b|\bbug\b|\bfix\b", "debugging"),
    (r"\bnotion\b|\bmcp\b|\bautomation\b", "tooling_integration"),
    (r"\bgit\b|\bcommit\b|\bpush\b|\bpr\b", "git_workflow"),
    (r"\bdeploy\b|\bvps\b|\bssh\b|\bsystemd\b", "devops"),
    (r"\bfastapi\b|\bpydantic\b|\bsqlite\b|\basync\b", "python_backend"),
    (r"\btypescript\b|\breact\b|\bnext\.?js\b", "frontend"),
    (r"\benglish\b|\btranslate\b|\bvocabulary\b", "english_learning"),
)


def _read_hook_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw[:2000]}
    if not isinstance(payload, dict):
        return {"raw": str(payload)[:2000]}
    return payload


def _extract_text(payload: dict[str, Any]) -> str:
    chunks: list[str] = []
    for key in ("user_message", "prompt", "last_user_message", "conversation_summary"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            chunks.append(value.strip())
    messages = payload.get("messages")
    if isinstance(messages, list):
        for item in messages[-6:]:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if isinstance(content, str) and content.strip():
                chunks.append(content.strip())
    return "\n".join(chunks)


def _detect_blind_spots(text: str) -> list[str]:
    if not text.strip():
        return []
    lowered = text.lower()
    hits: list[str] = []
    for pattern, label in BLIND_SPOT_PATTERNS:
        if re.search(pattern, lowered):
            hits.append(label)
    return sorted(set(hits))


def _append_signal(payload: dict[str, Any]) -> None:
    now = datetime.now(timezone.utc)
    day_key = now.strftime("%Y-%m-%d")
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    queue_file = QUEUE_DIR / f"{day_key}.jsonl"

    text = _extract_text(payload)
    record = {
        "captured_at": now.isoformat(),
        "event": payload.get("event") or payload.get("hook_event") or "stop",
        "workspace_roots": payload.get("workspace_roots") or payload.get("workspaceRoots"),
        "conversation_id": payload.get("conversation_id") or payload.get("conversationId"),
        "text_preview": text[:1200] if text else "",
        "blind_spots": _detect_blind_spots(text),
        "status": payload.get("status"),
    }
    with queue_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    payload = _read_hook_input()
    _append_signal(payload)
    sys.exit(0)


if __name__ == "__main__":
    main()
