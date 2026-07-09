#!/usr/bin/env bash
# Milestone 8A — SSH hardening: deploy user, package updates, UFW.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

require_root

log "Milestone 8A — base access and hardening"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y

if ! id "$DEPLOY_USER" &>/dev/null; then
  log "Creating deploy user: $DEPLOY_USER"
  adduser --disabled-password --gecos "" "$DEPLOY_USER"
  usermod -aG sudo "$DEPLOY_USER"
  log "Set a password for $DEPLOY_USER if you use password SSH:"
  log "  passwd $DEPLOY_USER"
  log "Or copy your SSH key to /home/$DEPLOY_USER/.ssh/authorized_keys"
else
  log "Deploy user already exists: $DEPLOY_USER"
fi

if ! command -v ufw &>/dev/null; then
  apt-get install -y ufw
fi

ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

log "UFW status:"
ufw status verbose

log "8A complete."
log "Verify from your machine: ssh ${DEPLOY_USER}@$(curl -sf --max-time 5 https://api.ipify.org 2>/dev/null || echo YOUR_SERVER_IP)"
log "On server: sudo whoami (as $DEPLOY_USER) should print root."
