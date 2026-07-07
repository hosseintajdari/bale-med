#!/usr/bin/env bash
# Milestone 8 — preflight: verify SSH session, OS, Python, ports policy.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

log "Milestone 8 preflight (SSH session and server basics)"

printf 'SSH user: %s\n' "$(whoami)"
printf 'Hostname: %s\n' "$(hostname)"

if [[ -f /etc/os-release ]]; then
  # shellcheck disable=SC1091
  source /etc/os-release
  printf 'OS: %s %s\n' "${NAME:-unknown}" "${VERSION_ID:-}"
  case "${ID:-}" in
    ubuntu)
      case "${VERSION_ID:-}" in
        22.04|24.04) log "Ubuntu LTS version is supported." ;;
        *) printf 'WARN: Ubuntu %s is not the documented 22.04/24.04 target. Continue with caution.\n' "${VERSION_ID:-}" ;;
      esac
      ;;
    *)
      printf 'WARN: OS is not Ubuntu. Scripts are tested for Ubuntu 22.04/24.04 only.\n'
      ;;
  esac
else
  printf 'WARN: /etc/os-release not found.\n'
fi

if command -v python3 &>/dev/null; then
  py_version="$(python3 --version 2>&1)"
  printf 'Python: %s\n' "$py_version"
  major="$(python3 -c 'import sys; print(sys.version_info.major)')"
  minor="$(python3 -c 'import sys; print(sys.version_info.minor)')"
  if [[ "$major" -lt 3 || ( "$major" -eq 3 && "$minor" -lt 11 ) ]]; then
    printf 'WARN: Python 3.11+ recommended. Install step 8B will install packages.\n'
  fi
else
  log "python3 not installed yet (expected before 8B)."
fi

for cmd in curl git; do
  if command -v "$cmd" &>/dev/null; then
    printf 'Found: %s\n' "$cmd"
  else
    printf 'Note: %s not installed yet (8B will install).\n' "$cmd"
  fi
done

if command -v ufw &>/dev/null; then
  log "UFW status:"
  ufw status verbose || true
else
  log "UFW not configured yet (8A will configure)."
fi

if command -v ss &>/dev/null; then
  log "Listening ports (sample):"
  ss -tln | head -20 || true
fi

public_ip=""
if command -v curl &>/dev/null; then
  public_ip="$(curl -sf --max-time 5 https://api.ipify.org 2>/dev/null || true)"
fi
if [[ -n "$public_ip" ]]; then
  printf 'Detected public IPv4 (for DNS A record): %s\n' "$public_ip"
else
  printf 'Could not auto-detect public IP. Set DNS A record manually from provider panel.\n'
fi

log "Preflight complete."
log "Next: sudo bash deploy/scripts/01-hardening.sh"
