#!/bin/sh
# =============================================================================
#   GITHUB SEARCH v2.0 — remote one-liner installer (Kali Linux)
#
#   curl -sSL <raw-url-to-this-file> | sudo bash
#
#   NOTE: this only works AFTER the project has been uploaded to GitHub.
#   If you just downloaded the ZIP locally, skip this file and run:
#       sudo bash install.sh
# =============================================================================
set -eu

REPO="arcticfox-cyber/GitHub-Search"
BRANCH="main"

command -v curl >/dev/null 2>&1 || { echo "[x] curl is required: sudo apt install curl"; exit 1; }
command -v tar  >/dev/null 2>&1 || { echo "[x] tar is required"; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "[*] Downloading GitHub Search v2.0 ..."
if ! curl -fsSL -o "$TMP/repo.tar.gz" "https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz"; then
    echo ""
    echo "[x] Could not download ${REPO} (HTTP error)."
    echo "    Reasons:"
    echo "      - the project is not on GitHub under that name yet, or"
    echo "      - you are offline / behind a proxy."
    echo ""
    echo "    Easiest fix (no GitHub needed):"
    echo "      1. extract the ZIP you already have"
    echo "      2. open that folder in a terminal"
    echo "      3. run:  sudo bash install.sh"
    exit 1
fi

tar xzf "$TMP/repo.tar.gz" -C "$TMP"

ROOT_DIR="$(find "$TMP" -maxdepth 1 -type d \( -name 'GitHub-Search-*'  \) | head -n1)"
[ -n "$ROOT_DIR" ] || { echo "[x] download failed (unexpected archive layout)"; exit 1; }

DIR="$ROOT_DIR/GitHub-Search-v2"
[ -f "$DIR/install.sh" ] || {
    echo "[x] installer not found in expected project folder: $DIR"
    exit 1
}

echo "[*] Starting installer ..."
bash "$DIR/install.sh" "$@"
