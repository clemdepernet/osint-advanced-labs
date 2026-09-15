#!/usr/bin/env bash
# opsec_check.sh - Pre-flight OPSEC check of the investigation environment.
#
# Run it INSIDE the environment you are about to investigate from (OSINT
# container, VM, or host) BEFORE touching a target. It answers one question:
# "what does this machine leak about me right now?"
#
# Usage:
#   ./opsec_check.sh                       # basic checks
#   ./opsec_check.sh --home-country FR     # FAIL if the exit country == your real country
#   ./opsec_check.sh --scan-dir ./exports  # look for metadata leaks in files you will publish
#   ./opsec_check.sh --expect-tor          # FAIL if traffic does not exit through Tor
#
# Exit code: 0 = all PASS, 1 = at least one FAIL (WARN does not fail).
set -u

HOME_COUNTRY=""
SCAN_DIR=""
EXPECT_TOR=0
TOR_PROXY="${TOR_PROXY:-127.0.0.1:9050}"
CURL="curl -s --max-time 12"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --home-country) HOME_COUNTRY="$(echo "$2" | tr "[:lower:]" "[:upper:]")"; shift 2 ;;
    --scan-dir)     SCAN_DIR="$2"; shift 2 ;;
    --expect-tor)   EXPECT_TOR=1; shift ;;
    -h|--help)      sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown option $1"; exit 2 ;;
  esac
done

RED=$'\e[31m'; GRN=$'\e[32m'; YLW=$'\e[33m'; BLU=$'\e[34m'; RST=$'\e[0m'
FAILS=0
pass() { printf "%s[PASS]%s %s\n" "$GRN" "$RST" "$1"; }
warn() { printf "%s[WARN]%s %s\n" "$YLW" "$RST" "$1"; }
fail() { printf "%s[FAIL]%s %s\n" "$RED" "$RST" "$1"; FAILS=$((FAILS+1)); }
head_() { printf "\n%s== %s ==%s\n" "$BLU" "$1" "$RST"; }

# ---------------------------------------------------------------- 1. system
head_ "System identity"
HN=$(hostname)
case "$HN" in
  *"$(whoami)"*|*macbook*|*MacBook*|*laptop*|*-pc|*-PC) warn "hostname '$HN' looks personal (rename the VM/container)";;
  *) pass "hostname '$HN' is neutral";;
esac

TZ_NOW=$(date +%Z)
if [[ "$TZ_NOW" == "UTC" || "$TZ_NOW" == "GMT" ]]; then
  pass "timezone is $TZ_NOW"
else
  fail "timezone is '$TZ_NOW' (reveals your region). Fix: sudo timedatectl set-timezone UTC  (or export TZ=UTC)"
fi

LANG_NOW="${LANG:-unset}"
case "$LANG_NOW" in
  C*|POSIX|en_US*|unset) pass "LANG=$LANG_NOW (neutral)";;
  *) warn "LANG=$LANG_NOW reveals a language. Fix: export LANG=en_US.UTF-8";;
esac

if [[ -n "${HISTFILE:-}" && -f "${HISTFILE:-}" ]]; then
  N=$(wc -l < "$HISTFILE" | tr -d ' ')
  warn "shell history has $N lines in $HISTFILE (case data may persist across sessions)"
fi

# ---------------------------------------------------------------- 2. network
head_ "Network exit (direct)"
DIRECT_JSON=$($CURL https://ipinfo.io/json 2>/dev/null)
if [[ -z "$DIRECT_JSON" ]]; then
  warn "no direct internet access (fine if you are Tor-only / offline)"
  DIRECT_IP=""; DIRECT_CC=""
else
  DIRECT_IP=$(echo "$DIRECT_JSON" | sed -n 's/.*"ip": *"\([^"]*\)".*/\1/p')
  DIRECT_CC=$(echo "$DIRECT_JSON" | sed -n 's/.*"country": *"\([^"]*\)".*/\1/p')
  DIRECT_ORG=$(echo "$DIRECT_JSON" | sed -n 's/.*"org": *"\([^"]*\)".*/\1/p')
  echo "       public IP : $DIRECT_IP  country=$DIRECT_CC  org=$DIRECT_ORG"
  if [[ -n "$HOME_COUNTRY" && "$DIRECT_CC" == "$HOME_COUNTRY" ]]; then
    fail "direct exit country ($DIRECT_CC) == home country. Your VPN/Tor is NOT active."
  elif [[ -n "$HOME_COUNTRY" ]]; then
    pass "direct exit country $DIRECT_CC != home $HOME_COUNTRY"
  fi
  case "$DIRECT_ORG" in
    *Orange*|*SFR*|*Bouygues*|*Free*|*Comcast*|*Vodafone*|*Telekom*|*BT\ *|*Telefonica*|*Proximus*)
      fail "org '$DIRECT_ORG' is a residential ISP: you are exposing your real connection";;
    *) pass "org does not look like a residential ISP";;
  esac
fi

head_ "Network exit (Tor)"
if (echo > /dev/tcp/${TOR_PROXY%:*}/${TOR_PROXY#*:}) 2>/dev/null; then
  TOR_JSON=$($CURL --socks5-hostname "$TOR_PROXY" https://check.torproject.org/api/ip 2>/dev/null)
  if echo "$TOR_JSON" | grep -q '"IsTor":true'; then
    TOR_IP=$(echo "$TOR_JSON" | sed -n 's/.*"IP":"\([^"]*\)".*/\1/p')
    pass "Tor SOCKS on $TOR_PROXY works, exit IP $TOR_IP"
    [[ -n "$DIRECT_IP" && "$DIRECT_IP" == "$TOR_IP" ]] && fail "direct IP == Tor IP ?! something is wrong"
  else
    fail "port $TOR_PROXY open but check.torproject.org says IsTor!=true"
  fi
else
  if [[ $EXPECT_TOR -eq 1 ]]; then
    fail "no Tor SOCKS proxy on $TOR_PROXY (start tor: 'sudo service tor start' or 'tor &')"
  else
    warn "no Tor SOCKS proxy on $TOR_PROXY (ok if your plan is VPN-only)"
  fi
fi

head_ "DNS resolvers"
if [[ -f /etc/resolv.conf ]]; then
  RES=$(grep -E '^nameserver' /etc/resolv.conf | awk '{print $2}' | tr '\n' ' ')
  echo "       resolv.conf: $RES"
  case "$RES" in
    *192.168.*|*10.*|*172.1[6-9].*|*172.2[0-9].*|*172.3[01].*)
      warn "DNS goes to a private/LAN resolver (likely your box/ISP). DNS leak possible if VPN is not full-tunnel.";;
    *) pass "no obvious LAN resolver";;
  esac
elif command -v scutil >/dev/null; then
  scutil --dns | grep 'nameserver\[0\]' | sort -u | sed 's/^/       /'
  warn "macOS host detected: run this check inside the container/VM, not on the host"
fi

# ---------------------------------------------------------------- 3. leaks in files
if [[ -n "$SCAN_DIR" ]]; then
  head_ "Metadata in files to be shared ($SCAN_DIR)"
  if ! command -v exiftool >/dev/null; then
    warn "exiftool missing (apt install libimage-exiftool-perl / brew install exiftool)"
  else
    LEAKS=0
    while IFS= read -r -d '' f; do
      HIT=$(exiftool -s -GPSLatitude -GPSPosition -Author -Creator -Artist -OwnerName \
                     -SerialNumber -BodySerialNumber -LensSerialNumber -Software -LastModifiedBy \
                     -Company -HostComputer "$f" 2>/dev/null | grep -v '^$')
      if [[ -n "$HIT" ]]; then
        LEAKS=$((LEAKS+1))
        echo "       $f"
        echo "$HIT" | sed 's/^/           /'
      fi
    done < <(find "$SCAN_DIR" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.pdf' -o -iname '*.docx' -o -iname '*.xlsx' -o -iname '*.mp4' -o -iname '*.mov' \) -print0)
    if [[ $LEAKS -gt 0 ]]; then
      fail "$LEAKS file(s) carry identifying metadata. Fix: exiftool -all= -overwrite_original <file>"
    else
      pass "no identifying metadata found"
    fi
  fi
fi

# ---------------------------------------------------------------- 4. reminders you cannot automate
head_ "Manual checks (cannot be scripted)"
echo "       - Browser fingerprint: https://coveryourtracks.eff.org  and  https://amiunique.org"
echo "       - WebRTC / DNS leak from the browser: https://browserleaks.com/webrtc"
echo "       - Are you logged into ANY personal account in this browser profile?"
echo "       - Is Hunchly capturing (green icon) in the persona browser?"

# ---------------------------------------------------------------- summary
echo
if [[ $FAILS -eq 0 ]]; then
  printf "%sRESULT: GO%s - no blocking issue detected.\n" "$GRN" "$RST"; exit 0
else
  printf "%sRESULT: NO-GO%s - %d blocking issue(s). Fix them before investigating.\n" "$RED" "$RST" "$FAILS"; exit 1
fi
