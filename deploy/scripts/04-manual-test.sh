#!/usr/bin/env bash
# Milestone 8D — manual uvicorn run and local health + mock webhook test.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

PORT="${PORT:-8000}"
UVICORN_PID=""

cleanup() {
  if [[ -n "$UVICORN_PID" ]] && kill -0 "$UVICORN_PID" 2>/dev/null; then
    kill "$UVICORN_PID" 2>/dev/null || true
    wait "$UVICORN_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

log "Milestone 8D — manual app test on 127.0.0.1:$PORT"

[[ -f "$DEPLOY_ROOT/.env" ]] || die "Missing $DEPLOY_ROOT/.env — run 03-configure-env.sh first."
assert_sending_disabled

load_env_if_present
[[ -n "${BALE_WEBHOOK_SECRET:-}" ]] || die "BALE_WEBHOOK_SECRET must be set in .env"
[[ "${BALE_WEBHOOK_SECRET}" != "LONG_RANDOM_SECRET_ON_SERVER_ONLY" ]] || die "Replace placeholder BALE_WEBHOOK_SECRET in .env"

cd "$DEPLOY_ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate

if ss -tln 2>/dev/null | grep -q ":${PORT} "; then
  die "Port $PORT already in use. Stop bale-bot service or other process first."
fi

log "Starting uvicorn (background for this test)..."
uvicorn app.main:app --host 127.0.0.1 --port "$PORT" &
UVICORN_PID=$!

for _ in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

health_check_local
log "Health OK."

webhook_url="http://127.0.0.1:${PORT}/webhook/bale/${BALE_WEBHOOK_SECRET}"
response="$(curl -sf -X POST "$webhook_url" \
  -H "Content-Type: application/json" \
  -d '{"message":{"chat":{"id":"demo-chat"},"message_id":1,"text":"Hello pharmacy"}}')"
printf 'Webhook response: %s\n' "$response"

if [[ -f "${DATABASE_PATH:-$DATA_DIR/bale_bot.db}" ]]; then
  log "SQLite database file exists."
else
  die "Expected SQLite database after webhook test."
fi

log "8D complete. No Bale message sent (BALE_ENABLE_SENDING=false)."
log "Next: sudo bash deploy/scripts/05-systemd.sh"
