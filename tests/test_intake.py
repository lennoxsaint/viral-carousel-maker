import json
import os
import subprocess
import sys
from pathlib import Path

from viral_carousel_maker.intake import normalize_intake
from viral_carousel_maker.spec import validate_spec


ROOT = Path(__file__).resolve().parents[1]


def test_text_intake_normalizes_to_valid_seed_spec():
    result = normalize_intake(
        text=(
            "# Your Threads posts do not need more tricks\n\n"
            "Weak posts announce a topic. Strong posts name the problem the reader already feels."
        )
    )

    assert result.source_type == "text"
    assert result.seed_spec["handle"] == "@yourhandle"
    assert result.seed_spec["intake"]["mapping"] == "best-effort"
    assert len(result.seed_spec["slides"]) == 8
    warnings = validate_spec(result.seed_spec)
    assert isinstance(warnings, list)


def test_threadify_json_intake_best_effort_mapping():
    payload = {
        "title": "Your posts are hiding the real problem",
        "profile": {"handle": "@lennox_saint"},
        "slides": [
            {"title": "Start with tension", "body": "Name the problem the reader already feels."},
            {"title": "Cut the tricks", "body": "Make one useful point per slide."},
        ],
        "cta": {"type": "offer", "url": "threadify.app/proof"},
    }
    result = normalize_intake(text=json.dumps(payload), input_format="json")

    assert result.source_type == "json"
    assert result.extracted["format"] == "threadify-json"
    assert result.seed_spec["handle"] == "@lennox_saint"
    assert result.seed_spec["slides"][-1]["cta"]["type"] == "offer"
    assert result.seed_spec["slides"][-1]["cta"]["url"] == "threadify.app/proof"
    validate_spec(result.seed_spec)


def test_intake_cli_writes_seed_yaml(tmp_path):
    out = tmp_path / "seed.yaml"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "viral_carousel_maker.cli",
            "intake",
            "--text",
            "This draft is doing too much. It needs one useful job.",
            "--out",
            str(out),
        ],
        text=True,
        capture_output=True,
        check=False,
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )

    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert "seed_spec" in result.stdout


def test_doctor_codex_does_not_require_api_key():
    result = subprocess.run(
        [sys.executable, "-m", "viral_carousel_maker.cli", "doctor", "--platform", "codex"],
        text=True,
        capture_output=True,
        check=False,
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["api_key_required"] is False
    assert payload["ok"] is True
    assert payload["native_imagegen"] == "host_tool"


def test_doctor_claude_accepts_connected_image_provider():
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT / "src"),
        "VIRAL_CAROUSEL_IMAGEGEN_PROVIDER": "connected-claude-provider",
    }
    env.pop("OPENAI_API_KEY", None)
    result = subprocess.run(
        [sys.executable, "-m", "viral_carousel_maker.cli", "doctor", "--platform", "claude-code"],
        text=True,
        capture_output=True,
        check=False,
        cwd=ROOT,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["api_key_required"] is False
    assert payload["connected_imagegen_provider"] == "connected-claude-provider"
