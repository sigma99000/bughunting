#!/usr/bin/env bash
# install.sh — symlink CBH skills/commands into Claude Code's skill dir,
# and add cbh.py to PATH via ~/.local/bin/cbh shim.

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
SKILLS_DIR="$CLAUDE_HOME/skills"
COMMANDS_DIR="$CLAUDE_HOME/commands"
BIN_DIR="$HOME/.local/bin"

echo "[install] repo:     $REPO"
echo "[install] claude:   $CLAUDE_HOME"
mkdir -p "$SKILLS_DIR" "$COMMANDS_DIR" "$BIN_DIR"

n_skills=0
for d in "$REPO"/skills/*/; do
    name="$(basename "$d")"
    target="$SKILLS_DIR/$name"
    if [ -e "$target" ] || [ -L "$target" ]; then
        rm -rf "$target"
    fi
    ln -s "$d" "$target"
    n_skills=$((n_skills + 1))
done
echo "[install] linked $n_skills skill(s)"

n_cmds=0
for f in "$REPO"/commands/*.md; do
    name="$(basename "$f")"
    target="$COMMANDS_DIR/$name"
    if [ -e "$target" ] || [ -L "$target" ]; then
        rm -f "$target"
    fi
    ln -s "$f" "$target"
    n_cmds=$((n_cmds + 1))
done
echo "[install] linked $n_cmds command(s)"

# cbh shim
shim="$BIN_DIR/cbh"
cat > "$shim" <<EOF
#!/usr/bin/env bash
exec python3 "$REPO/scripts/cbh.py" "\$@"
EOF
chmod +x "$shim"
echo "[install] cbh shim:  $shim"

if ! echo ":$PATH:" | grep -q ":$BIN_DIR:"; then
    echo "[install] NOTE: $BIN_DIR is not on PATH — add this to your shell rc:"
    echo "  export PATH=\"$BIN_DIR:\$PATH\""
fi

echo "[install] done. Restart Claude Code to pick up the new skills/commands."
