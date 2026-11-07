#!/bin/sh
# =============================================================================
#   GITHUB SEARCH v3.0 — remote installer (Kali Linux)
#
#   Review this script before running it:
#   curl -fsSL https://raw.githubusercontent.com/arcticfox-cyber/GitHub-Search/main/GitHub-Search-v3/remote-install.sh -o remote-install.sh
#   less remote-install.sh
#   sudo bash remote-install.sh
# =============================================================================
set -eu

REPO="arcticfox-cyber/GitHub-Search"
BRANCH="main"
APP_DIR="GitHub-Search-v3"

command -v curl >/dev/null 2>&1 || { echo "[x] curl is required: sudo apt install curl"; exit 1; }
command -v tar >/dev/null 2>&1 || { echo "[x] tar is required"; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT HUP INT TERM

echo "[*] Downloading GitHub Search v3.0 ..."
if ! curl -fsSL -o "$TMP/repo.tar.gz" "https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz"; then
    echo "[x] Could not download ${REPO}."
    echo "    Check the repository URL, internet connection, or proxy."
    exit 1
fi

tar xzf "$TMP/repo.tar.gz" -C "$TMP"
ROOT_DIR="$(find "$TMP" -mindepth 1 -maxdepth 1 -type d -name 'GitHub-Search-*' -print -quit)"
[ -n "$ROOT_DIR" ] || { echo "[x] Unexpected archive layout."; exit 1; }

DIR="$ROOT_DIR/$APP_DIR"
[ -f "$DIR/install.sh" ] || {
    echo "[x] Installer not found: $DIR/install.sh"
    echo "    The repository layout may have changed."
    exit 1
}

echo "[*] Starting GitHub Search v3.0 installer ..."
exec bash "$DIR/install.sh" "$@"
