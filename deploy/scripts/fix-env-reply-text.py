#!/usr/bin/env python3
"""Quote BALE_REPLY_TEXT in server .env so bash can source it safely."""
from __future__ import annotations

import pathlib
import sys

ENV_PATH = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/bale-bot/.env")

lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
out: list[str] = []
for line in lines:
    if line.startswith("BALE_REPLY_TEXT="):
        key, _, val = line.partition("=")
        val = val.strip()
        if not (len(val) >= 2 and val[0] == val[-1] == '"'):
            val = '"' + val.replace('"', '\\"') + '"'
        line = f"{key}={val}"
    out.append(line)

ENV_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")
print("fixed BALE_REPLY_TEXT quoting in", ENV_PATH)
