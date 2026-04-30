from pathlib import Path
import os
import subprocess
import sys

from viral_carousel_maker.profile import merge_profile, strip_profile_secrets, update_profile_from_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_profile_merge_allowlist_and_secret_stripping():
    merged = merge_profile(
        {"handle": "@old", "visual_preferences": ["clean"]},
        {
            "handle": "@new",
            "niche": "creator education",
            "visual_preferences": ["clean", "high contrast"],
            "style_canon": {"name": "Lennox/Fwed Blackboard"},
            "imagegen_policy": {"production_renderer": "codex-native-imagegen"},
            "OPENAI_API_KEY": "sk-test",
            "nested": {"secret_token": "hidden"},
        },
        source="test",
        now="2026-04-24T00:00:00+00:00",
    )

    assert merged["handle"] == "@new"
    assert merged["niche"] == "creator education"
    assert merged["visual_preferences"] == ["clean", "high contrast"]
    assert merged["style_canon"]["name"] == "Lennox/Fwed Blackboard"
    assert merged["imagegen_policy"]["production_renderer"] == "codex-native-imagegen"
    assert "OPENAI_API_KEY" not in merged
    assert "nested" not in merged
    assert merged["provenance"]["sources"] == ["test"]
    assert merged["provenance"]["last_updated_at"] == "2026-04-24T00:00:00+00:00"


def test_profile_snapshot_secret_stripping():
    clean = strip_profile_secrets(
        {
            "handle": "@tester",
            "api_key": "sk-nope",
            "nested": {"secret_token": "hidden", "tone": "direct"},
        }
    )

    assert clean == {"handle": "@tester", "nested": {"tone": "direct"}}


def test_update_profile_from_manifest_writes_merged_profile(tmp_path):
    profile_path = tmp_path / "profile.yaml"
    manifest = {
        "handle": "@tester",
        "profile_snapshot": {
            "niche": "AI education",
            "tone": "direct",
            "api_key": "sk-nope",
        },
        "strategy": {
            "hook_archetype": "enemy_belief",
            "visual_thesis": "Dark proof board with one loud object.",
        },
        "design": {"design_pack": "brutal-proof"},
        "slides": [
            {"role": "hook", "title": "Your hooks are too polite"},
            {"role": "body", "title": "One"},
            {"role": "body", "title": "Two"},
            {"role": "body", "title": "Three"},
            {"role": "recap", "title": "TL;DR"},
            {"role": "cta", "title": "Follow", "cta": {"type": "follow"}},
        ],
    }

    update_profile_from_manifest(manifest, path=profile_path, source="successful-render")
    text = profile_path.read_text(encoding="utf-8")

    assert "AI education" in text
    assert "sk-nope" not in text
    assert "brutal-proof" in text
    assert "successful-render" in text


def test_cli_render_updates_profile_after_successful_qa(tmp_path):
    profile_path = tmp_path / "profile.yaml"
    out_dir = tmp_path / "pack"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "viral_carousel_maker.cli",
            "render",
            "examples/specs/ai-framework.yaml",
            "--out-dir",
            str(out_dir),
            "--renderer",
            "pillow",
            "--update-profile",
            "--profile-path",
            str(profile_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )

    assert result.returncode == 0, result.stderr
    assert profile_path.exists()
    assert "successful-render" in profile_path.read_text(encoding="utf-8")
