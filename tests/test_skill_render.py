from pathlib import Path

import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_skill_render_script_creates_dist():
    result = subprocess.run(
        [sys.executable, "scripts/render_skills.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    claude_skill = ROOT / "skills" / "dist" / "claude" / "viral-carousel-maker" / "SKILL.md"
    codex_skill = ROOT / "skills" / "dist" / "codex" / "viral-carousel-maker" / "SKILL.md"
    assert claude_skill.exists()
    assert codex_skill.exists()
    assert (
        ROOT
        / "skills"
        / "dist"
        / "claude"
        / "viral-carousel-maker"
        / "references"
        / "claude-openai-api-key-setup.md"
    ).exists()

    claude_text = claude_skill.read_text(encoding="utf-8")
    codex_text = codex_skill.read_text(encoding="utf-8")
    assert "require `OPENAI_API_KEY`" in claude_text
    assert "https://platform.openai.com/api-keys" in claude_text
    assert "do not require `OPENAI_API_KEY`" in codex_text
