from pathlib import Path
import json
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_codex_doctor_reports_native_imagegen_without_api_key():
    result = _run_cli("doctor", "--platform", "codex", env_overrides={
        "GOOGLE_API_KEY": None,
        "GEMINI_API_KEY": None,
        "GOOGLE_GENERATIVE_AI_API_KEY": None,
    })

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["production_renderer"] == "codex-native-imagegen"
    assert payload["api_key_required"] is False
    assert payload["separate_slide_output_required"] is True
    assert payload["contact_sheet_deliverable_allowed"] is False
    assert "ImageGen 2" in payload["message"]
    assert "separate slide PNGs" in payload["message"]


def test_claude_doctor_reports_provider_then_gemini_readiness():
    result = _run_cli("doctor", "--platform", "claude-code", env_overrides={
        "GOOGLE_API_KEY": "set",
        "CLAUDE_IMAGEGEN_PROVIDER": None,
        "VIRAL_CAROUSEL_IMAGEGEN_PROVIDER": None,
    })

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["google_image_api_key_set"] is True
    assert payload["provider_order"] == [
        "connected native image-generation provider",
        "Gemini image API emergency fallback",
    ]
    assert "Gemini emergency fallback" in payload["message"]


def _run_cli(*args, env_overrides=None):
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    for key, value in (env_overrides or {}).items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    return subprocess.run(
        [sys.executable, "-m", "viral_carousel_maker.cli", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
