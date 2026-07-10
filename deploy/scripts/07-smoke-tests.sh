#!/usr/bin/env bash
# Milestone 8G — HTTPS smoke tests, database row, backup, log safety.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

DOMAIN="${DOMAIN:-}"
MESSAGE_ID="${MESSAGE_ID:-2}"

[[ -n "$DOMAIN" ]] || die "Set DOMAIN env var, e.g. DOMAIN=bot.example.ir bash deploy/scripts/07-smoke-tests.sh"

load_env_if_present
assert_sending_disabled
[[ -n "${BALE_WEBHOOK_SECRET:-}" ]] || die "BALE_WEBHOOK_SECRET required in .env"

log "Milestone 8G — smoke tests for https://$DOMAIN"

curl -sf "https://${DOMAIN}/health" | grep -q '"status":"ok"' || die "Health check failed."

local_status="$(curl -s -o /dev/null -w '%{http_code}' "https://${DOMAIN}/local/reviews/pending")"
[[ "$local_status" == "404" ]] || die "Expected /local/* to return 404 publicly, got HTTP $local_status"
log "/local/* blocked at reverse proxy (HTTP $local_status)."

webhook_url="https://${DOMAIN}/webhook/bale/${BALE_WEBHOOK_SECRET}"
response="$(curl -sf -X POST "$webhook_url" \
  -H "Content-Type: application/json" \
  -d "{\"message\":{\"chat\":{\"id\":\"demo-chat\"},\"message_id\":${MESSAGE_ID},\"text\":\"Hello pharmacy\"}}")"
printf 'Webhook response: %s\n' "$response"

cd "$DEPLOY_ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate
python -c "
import sqlite3
conn = sqlite3.connect('${DATABASE_PATH:-/opt/bale-bot/data/bale_bot.db}')
cur = conn.cursor()
cur.execute('select id, text, review_status from incoming_messages order by id desc limit 1')
row = cur.fetchone()
conn.close()
assert row, 'No message row found'
print('Latest row:', row)
"

backup_path="$(python -c "from app.database import create_sqlite_backup; result = create_sqlite_backup(); print(result.backup_path)")"
log "Backup created: $backup_path"

if command -v journalctl &>/dev/null; then
  journalctl -u "$SERVICE_NAME" -n 100 --no-pager
fi

grep -qE 'BALE_ENABLE_SENDING=false' "$DEPLOY_ROOT/.env" || die "BALE_ENABLE_SENDING must remain false."

log "8G complete."
log "Next: DOMAIN=$DOMAIN bash deploy/scripts/08-register-webhook.sh"
