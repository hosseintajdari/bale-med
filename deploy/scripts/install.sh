#!/usr/bin/env bash
# Milestone 8 — orchestrate VPS deployment steps 8A through 8I.
# Run on Ubuntu VPS after SSH login. See deploy/README.md.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

normalize_deploy_scripts() {
  if command -v python3 &>/dev/null; then
    python3 "$SCRIPT_DIR/normalize-deploy-scripts.py" "$SCRIPT_DIR"
  fi
}

usage() {
  cat <<'EOF'
Usage: install.sh <step|all|through-N>

Steps:
  preflight   00 — SSH session and server basics
  8a          01 — hardening (root/sudo)
  8b          02 — Python, git, clone, venv
  8c          03 — .env template (edit secrets before 8d)
  8d          04 — manual uvicorn test
  8e          05 — systemd (root/sudo)
  8f          06 — Caddy HTTPS (requires DOMAIN, root/sudo)
  8g          07 — smoke tests (requires DOMAIN)
  8h          08 — Bale webhook (requires DOMAIN)
  8i          09 — dry-run monitoring
  9a|10       10 — Milestone 9 shadow LLM pull + verify

Examples:
  sudo bash deploy/scripts/install.sh preflight
  sudo bash deploy/scripts/install.sh 8a
  sudo -u deploy bash deploy/scripts/install.sh 8b
  bash deploy/scripts/install.sh 8c
  DOMAIN=bot.example.ir sudo bash deploy/scripts/install.sh 8f

  sudo bash deploy/scripts/install.sh through-8e
  DOMAIN=bot.example.ir bash deploy/scripts/install.sh through-8i

Environment:
  DOMAIN       Production hostname (required for 8f–8h)
  REPO_URL     Git clone URL (default: GitHub bale-med)
  DEPLOY_ROOT  App path (default: /opt/bale-bot)
EOF
}

run_step() {
  local step="$1"
  case "$step" in
    preflight|00) bash "$SCRIPT_DIR/00-preflight.sh" ;;
    8a|01) bash "$SCRIPT_DIR/01-hardening.sh" ;;
    8b|02) bash "$SCRIPT_DIR/02-bootstrap.sh" ;;
    8c|03) bash "$SCRIPT_DIR/03-configure-env.sh" ;;
    8d|04) bash "$SCRIPT_DIR/04-manual-test.sh" ;;
    8e|05) bash "$SCRIPT_DIR/05-systemd.sh" ;;
    8f|06) bash "$SCRIPT_DIR/06-caddy.sh" ;;
    8g|07) bash "$SCRIPT_DIR/07-smoke-tests.sh" ;;
    8h|08) bash "$SCRIPT_DIR/08-register-webhook.sh" ;;
    8i|09) bash "$SCRIPT_DIR/09-monitor-dry-run.sh" ;;
    9a|10) bash "$SCRIPT_DIR/10-shadow-llm-verify.sh" ;;
    *) die "Unknown step: $step" ;;
  esac
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

STEP="${1:-}"
[[ -n "$STEP" ]] || { usage; exit 1; }

case "$STEP" in
  -h|--help|help) usage; exit 0 ;;
esac

normalize_deploy_scripts

case "$STEP" in
  all|through-8i)
    run_step preflight
    run_step 8a
    run_step 8b
    run_step 8c
    printf '\n*** Edit /opt/bale-bot/.env with real token and webhook secret, then press Enter ***\n'
    read -r _
    run_step 8d
    run_step 8e
    [[ -n "${DOMAIN:-}" ]] || die "Set DOMAIN before 8f–8i"
    run_step 8f
    run_step 8g
    run_step 8h
    run_step 8i
    ;;
  through-8e)
    run_step preflight
    run_step 8a
    run_step 8b
    run_step 8c
    printf '\n*** Edit /opt/bale-bot/.env, then press Enter ***\n'
    read -r _
    run_step 8d
    run_step 8e
    ;;
  *)
    run_step "$STEP"
    ;;
esac
