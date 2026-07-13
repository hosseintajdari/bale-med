#!/usr/bin/env python3
"""Add Milestone 9 LLM env keys to server .env if missing (no stdout secrets)."""
from __future__ import annotations

from pathlib import Path

ENV_PATH = Path("/opt/bale-bot/.env")

DEFAULTS = {
    "BALE_ENABLE_LLM": "true",
    "BALE_LLM_MODE": "shadow",
    "BALE_LLM_API_BASE_URL": "",
    "BALE_LLM_API_KEY": "",
    "BALE_LLM_MODEL": "DeepSeek-V3.2",
    "BALE_LLM_TIMEOUT_SECONDS": "90",
}


def main() -> None:
    text = ENV_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    existing: dict[str, str] = {}
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.split("=", 1)
            existing[key.strip()] = value.strip()

    added: list[str] = []
    for key, default in DEFAULTS.items():
        if key not in existing:
            lines.append(f"{key}={default}")
            added.append(key)

    if added:
        ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for key in DEFAULTS:
        value = existing.get(key, DEFAULTS[key] if key in added else "")
        print(f"{key}={'set' if value else 'missing'}")


if __name__ == "__main__":
    main()
