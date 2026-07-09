#!/usr/bin/env bash
# Shared helpers for Milestone 8 VPS deployment scripts.
set -euo pipefail

DEPLOY_ROOT="${DEPLOY_ROOT:-/opt/bale-bot}"
DEPLOY_USER="${DEPLOY_USER:-deploy}"
DATA_DIR="${DATA_DIR:-/opt/bale-bot/data}"
SERVICE_NAME="${SERVICE_NAME:-bale-bot}"

log() {
  printf '==> %s\n' "$*"
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_root() {
  if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    die "Run as root or with sudo: sudo bash $0"
  fi
}

require_deploy_user() {
  id "$DEPLOY_USER" &>/dev/null || die "Deploy user '$DEPLOY_USER' does not exist. Run 01-hardening.sh first."
}

repo_deploy_dir() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [[ -f "$script_dir/../../app/main.py" ]]; then
    cd "$script_dir/../.." && pwd
    return
  fi
  if [[ -d "$DEPLOY_ROOT/app" ]]; then
    printf '%s\n' "$DEPLOY_ROOT"
    return
  fi
  die "Cannot locate bale-med repository. Set DEPLOY_ROOT or run from a cloned repo."
}

load_env_if_present() {
  if [[ -f "$DEPLOY_ROOT/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$DEPLOY_ROOT/.env"
    set +a
  fi
}

assert_sending_disabled() {
  load_env_if_present
  [[ "${BALE_ENABLE_SENDING:-false}" == "false" ]] || die "BALE_ENABLE_SENDING must be false for Milestone 8 dry-run."
  [[ "${BALE_ENABLE_ADMIN_NOTIFICATIONS:-false}" == "false" ]] || die "BALE_ENABLE_ADMIN_NOTIFICATIONS must be false for first deployment."
}

health_check_local() {
  curl -sf http://127.0.0.1:8000/health | grep -q '"status":"ok"' || die "Local health check failed."
}
