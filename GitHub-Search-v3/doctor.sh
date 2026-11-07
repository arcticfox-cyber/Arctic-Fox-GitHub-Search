#!/usr/bin/env bash
# =============================================================================
#   GITHUB SEARCH v3.0 — Doctor
#   Run this when something does not work:
#
#       bash doctor.sh
#
#   It checks everything and prints the FIX for each problem it finds.
#   If you still need help: send a screenshot of this output.
# =============================================================================
set -u

GREEN='\033[38;5;114m'; RED='\033[38;5;203m'; YELL='\033[38;5;221m'
CYAN='\033[38;5;51m'; GREY='\033[38;5;245m'; B='\033[1m'; R='\033[0m'
ok()   { printf " ${GREEN}[OK]${R} %s\n" "$1"; }
bad()  { printf " ${RED}[FIX]${R} %s\n" "$1"; }
warn() { printf " ${YELL}[warn]${R} %s\n" "$1"; }
head_(){ printf "\n${B}${CYAN}== %s ==${R}\n" "$1"; }

PROBLEMS=0

printf "%b\n" " ${B}${CYAN}┌──────────────────────────────────────────┐${R}"
printf "%b\n" " ${B}${CYAN}│   GITHUB SEARCH v2.0 · DOCTOR (diagnosis)   │${R}"
printf "%b\n" " ${B}${CYAN}└──────────────────────────────────────────┘${R}"

# ---------------------------------------------------------------- system ----
head_ "System"
if [ -r /etc/os-release ]; then
    . /etc/os-release
    ok "OS: ${PRETTY_NAME:-unknown}"
    case "${ID:-}${ID_LIKE:-}" in
        *kali*) : ;;
        *) warn "not Kali Linux — installer needs: sudo bash install.sh --force" ;;
    esac
else
    warn "cannot read /etc/os-release"
fi

case "${PREFIX:-}" in
    *com.termux*)
        bad "Termux / NetHunter-rootless detected — desktop GUI is NOT possible here."
        echo "        Use terminal mode:      python3 arcticfox-cli.py"
        ;;
esac

[ -n "${DISPLAY:-}" ] && ok "display: $DISPLAY" || {
    bad "no DISPLAY set — GUI cannot open (SSH or headless?)"
    echo "        Fix A: run it on the Kali desktop itself (not SSH)."
    echo "        Fix B: use terminal mode:  python3 arcticfox-cli.py"
    PROBLEMS=$((PROBLEMS+1))
}

# --------------------------------------------------------------- python -----
head_ "Python"
PY=""
if command -v python3 >/dev/null 2>&1; then
    PY=python3
    ok "python3: $($PY --version 2>&1)"
else
    bad "python3 missing          →  sudo apt install -y python3 python3-tk"
    PROBLEMS=$((PROBLEMS+1))
fi

if [ -n "$PY" ]; then
    if $PY -c "import tkinter" 2>/dev/null; then
        ok "tkinter (python3-tk): present"
    else
        bad "tkinter missing          →  sudo apt install -y python3-tk"
        PROBLEMS=$((PROBLEMS+1))
    fi
fi

if command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
    warn "only 'python' exists (probably python 2) — always use: python3"
fi

# --------------------------------------------------------------- tools ------
head_ "Tools"
command -v git >/dev/null 2>&1 && ok "git: $(git --version | awk '{print $3}')" || {
    bad "git missing              →  sudo apt install -y git"
    PROBLEMS=$((PROBLEMS+1)); }
command -v curl >/dev/null 2>&1 && ok "curl: present" || warn "curl missing (only needed for remote-install)"

# ------------------------------------------------------------- internet -----
head_ "Internet / GitHub API"
CODE="$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 https://api.github.com 2>/dev/null || echo 000)"
case "$CODE" in
    200) ok "api.github.com reachable" ;;
    000) bad "no internet / DNS broken →  check connection, VPN, or DNS"
         echo "        Test:  ping -c2 8.8.8.8   and   curl -I https://github.com"
         PROBLEMS=$((PROBLEMS+1)) ;;
    *)   warn "api.github.com answered HTTP $CODE (proxy/captive portal?)" ;;
esac

if [ -n "$PY" ]; then
    RL="$($PY - <<'EOF' 2>/dev/null
import json, urllib.request
try:
    r = json.load(urllib.request.urlopen("https://api.github.com/rate_limit", timeout=8))
    c = r["resources"]["core"]
    print(f"{c['remaining']}/{c['limit']}")
except Exception:
    print("?")
EOF
)"
    if [ "$RL" = "?" ]; then
        warn "could not read GitHub rate limit (offline?)"
    else
        REM="${RL%%/*}"
        ok "GitHub rate limit (no token): $RL requests left"
        if [ "$REM" -le 5 ]; then
            warn "almost rate-limited → add a token: Settings in the GUI,"
            echo "        or: af  →  Settings → paste a Personal Access Token"
        fi
    fi
fi

# ------------------------------------------------------------- install ------
head_ "Installation"
if [ -x /usr/local/bin/af ]; then
    ok "command 'af' installed (/usr/local/bin/af)"
    [ -f /opt/github-search/arcticfox_gui.py ] && ok "files in /opt/github-search OK" || {
        bad "'af' exists but /opt/github-search is broken → reinstall: sudo bash install.sh"
        PROBLEMS=$((PROBLEMS+1)); }
else
    warn "'af' command not installed (optional)"
    echo "        Install it:   sudo bash install.sh"
    echo "        Or run without installing:   bash run.sh"
fi

CONF="$HOME/.config/github-search/config.json"
if [ -f "$CONF" ]; then
    ok "config found: $CONF"
    if grep -q '"token": *""' "$CONF" 2>/dev/null || ! grep -q 'token' "$CONF" 2>/dev/null; then
        warn "no GitHub token saved — 60 req/h limit; add one in Settings"
    fi
else
    warn "no config yet (created on first Settings save) — that is fine"
fi

# ------------------------------------------------------------- summary ------
printf "\n${B}${CYAN}== Summary ==${R}\n"
if [ "$PROBLEMS" -eq 0 ]; then
    printf " ${GREEN}Everything looks good!${R}\n"
    echo "  Start the app:   af        (if installed)"
    echo "              or:  bash run.sh   (from this folder)"
else
    printf " ${RED}%d problem(s) found — apply the [FIX] lines above.${R}\n" "$PROBLEMS"
fi
printf " ${GREY}Still stuck? Send a screenshot of this whole output.${R}\n\n"
