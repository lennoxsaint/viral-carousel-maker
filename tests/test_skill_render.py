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
    assert (ROOT / "skills" / "dist" / "claude" / "viral-carousel-maker" / "SKILL.md").exists()
    assert (ROOT / "skills" / "dist" / "codex" / "viral-carousel-maker" / "SKILL.md").exists()

