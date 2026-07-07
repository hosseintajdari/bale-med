#!/usr/bin/env bash
# Milestone 8C — create data dir and .env from template (no secrets in Git).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

REPO_DIR="$(repo_deploy_dir)"
TEMPLATE="$REPO_DIR/deploy/templates/env.production.example"
ENV_FILE="$DEPLOY_ROOT/.env"

log "Milestone 8C — configure server .env"

mkdir -p "$DATA_DIR"

if [[ -f "$ENV_FILE" ]]; then
  log ".env already exists at $ENV_FILE — not overwriting."
else
  if [[ ! -f "$TEMPLATE" ]]; then
    die "Template not found: $TEMPLATE"
  fi
  cp "$TEMPLATE" "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  log "Created $ENV_FILE from template."
fi

log "Edit secrets on the server only:"
log "  nano $ENV_FILE"
log "Replace BALE_BOT_TOKEN and BALE_WEBHOOK_SECRET with real values."
log "Keep BALE_ENABLE_SENDING=false and BALE_ENABLE_ADMIN_NOTIFICATIONS=false."

if ! grep -qE '^BALE_ENABLE_SENDING=false' "$ENV_FILE"; then
  die "BALE_ENABLE_SENDING must be false in $ENV_FILE"
fi
if ! grep -qE '^BALE_ENABLE_ADMIN_NOTIFICATIONS=false' "$ENV_FILE"; then
  die "BALE_ENABLE_ADMIN_NOTIFICATIONS=false required in $ENV_FILE"
fi
if ! grep -qE '^BALE_STORE_RAW_UPDATES=false' "$ENV_FILE"; then
  die "BALE_STORE_RAW_UPDATES=false required in $ENV_FILE"
fi

perm="$(stat -c '%a' "$ENV_FILE")"
[[ "$perm" == "600" ]] || chmod 600 "$ENV_FILE"

if [[ -d "$DEPLOY_ROOT/.git" ]]; then
  if git -C "$DEPLOY_ROOT" status --short -- .env 2>/dev/null | grep -q .; then
    die ".env must not be tracked by git."
  fi
fi

log "8C complete (verify token and webhook secret are set before 8D)."
log "Next: bash deploy/scripts/04-manual-test.sh"
