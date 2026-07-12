#!/usr/bin/env python3
"""Convert CRLF and lone CR to LF in deploy shell scripts."""
from __future__ import annotations

import pathlib
import sys

DEFAULT_SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent


def normalize_script_bytes(content: bytes) -> bytes:
    if b"\r" not in content:
        return content
    return content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def normalize_script_file(path: pathlib.Path) -> bool:
    original = path.read_bytes()
    normalized = normalize_script_bytes(original)
    if normalized == original:
        return False
    path.write_bytes(normalized)
    return True


def normalize_scripts_directory(scripts_dir: pathlib.Path) -> list[pathlib.Path]:
    if not scripts_dir.is_dir():
        raise FileNotFoundError(f"Scripts directory not found: {scripts_dir}")

    fixed: list[pathlib.Path] = []
    for path in sorted(scripts_dir.glob("*.sh")):
        if normalize_script_file(path):
            fixed.append(path)
    return fixed


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    scripts_dir = pathlib.Path(args[0]) if args else DEFAULT_SCRIPTS_DIR
    fixed = normalize_scripts_directory(scripts_dir)
    for path in fixed:
        print("normalized line endings in", path)
    if not fixed:
        print("no CRLF changes needed in", scripts_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
