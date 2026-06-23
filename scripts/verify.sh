#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"

echo "==> unittest"
"$PYTHON" -m unittest discover -s tests

echo "==> compileall"
"$PYTHON" -m compileall app tests

echo "==> git diff --check"
git diff --check

echo "All verification checks passed."
