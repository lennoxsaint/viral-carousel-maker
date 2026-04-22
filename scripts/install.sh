#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-python3}"

"$PYTHON_BIN" "$ROOT/scripts/render_skills.py"

mkdir -p "$HOME/.claude/skills" "$HOME/.codex/skills"
rm -rf "$HOME/.claude/skills/viral-carousel-maker" "$HOME/.codex/skills/viral-carousel-maker"
cp -R "$ROOT/skills/dist/claude/viral-carousel-maker" "$HOME/.claude/skills/viral-carousel-maker"
cp -R "$ROOT/skills/dist/codex/viral-carousel-maker" "$HOME/.codex/skills/viral-carousel-maker"

echo "Installed viral-carousel-maker into Claude Code and Codex skill roots."
