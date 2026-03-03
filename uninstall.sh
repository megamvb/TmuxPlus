#!/usr/bin/env bash
# TmuxPlus — Uninstallation script
# Usage: bash uninstall.sh

set -euo pipefail

INSTALL_DIR="$HOME/.TmuxPlus"
CONFIG_DIR="$HOME/.config/tmuxplus"

info()  { printf '\033[1;34m::\033[0m %s\n' "$*"; }
ok()    { printf '\033[1;32m✔\033[0m  %s\n' "$*"; }
warn()  { printf '\033[1;33m⚠\033[0m  %s\n' "$*"; }

# ── Confirm uninstallation ───────────────────────────

echo ""
info "This script will remove TmuxPlus from your system."
echo ""
read -rp "Do you want to continue? [y/N] " answer
case "$answer" in
    [yY]|[yY][eE][sS]) ;;
    *) info "Uninstallation cancelled."; exit 0 ;;
esac

# ── Remove shell alias ──────────────────────────────

remove_alias() {
    local rc_file="$1"
    if [ -f "$rc_file" ] && grep -qF 'tmux-plus' "$rc_file" 2>/dev/null; then
        sed -i '/^# TmuxPlus$/d' "$rc_file"
        sed -i '/alias tmux-plus=/d' "$rc_file"
        ok "Alias removed from $(basename "$rc_file")"
    fi
}

[ -f "$HOME/.bashrc" ] && remove_alias "$HOME/.bashrc"
[ -f "$HOME/.zshrc" ]  && remove_alias "$HOME/.zshrc"

# ── Remove installation directory ────────────────────

if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    ok "Directory $INSTALL_DIR removed"
else
    warn "Directory $INSTALL_DIR not found (already removed?)"
fi

# ── Remove configuration ────────────────────────────

if [ -d "$CONFIG_DIR" ]; then
    read -rp "Remove saved configurations and sessions from $CONFIG_DIR? [y/N] " answer
    case "$answer" in
        [yY]|[yY][eE][sS])
            rm -rf "$CONFIG_DIR"
            ok "Configuration removed"
            ;;
        *)
            warn "Configuration kept at $CONFIG_DIR"
            ;;
    esac
fi

# ── Done ─────────────────────────────────────────────

echo ""
ok "TmuxPlus uninstalled successfully!"
info "Open a new terminal to apply the shell changes."
echo ""
