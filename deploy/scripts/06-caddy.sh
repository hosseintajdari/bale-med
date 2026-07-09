#!/usr/bin/env bash
# Milestone 8F — Caddy reverse proxy, HTTPS, block /local/* publicly.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

DOMAIN="${DOMAIN:-}"
REPO_DIR="$(repo_deploy_dir)"
CADDY_TEMPLATE="$REPO_DIR/deploy/templates/Caddyfile"
CADDY_DST="/etc/caddy/Caddyfile"

require_root
[[ -n "$DOMAIN" ]] || die "Set DOMAIN env var, e.g. DOMAIN=bot.example.ir sudo bash deploy/scripts/06-caddy.sh"
assert_sending_disabled

log "Milestone 8F — Caddy HTTPS for $DOMAIN"
log "Ensure DNS A record for $DOMAIN points to this server before continuing."

export DEBIAN_FRONTEND=noninteractive
if ! command -v caddy &>/dev/null; then
  apt-get update
  apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl gnupg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
  apt-get update
  apt-get install -y caddy
fi

sed "s/YOUR_DOMAIN/$DOMAIN/g" "$CADDY_TEMPLATE" > "$CADDY_DST"
caddy validate --config "$CADDY_DST"
systemctl enable caddy
systemctl reload caddy
systemctl status caddy --no-pager

log "Waiting for HTTPS (DNS + certificate may take a minute)..."
for _ in $(seq 1 60); do
  if curl -sf "https://${DOMAIN}/health" | grep -q '"status":"ok"'; then
    log "HTTPS health OK."
    break
  fi
  sleep 2
done

curl -sf "https://${DOMAIN}/health" | grep -q '"status":"ok"' || die "HTTPS health check failed for https://${DOMAIN}/health"

local_status="$(curl -s -o /dev/null -w '%{http_code}' "https://${DOMAIN}/local/reviews/pending")"
[[ "$local_status" == "404" ]] || die "Expected /local/* to return 404 publicly, got HTTP $local_status"

if ss -tln | grep -q '0.0.0.0:8000'; then
  die "uvicorn must bind 127.0.0.1 only, not 0.0.0.0"
fi

log "8F complete."
log "Next: DOMAIN=$DOMAIN bash deploy/scripts/07-smoke-tests.sh"
