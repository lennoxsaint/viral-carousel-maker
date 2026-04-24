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
    assert "Mandatory Interrogation Gate" in claude_text
    assert "request_user_input" in claude_text
    assert "interview validate" in claude_text
    assert "--require-interview" in claude_text
    assert "profile.yaml" in claude_text
    assert "per-slide quality gate" in claude_text
    assert "Virality Engine" in claude_text
    assert "Hook Lab" in claude_text
    assert "AI critic gate" in claude_text
    assert "browser renderer" in claude_text
    assert "visual_priority" in claude_text
    assert "visual_qa.json" in claude_text
    assert "contact_sheet.png" in claude_text
    assert "Threadify draft" in claude_text
    assert "Safe fallback message" in claude_text
    assert "Mandatory Interrogation Gate" in codex_text
    assert "request_user_input" in codex_text
    assert "interview validate" in codex_text
    assert "--require-interview" in codex_text
    assert "profile.yaml" in codex_text
    assert "Virality Engine" in codex_text
    assert "AI critic gate" in codex_text
    assert "browser renderer" in codex_text
    assert "visual_priority" in codex_text
    assert "OPENAI_API_KEY" not in codex_text.split("## Platform Adapter", 1)[1].split("<!-- END GENERATED", 1)[0] or "do not require `OPENAI_API_KEY`" in codex_text


def test_skill_reference_docs_include_interview_profile_and_quality_gates():
    source_root = ROOT / "skills" / "source" / "viral-carousel-maker" / "references"
    interview = (source_root / "interview.md").read_text(encoding="utf-8")
    profile = (source_root / "profile-memory.md").read_text(encoding="utf-8")
    quality = (source_root / "quality-rubric.md").read_text(encoding="utf-8")
    constitution = (source_root / "threads-virality-constitution.md").read_text(encoding="utf-8")
    hooks = (source_root / "hook-lab.md").read_text(encoding="utf-8")
    performance = (source_root / "performance-loop.md").read_text(encoding="utf-8")
    critic = (source_root / "ai-critic-gate.md").read_text(encoding="utf-8")
    pattern_bank = (source_root / "pattern-bank.md").read_text(encoding="utf-8")
    intake = (source_root / "threadify-draft-intake.md").read_text(encoding="utf-8")

    assert "This gate is mandatory before carousel generation." in interview
    assert "Two-stage interrogation flow" in interview
    assert "Ready to generate" in interview
    assert "viral-carousel interview next" in interview
    assert "ready_to_draft: true" in interview
    assert "Use `request_user_input` whenever the host provides it." in interview
    assert "Do not summarize, draft, plan, select a template, generate images, or render" in interview
    assert "~/.viral-carousel-maker/profile.yaml" in profile
    assert "Never store" in profile
    assert "provenance" in profile
    assert "Threadify-style JSON" in intake
    assert "best-effort" in intake
    assert "Quality gates are mandatory" in quality
    assert "Per-slide finished image quality" in quality
    assert "visual-area threshold" in quality
    assert "No how-to hooks by default" in constitution
    assert "Generate at least 5 hook candidates" in hooks
    assert "viral-carousel metrics add" in performance
    assert "The AI critic gate is required" in critic
    assert "viral-carousel critic validate" in critic
    assert "viral-carousel corpus import" in pattern_bank
    assert "raw posts" in pattern_bank
