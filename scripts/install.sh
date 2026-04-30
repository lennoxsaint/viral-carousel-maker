#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-python3}"

"$PYTHON_BIN" "$ROOT/scripts/render_skills.py"

mkdir -p "$HOME/.claude/skills" "$HOME/.codex/skills"
rm -rf "$HOME/.claude/skills/viral-carousel-maker" "$HOME/.codex/skills/viral-carousel-maker"
cp -R "$ROOT/skills/dist/claude/viral-carousel-maker" "$HOME/.claude/skills/viral-carousel-maker"
cp -R "$ROOT/skills/dist/codex/viral-carousel-maker" "$HOME/.codex/skills/viral-carousel-maker"

grep -q "ChatGPT ImageGen 2" "$HOME/.codex/skills/viral-carousel-maker/SKILL.md"
grep -q "first-use style calibration" "$HOME/.codex/skills/viral-carousel-maker/SKILL.md"
grep -q "GOOGLE_API_KEY" "$HOME/.claude/skills/viral-carousel-maker/SKILL.md"
test -f "$HOME/.codex/skills/viral-carousel-maker/references/style-calibration.md"
test -f "$HOME/.claude/skills/viral-carousel-maker/references/style-calibration.md"

echo "Installed viral-carousel-maker into Claude Code and Codex skill roots."
echo "Verified ImageGen-first policy, first-use style calibration, and Claude OpenAI/Google fallback docs."
