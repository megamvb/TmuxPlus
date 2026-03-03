#!/usr/bin/env bash
# TmuxPlus — Installation script
# Usage: curl -fsSL <url>/install.sh | bash
#   or:  bash install.sh

set -euo pipefail

REPO_URL="https://github.com/megamvb/TmuxPlus.git"
INSTALL_DIR="$HOME/.TmuxPlus"
ALIAS_CMD='alias tmux-plus="python3 $HOME/.TmuxPlus/main.py"'

info()  { printf '\033[1;34m::\033[0m %s\n' "$*"; }
ok()    { printf '\033[1;32m✔\033[0m  %s\n' "$*"; }
err()   { printf '\033[1;31m✘\033[0m  %s\n' "$*" >&2; exit 1; }

# ── Check dependencies ───────────────────────────────

for cmd in git python3 pip3 tmux; do
    command -v "$cmd" >/dev/null 2>&1 || err "'$cmd' not found. Please install it before continuing."
done

# ── Clone or update repository ───────────────────────

if [ -d "$INSTALL_DIR" ]; then
    info "Directory $INSTALL_DIR already exists, updating..."
    git -C "$INSTALL_DIR" pull --ff-only || err "Failed to update repository."
    ok "Repository updated"
else
    info "Cloning TmuxPlus into $INSTALL_DIR..."
    git clone "$REPO_URL" "$INSTALL_DIR" || err "Failed to clone repository."
    ok "Repository cloned"
fi

# ── Install Python dependencies ──────────────────────

info "Installing Python dependencies..."
pip3 install --user -q -r "$INSTALL_DIR/requirements.txt"
ok "Dependencies installed"

# ── Configure shell alias ────────────────────────────

add_alias() {
    local rc_file="$1"
    if [ -f "$rc_file" ] && grep -qF 'tmux-plus' "$rc_file" 2>/dev/null; then
        ok "Alias already exists in $(basename "$rc_file")"
        return
    fi
    printf '\n# TmuxPlus\n%s\n' "$ALIAS_CMD" >> "$rc_file"
    ok "Alias added to $(basename "$rc_file")"
}

shell_name="$(basename "${SHELL:-/bin/bash}")"

case "$shell_name" in
    zsh)  add_alias "$HOME/.zshrc" ;;
    bash) add_alias "$HOME/.bashrc" ;;
    *)
        # Try both if the shell is not recognized
        [ -f "$HOME/.bashrc" ] && add_alias "$HOME/.bashrc"
        [ -f "$HOME/.zshrc" ]  && add_alias "$HOME/.zshrc"
        ;;
esac

# ── Done ─────────────────────────────────────────────

echo ""
ok "TmuxPlus installed successfully!"
info "Run 'source ~/.${shell_name}rc' or open a new terminal, then run:"
echo ""
echo "    tmux-plus"
echo ""
