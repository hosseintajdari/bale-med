#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

pick_python() {
  local candidate
  for candidate in ${PYTHON:+"$PYTHON"} "$ROOT/.venv/bin/python" python3 python; do
    if [ -x "$candidate" ] || command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 0) else 1)' >/dev/null 2>&1; then
        echo "$candidate"
        return 0
      fi
    fi
  done
  return 1
}

if ! PYTHON="$(pick_python)"; then
  echo "error: no working Python 3 found in PATH (set PYTHON to a Python 3 interpreter)" >&2
  exit 1
fi

echo "==> unittest"
"$PYTHON" -m unittest discover -s tests

echo "==> compileall"
"$PYTHON" -m compileall app tests

echo "==> ruff"
if ! "$PYTHON" -m ruff --version >/dev/null 2>&1; then
  "$PYTHON" -m pip install -q -r requirements-dev.txt
fi
"$PYTHON" -m ruff check app tests

echo "==> git diff --check"
git diff --check

echo "All verification checks passed."
