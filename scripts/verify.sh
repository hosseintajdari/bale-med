#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

pick_python() {
  local candidate
  for candidate in ${PYTHON:+"$PYTHON"} python python3; do
    if command -v "$candidate" >/dev/null 2>&1 \
      && "$candidate" -c "import sys" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

if ! PYTHON="$(pick_python)"; then
  echo "error: no working python or python3 found in PATH" >&2
  exit 1
fi

echo "==> unittest"
"$PYTHON" -m unittest discover -s tests

echo "==> compileall"
"$PYTHON" -m compileall app tests

echo "==> git diff --check"
git diff --check

echo "All verification checks passed."
