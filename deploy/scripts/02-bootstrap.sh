#!/usr/bin/env bash
# Milestone 8B — Python, Git, clone repo, virtualenv, dependencies.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

REPO_URL="${REPO_URL:-https://github.com/hosseintajdari/bale-med.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"

require_deploy_user

log "Milestone 8B — runtime bootstrap"

export DEBIAN_FRONTEND=noninteractive
if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
  apt-get update
  apt-get install -y python3 python3-venv python3-pip git curl
fi

python3 --version
git --version

if [[ ! -d "$DEPLOY_ROOT/.git" ]]; then
  log "Cloning $REPO_URL (branch $REPO_BRANCH) to $DEPLOY_ROOT"
  sudo mkdir -p "$DEPLOY_ROOT"
  sudo chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_ROOT"
  sudo -u "$DEPLOY_USER" git clone --branch "$REPO_BRANCH" "$REPO_URL" "$DEPLOY_ROOT"
else
  log "Repository already exists at $DEPLOY_ROOT"
  sudo chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_ROOT"
fi

sudo -u "$DEPLOY_USER" bash -lc "
  set -euo pipefail
  cd '$DEPLOY_ROOT'
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  python -m compileall app tests
"

log "8B complete."
log "Next: bash deploy/scripts/03-configure-env.sh (as $DEPLOY_USER)"
