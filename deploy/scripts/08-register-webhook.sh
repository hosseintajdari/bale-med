#!/usr/bin/env bash
# Milestone 8H — register Bale production webhook (sending still disabled).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

DOMAIN="${DOMAIN:-}"

[[ -n "$DOMAIN" ]] || die "Set DOMAIN env var."

load_env_if_present
assert_sending_disabled
[[ -n "${BALE_WEBHOOK_SECRET:-}" ]] || die "BALE_WEBHOOK_SECRET required"
[[ "${BALE_BOT_TOKEN:-}" != "REAL_TOKEN_ON_SERVER_ONLY" ]] || die "Set real BALE_BOT_TOKEN in .env"

WEBHOOK_URL="https://${DOMAIN}/webhook/bale/${BALE_WEBHOOK_SECRET}"

log "Milestone 8H — register Bale webhook for domain: ${DOMAIN}"
log "Webhook URL includes a secret path — not printed here."

cd "$DEPLOY_ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate

WEBHOOK_URL="$WEBHOOK_URL" python -c "
from app.bale_client import BaleClient
import json
import os

def redact_webhook_info(data):
    if not isinstance(data, dict):
        return data
    result = data.get('result')
    if isinstance(result, dict) and 'url' in result:
        copy = dict(data)
        copy['result'] = dict(result)
        copy['result']['url'] = '[redacted]'
        return copy
    return data

client = BaleClient()
print('setWebhook:')
print(json.dumps(client.set_webhook(os.environ['WEBHOOK_URL']), ensure_ascii=False, indent=2))
print('getWebhookInfo:')
print(json.dumps(redact_webhook_info(client.get_webhook_info()), ensure_ascii=False, indent=2))
"

log "Send one controlled test message to the bot in Bale, then verify a database row."
log "Bot must NOT send an outgoing reply while BALE_ENABLE_SENDING=false."
log "Next: bash deploy/scripts/09-monitor-dry-run.sh"
