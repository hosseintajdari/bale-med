#!/usr/bin/env bash
# Milestone 8E — install and enable bale-bot systemd service.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

REPO_DIR="$(repo_deploy_dir)"
UNIT_SRC="$REPO_DIR/deploy/templates/bale-bot.service"
UNIT_DST="/etc/systemd/system/${SERVICE_NAME}.service"

require_root
[[ -f "$DEPLOY_ROOT/.env" ]] || die "Missing $DEPLOY_ROOT/.env"
assert_sending_disabled

log "Milestone 8E — systemd service"

cp "$UNIT_SRC" "$UNIT_DST"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"
sleep 2
systemctl status "$SERVICE_NAME" --no-pager

health_check_local

log "Recent logs (check for sanitized output — no tokens, chat ids, full patient text):"
journalctl -u "$SERVICE_NAME" -n 50 --no-pager

if journalctl -u "$SERVICE_NAME" -n 200 --no-pager | grep -qiE 'BALE_BOT_TOKEN|webhook.secret|demo-chat'; then
  die "Logs may contain sensitive data. Review journalctl output before continuing."
fi

log "8E complete."
log "Next: set DOMAIN and run sudo bash deploy/scripts/06-caddy.sh"
