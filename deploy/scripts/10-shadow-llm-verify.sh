#!/usr/bin/env bash
# Milestone 9 — pull shadow LLM code, verify env, restart, check /local/reviews/pending.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

GIT_REF="${GIT_REF:-origin/main}"
RESTART_SERVICE="${RESTART_SERVICE:-true}"

log "Milestone 9 — shadow LLM deploy + verify"

cd "$DEPLOY_ROOT"

if [[ -d .git ]]; then
  log "Fetching and checking out $GIT_REF"
  git fetch origin
  git checkout "${GIT_REF#origin/}" 2>/dev/null || git checkout -B "${GIT_REF#origin/}" "$GIT_REF"
  git pull --ff-only origin "${GIT_REF#origin/}" || true
else
  die "No git repo at $DEPLOY_ROOT — clone bale-med first."
fi

if command -v python3 >/dev/null 2>&1; then
  python3 deploy/scripts/normalize-deploy-scripts.py deploy/scripts || true
fi

# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

load_env_if_present

if [[ "${BALE_ENABLE_LLM:-false}" != "true" ]]; then
  log "WARNING: BALE_ENABLE_LLM is not true — add LLM vars to $DEPLOY_ROOT/.env:"
  cat <<'EOF'
BALE_ENABLE_LLM=true
BALE_LLM_MODE=shadow
BALE_LLM_API_BASE_URL=https://YOUR_PROVIDER/v1
BALE_LLM_API_KEY=YOUR_KEY
BALE_LLM_MODEL=gpt-4o-mini
EOF
fi

if [[ "${BALE_LLM_MODE:-shadow}" != "shadow" ]]; then
  log "WARNING: BALE_LLM_MODE=${BALE_LLM_MODE:-unset} — shadow deploy expects shadow."
fi

if [[ "$RESTART_SERVICE" == "true" ]]; then
  log "Restarting $SERVICE_NAME"
  sudo systemctl restart "$SERVICE_NAME"
  sleep 2
fi

health_check_local

log "Local /local/reviews/pending (loopback only):"
pending_json="$(curl -sS http://127.0.0.1:8000/local/reviews/pending)"
printf '%s\n' "$pending_json" | python3 -m json.tool

python3 <<'PY'
import json
import sys

payload = json.loads(sys.stdin.read())
items = payload.get("pending_reviews", [])
llm_items = [i for i in items if i.get("llm_status")]
print(f"pending_count={len(items)} llm_populated={len(llm_items)}")
if llm_items:
    sample = llm_items[0]
    print(
        "sample:",
        {
            "id": sample.get("id"),
            "llm_status": sample.get("llm_status"),
            "llm_extracted": sample.get("llm_extracted"),
        },
    )
PY
<<<"$pending_json"

log "Recent LLM log lines (no prompt/response text expected):"
journalctl -u "$SERVICE_NAME" -n 100 --no-pager | grep -E 'llm_status|llm_classification' || log "(no llm log lines yet — send test messages to @embednebot)"

log "Public /local/reviews/pending must stay blocked (404 via Caddy):"
if [[ -n "${DOMAIN:-}" ]]; then
  public_status="$(curl -s -o /dev/null -w '%{http_code}' "https://${DOMAIN}/local/reviews/pending" || true)"
  log "https://${DOMAIN}/local/reviews/pending -> HTTP $public_status (expect 404)"
else
  log "Set DOMAIN=your-domain.example to check public block."
fi

log "Milestone 9 shadow verify complete."
