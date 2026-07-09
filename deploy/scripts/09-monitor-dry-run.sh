#!/usr/bin/env bash
# Milestone 8I — dry-run monitoring helpers (sending disabled).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

FOLLOW_LOGS="${FOLLOW_LOGS:-false}"

assert_sending_disabled

log "Milestone 8I — dry-run operation checks"

grep -E 'BALE_ENABLE_SENDING=false|BALE_ENABLE_ADMIN_NOTIFICATIONS=false' "$DEPLOY_ROOT/.env"

cd "$DEPLOY_ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate

python -c "
import sqlite3
conn = sqlite3.connect('${DATABASE_PATH:-/opt/bale-bot/data/bale_bot.db}')
cur = conn.cursor()
cur.execute('select id, length(text), needs_review, review_reason, review_status from incoming_messages order by id desc limit 10')
rows = cur.fetchall()
conn.close()
print('Recent messages (text length only):')
for row in rows:
    print(row)
"

backup_path="$(python -c "from app.database import create_sqlite_backup; result = create_sqlite_backup(); print(result.backup_path)")"
log "Backup: $backup_path"

log "Service status:"
systemctl status "$SERVICE_NAME" --no-pager || true

if [[ "$FOLLOW_LOGS" == "true" ]]; then
  log "Following logs (Ctrl+C to stop)..."
  journalctl -u "$SERVICE_NAME" -f
else
  log "Recent logs:"
  journalctl -u "$SERVICE_NAME" -n 50 --no-pager
  log "To follow logs: FOLLOW_LOGS=true bash deploy/scripts/09-monitor-dry-run.sh"
fi

log "8I dry-run checks complete. Real sending remains disabled until explicit approval (8J)."
