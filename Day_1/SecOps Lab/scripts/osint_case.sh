#!/usr/bin/env bash
# osint_case.sh - one disposable container per case, one workspace per case.
#
# Usage:
#   ./osint_case.sh start  CASE-042            # create/enter the container for the case
#   ./osint_case.sh start  CASE-042 --keep     # keep the container after exit (default: destroyed)
#   ./osint_case.sh shell  CASE-042            # open another shell in a running --keep container
#   ./osint_case.sh check  CASE-042            # run opsec_check.sh inside the container
#   ./osint_case.sh purge  CASE-042            # destroy container (workspace on host is kept)
#
# Design choices (explain them in your OPSEC note):
#   - --rm by default        : nothing survives the session except /workspace
#   - --hostname            : neutral name, never your machine's name
#   - TZ=UTC, LANG=C.UTF-8  : no regional leak
#   - workspace on host      : ~/osint-cases/<CASE>/ {captures,exports,notes,logs}
#   - no host network        : container has its own stack (bridge). Tor runs inside.
#   - --cap-drop ALL         : least privilege
set -euo pipefail

IMAGE="${OSINT_IMAGE:-osint-lab:latest}"
BASE="${OSINT_CASES_DIR:-$HOME/osint-cases}"
ACTION="${1:-}"; CASE="${2:-}"; shift 2 2>/dev/null || true
[[ -z "$ACTION" || -z "$CASE" ]] && { sed -n '2,20p' "$0"; exit 2; }

NAME="osint-$(echo "$CASE" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9\n' '-')"
WS="$BASE/$CASE"
HERE="$(cd "$(dirname "$0")" && pwd)"

case "$ACTION" in
  start)
    KEEP=0; [[ "${1:-}" == "--keep" ]] && KEEP=1
    mkdir -p "$WS"/{captures,exports,notes,logs}
    cp -n "$HERE"/{opsec_check.sh,footprint_audit.py,persona_forge.py} "$WS/" 2>/dev/null || true
    if docker ps -a --format '{{.Names}}' | grep -qx "$NAME"; then
      echo "[*] container $NAME exists, resuming"; docker start -ai "$NAME"; exit $?
    fi
    RM="--rm"; [[ $KEEP -eq 1 ]] && RM=""
    echo "[*] case=$CASE  container=$NAME  workspace=$WS  image=$IMAGE"
    echo "[*] session start $(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$WS/logs/sessions.log"
    docker run -it $RM \
      --name "$NAME" \
      --hostname "workstation" \
      --env TZ=UTC --env LANG=C.UTF-8 --env CASE="$CASE" \
      --cap-drop ALL --cap-add CHOWN --cap-add SETUID --cap-add SETGID --cap-add DAC_OVERRIDE \
      --security-opt no-new-privileges \
      --volume "$WS:/workspace" \
      "$IMAGE" zsh
    echo "[*] session end   $(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$WS/logs/sessions.log"
    ;;
  shell)
    docker exec -it -u analyst -w /workspace "$NAME" zsh ;;
  check)
    docker exec -it -u analyst -w /workspace "$NAME" bash ./opsec_check.sh --expect-tor "$@" ;;
  purge)
    docker rm -f "$NAME" 2>/dev/null && echo "[+] $NAME removed" || echo "[i] no container $NAME"
    echo "[i] workspace kept at $WS (encrypt/archive it, then shred if the case is closed)" ;;
  *) echo "unknown action $ACTION"; exit 2 ;;
esac
