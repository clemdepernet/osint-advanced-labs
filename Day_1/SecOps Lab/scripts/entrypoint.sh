#!/usr/bin/env bash
# entrypoint.sh - start Tor in the background, then hand over to the shell.
set -e
if ! pgrep -x tor >/dev/null; then
  mkdir -p /var/lib/tor && chown analyst:analyst /var/lib/tor
  su -s /bin/sh analyst -c "tor -f /etc/tor/torrc >/tmp/tor.log 2>&1 &"
  # wait (max 40s) for the SOCKS port and bootstrap
  for i in $(seq 1 40); do
    grep -q "Bootstrapped 100%" /tmp/tor.log 2>/dev/null && break
    sleep 1
  done
  grep -q "Bootstrapped 100%" /tmp/tor.log 2>/dev/null \
    && echo "[+] Tor ready on 127.0.0.1:9050" \
    || echo "[!] Tor not bootstrapped yet (check /tmp/tor.log). Continuing."
fi
echo "[i] $(date -u '+%Y-%m-%d %H:%M:%S UTC') | hostname=$(hostname) | TZ=$TZ | workspace=/workspace"
exec su -s /bin/zsh analyst -c "cd /workspace && exec $*"
