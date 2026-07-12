#!/usr/bin/env python3
"""Print safe .env health check (no secret values)."""
from __future__ import annotations

from pathlib import Path

ENV_PATH = Path("/opt/bale-bot/.env")

CHECK_KEYS = (
    "BALE_BOT_TOKEN",
    "BALE_ENABLE_SENDING",
    "BALE_WEBHOOK_SECRET",
    "BALE_ENABLE_LLM",
    "BALE_LLM_MODE",
    "BALE_LLM_API_BASE_URL",
    "BALE_LLM_API_KEY",
    "BALE_LLM_MODEL",
)


def main() -> None:
    text = ENV_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    values: dict[str, str] = {}
    problems: list[str] = []

    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            problems.append(f"line {index}: not KEY=VALUE")
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key in values:
            problems.append(f"duplicate key: {key}")
        values[key] = value
        if key.startswith("BALE_LLM_") and "BALE_LLM_" in value:
            problems.append(f"line {index}: {key} looks merged with another line")
        if value.startswith('"') or value.startswith("'"):
            problems.append(f"line {index}: {key} has quotes (remove them)")

    for key in CHECK_KEYS:
        value = values.get(key, "")
        status = "missing" if key not in values else ("empty" if not value else f"len={len(value)}")
        print(f"{key}={status}")

    for problem in problems:
        print(f"PROBLEM: {problem}")


if __name__ == "__main__":
    main()
