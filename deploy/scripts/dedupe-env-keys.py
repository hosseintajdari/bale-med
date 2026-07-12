#!/usr/bin/env python3
"""Remove duplicate KEY= lines from server .env (keeps last value per key)."""
from __future__ import annotations

import pathlib
import sys

ENV_PATH = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/bale-bot/.env")


def _key_from_line(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    return stripped.split("=", 1)[0].strip()


def main() -> None:
    lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    seen: set[str] = set()
    out_reversed: list[str] = []
    removed = 0

    for line in reversed(lines):
        key = _key_from_line(line)
        if key is not None:
            if key in seen:
                removed += 1
                continue
            seen.add(key)
        out_reversed.append(line)

    ENV_PATH.write_text("\n".join(reversed(out_reversed)) + "\n", encoding="utf-8")
    print(f"deduped {ENV_PATH} removed_duplicate_lines={removed}")


if __name__ == "__main__":
    main()
