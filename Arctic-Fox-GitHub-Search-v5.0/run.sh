#!/usr/bin/env bash
# =============================================================================
#   ARCTIC FOX v5.0 — Quick Launcher (no installation needed)
#
#   bash run.sh                 start the GUI
#   bash run.sh octocat         start GUI and search a username
#   bash run.sh --cli           terminal mode (works everywhere)
#
#   Checks python3, tkinter and your display, and offers to FIX
#   the missing pieces automatically. Works on Kali and any Debian.
# =============================================================================
set -u

GREEN='\033[38;5;114m'; RED='\033[38;5;203m'; YELL='\033[38;5;221m'
CYAN='\033[38;5;51m';   B='\033[1m'; R='\033[0m'
ok()   { printf " ${GREEN}[+]${R} %s\n" "$1"; }
bad()  { printf " ${RED}[x]${R} %s\n" "$1"; }
warn() { printf " ${YELL}[!]${R} %s\n" "$1"; }

printf "%b\n" " ${B}${CYAN}ARCTIC FOX v5.0.3 — quick launcher${R}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
cd "$HERE"

# Help/version work from any current directory after resolving the script path.
case "${1:-}" in
    -h|--help|-v|--version)
        command -v python3 >/dev/null 2>&1 || { bad "python3 is not installed"; exit 1; }
        exec python3 "$HERE/arcticfox_gui.py" "$1"
        ;;
esac


# --- 0. right folder? -------------------------------------------------------
for f in arcticfox_gui.py arcticfox_core.py; do
    [ -f "$HERE/$f" ] || {
        bad "missing $f — run this script from the extracted Arctic-Fox folder"
        exit 1
    }
done

# --- 1. python3? ------------------------------------------------------------
PY=""
if command -v python3 >/dev/null 2>&1; then
    PY=python3
    ok "python3: $($PY --version 2>&1)"
else
    bad "python3 is not installed"
    if command -v sudo >/dev/null 2>&1; then
        printf "     Install it now? [Y/n] "
        read -r ans
        case "$ans" in n*|N*) exit 1 ;; esac
        sudo apt-get update -y      && sudo apt-get install -y python3 python3-tk
        command -v python3 >/dev/null 2>&1 || { bad "still no python3 — install it manually"; exit 1; }
        PY=python3
    else
        exit 1
    fi
fi

# CLI mode must not depend on Tkinter or an X display.
if [ "${1:-}" = "--cli" ]; then
    shift
    exec "$PY" "$HERE/arcticfox-cli.py" "$@"
fi

# --- 2. tkinter? (needed for the GUI only) ----------------------------------
GUI_OK=1
if ! $PY -c "import tkinter" 2>/dev/null; then
    GUI_OK=0
    if [ "${1:-}" = "--cli" ]; then
        warn "tkinter missing — but --cli does not need it"
    else
        bad "tkinter (python3-tk) is missing — the GUI cannot start without it"
        if command -v sudo >/dev/null 2>&1; then
            printf "     Install python3-tk now? [Y/n] "
            read -r ans
            case "$ans" in n*|N*) printf "     Falling back to terminal mode.\n"; exec "$PY" "$HERE/arcticfox-cli.py" "$@" ;; esac
            if sudo apt-get install -y python3-tk; then
                GUI_OK=1; ok "python3-tk installed"
            fi
        fi
        [ "$GUI_OK" -eq 1 ] || exec $PY arcticfox-cli.py "$@"
    fi
else
    ok "tkinter OK"
fi

# --- 3. display? ------------------------------------------------------------
if [ "$GUI_OK" -eq 1 ] && [ "${1:-}" != "--cli" ]; then
    if [ -z "${DISPLAY:-}" ]; then
        warn "no display detected (SSH / headless / Termux?)"
        printf "     GUI needs a desktop. Start terminal mode instead? [Y/n] "
        read -r ans
        case "$ans" in n*|N*) exit 1 ;; esac
        exec "$PY" arcticfox-cli.py "${@:2}"
    fi
    ok "display: ${DISPLAY}"
fi

# --- 4. launch ---------------------------------------------------------------
exec "$PY" "$HERE/arcticfox_gui.py" "$@"
