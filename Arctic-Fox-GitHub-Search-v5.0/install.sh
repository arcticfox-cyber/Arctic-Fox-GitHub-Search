#!/usr/bin/env bash
# =============================================================================
#   ARCTIC FOX  ·  GitHub Search v5.0 (GUI Edition)
#   One-command installer for Kali Linux
#
#   Install:      sudo bash install.sh
#   Uninstall:    sudo bash install.sh --uninstall
#   Other Debian: sudo bash install.sh --force
# =============================================================================
set -u

# re-exec under bash when launched with sh/dash
if [ -z "${BASH_VERSION:-}" ]; then
    exec bash "$0" "$@"
fi

APP="arctic-fox"
APP_TITLE="Arctic Fox"
VERSION="5.0.3"
OPT_DIR="/opt/arctic-fox"
BIN_AF="/usr/local/bin/af"
BIN_FULL="/usr/local/bin/arcticfox"
DESKTOP_FILE="/usr/share/applications/arcticfox.desktop"
ICON_FILE="/usr/share/pixmaps/arcticfox.png"

# ------------------------------------------------------------------ output --
if [ -t 1 ]; then
    ICE="\033[38;5;159m"; CYAN="\033[38;5;51m"; BLUE="\033[38;5;39m"
    GREEN="\033[38;5;114m"; RED="\033[38;5;203m"; YELL="\033[38;5;221m"
    GREY="\033[38;5;245m"; WHITE="\033[97m"; B="\033[1m"; R="\033[0m"
else
    ICE=""; CYAN=""; BLUE=""; GREEN=""; RED=""; YELL=""; GREY=""; WHITE=""; B=""; R=""
fi

ok()   { printf "  ${GREEN}[+]${R} %s\n" "$1"; }
warn() { printf "  ${YELL}[!]${R} %s\n" "$1"; }
die()  { printf "  ${RED}[x]${R} %s\n" "$1" >&2; exit 1; }
step() { printf "\n${B}${ICE} ==> %s${R}\n" "$1"; }

banner() {
    printf "${B}${CYAN}"
    printf "  ▄▀█ █▀█ █▀▀ ▀█▀ █ █▀▀   █▀▀ █▀█ █ █  \n"
    printf "  █▀█ █▀▄ █▄▄  █  █ █▄▄   █▀▀ █▄█ ▄▀▄  \n"
    printf "${GREY}  GitHub Account & Repository Inspector  ·  v%s  ·  Kali Linux installer${R}\n" "$VERSION"
    printf "\n"
}

# ------------------------------------------------- environment sanity check --
if [ -n "${PREFIX:-}" ] && case "${PREFIX}" in *com.termux*) true ;; *) false ;; esac; then
    die "Termux / NetHunter-rootless detected — no desktop GUI here.\n        Use the terminal edition instead:   python3 arcticfox-cli.py"
fi

# ------------------------------------------------------------------ args ---
DO_UNINSTALL=0; FORCE=0
for a in "$@"; do
    case "$a" in
        --uninstall) DO_UNINSTALL=1 ;;
        --force)     FORCE=1 ;;
        -h|--help)   sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) warn "ignored option: $a" ;;
    esac
done

clear 2>/dev/null || true
banner

# --------------------------------------------------------------- uninstall --
if [ "$DO_UNINSTALL" -eq 1 ]; then
    step "Uninstalling $APP_TITLE"
    [ "$(id -u)" -eq 0 ] || die "Run with sudo: sudo bash install.sh --uninstall"
    rm -f "$BIN_AF" "$BIN_FULL"                  && ok "removed af / arcticfox commands"
    rm -f "$DESKTOP_FILE"                        && ok "removed menu launcher"
    rm -f "$ICON_FILE"                           && ok "removed icon"
    rm -rf "$OPT_DIR"                            && ok "removed $OPT_DIR"
    printf "\n  ${GREY}Config (~/.config/arctic-fox) and reports (~/arctic-fox-reports) were kept.${R}\n"
    printf "  ${GREY}Bye. Stay frosty.${R}\n\n"
    exit 0
fi

# -------------------------------------------------------------- root / kali --
step "Checking privileges"
if [ "$(id -u)" -eq 0 ]; then
    ok "running as root"
elif command -v sudo >/dev/null 2>&1; then
    ok "using sudo"
    SUDO="sudo"
else
    die "root privileges required (try: sudo bash install.sh)"
fi
SUDO="${SUDO:-}"

step "Checking operating system"
KALI=0
if [ -r /etc/os-release ]; then
    . /etc/os-release
    case "${ID:-}${ID_LIKE:-}" in
        *kali*) KALI=1 ;;
    esac
fi
if [ "$KALI" -eq 1 ]; then
    ok "Kali Linux detected  (${PRETTY_NAME:-})"
else
    if [ "$FORCE" -eq 1 ]; then
        warn "not Kali (${PRETTY_NAME:-unknown}) — continuing (--force)"
    else
        die "this installer is built for Kali Linux only (re-run with --force to override)"
    fi
fi

# ---------------------------------------------------------------- packages --
step "Installing required packages (python3, python3-tk, git, xdg-utils)"
export DEBIAN_FRONTEND=noninteractive
if ! command -v python3 >/dev/null 2>&1 || ! python3 -c "import tkinter" 2>/dev/null; then
    if ! $SUDO apt-get update -y; then
        die "apt-get update failed.\n        Check internet. Kali mirror busy? Try again or run: sudo apt update\n        Behind a proxy/VPN? Disable it and retry."
    fi
    if ! $SUDO apt-get install -y python3 python3-tk git xdg-utils; then
        die "apt-get install failed.\n        Try manually:  sudo apt install -y python3 python3-tk git xdg-utils"
    fi
    ok "packages installed"
else
    ok "python3 + tkinter already present"
fi
command -v git >/dev/null 2>&1      || $SUDO apt-get install -y git        >/dev/null 2>&1 || true
command -v xdg-open >/dev/null 2>&1 || $SUDO apt-get install -y xdg-utils   >/dev/null 2>&1 || true
ok "git: $(git --version 2>/dev/null | awk '{print $3}' || echo 'missing')"

# ------------------------------------------------------------------- files --
step "Installing $APP_TITLE to $OPT_DIR"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
for f in arcticfox_core.py arcticfox_gui.py arcticfox-cli.py; do
    [ -f "$SRC/$f" ] || die "missing file: $SRC/$f (run this script from the project folder)"
done
$SUDO mkdir -p "$OPT_DIR/assets"
$SUDO install -m 644 "$SRC/arcticfox_core.py" "$OPT_DIR/"
$SUDO install -m 644 "$SRC/arcticfox_gui.py"  "$OPT_DIR/"
$SUDO install -m 755 "$SRC/arcticfox-cli.py"  "$OPT_DIR/"
# Install every runtime image asset. The GIF is required for the 3-second startup splash.
for asset in arcticfox-icon.png moonlit-fox-splash.gif moonlit-fox-splash.png; do
    if [ -f "$SRC/assets/$asset" ]; then
        $SUDO install -m 644 "$SRC/assets/$asset" "$OPT_DIR/assets/"
    elif [ "$asset" = "moonlit-fox-splash.gif" ]; then
        warn "missing $asset — startup splash artwork will not be available"
    fi
done
ok "application files and available assets installed"

# ----------------------------------------------------------------- commands --
step "Creating the 'af' command"
$SUDO tee "$BIN_AF" >/dev/null <<'EOF'
#!/bin/sh
# Arctic Fox v5.0.3 — launcher (GUI with automatic checks)
if ! command -v python3 >/dev/null 2>&1; then
    echo "[x] python3 missing — fix: sudo apt install -y python3 python3-tk"
    exit 1
fi
if [ "${1:-}" = "--cli" ]; then
    shift
    exec python3 /opt/arctic-fox/arcticfox-cli.py "$@"
fi
if [ "${1:-}" != "--cli" ]; then
    if ! python3 -c "import tkinter" 2>/dev/null; then
        echo "[x] tkinter missing — GUI cannot start."
        echo "    Fix: sudo apt install -y python3-tk"
        echo "    Terminal mode instead:  af --cli"
        exit 1
    fi
    if [ -z "${DISPLAY:-}" ]; then
        echo "[x] no display detected (SSH / headless?)."
        echo "    Run on the Kali desktop, or use terminal mode:  af --cli"
        exit 1
    fi
fi
exec python3 /opt/arctic-fox/arcticfox_gui.py "$@"
EOF
$SUDO chmod 755 "$BIN_AF"
$SUDO ln -sf "$BIN_AF" "$BIN_FULL"
ok "created: af   (same as: arcticfox)"

# ------------------------------------------------------------------ desktop --
step "Creating Applications menu entry"
$SUDO tee "$DESKTOP_FILE" >/dev/null <<'EOF'
[Desktop Entry]
Type=Application
Version=1.0
Name=Arctic Fox
GenericName=GitHub Inspector
Comment=GitHub Account & Repository Inspector — Arctic Fox v5.0.3
Exec=/usr/local/bin/af
Icon=arcticfox
Terminal=false
Categories=Network;Utility;
Keywords=github;osint;recon;arcticfox;search;
StartupNotify=true
EOF
if [ -f "$SRC/assets/arcticfox-icon.png" ]; then
    $SUDO install -m 644 "$SRC/assets/arcticfox-icon.png" "$ICON_FILE"
fi
ok "menu: Applications → Internet → Arctic Fox"

# ------------------------------------------------------------------ verify --
step "Verifying installation"
if python3 -c "import tkinter" 2>/dev/null; then
    ok "tkinter OK"
else
    die "tkinter still missing — run: sudo apt install python3-tk"
fi
[ -x "$BIN_AF" ] && ok "command ready: af"

cat <<EOF

  ${B}${ICE}─────────────────────────────────────────────────────${R}
   ${B}${WHITE}$APP_TITLE $VERSION installed!${R}

     ${CYAN}af${R}              start the GUI
     ${CYAN}af octocat${R}      search a username directly
     ${CYAN}af --cli${R}        old-school terminal mode
     ${CYAN}af --help${R}       help
  ${B}${ICE}─────────────────────────────────────────────────────${R}

  ${GREY}Tips: add a GitHub token in Settings (higher rate limits).${R}
  ${GREY}Reports are saved to ~/arctic-fox-reports${R}

EOF
printf "  ${B}${GREEN}Run it now:  af${R}\n\n"
