from pathlib import Path
import json
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_codex_doctor_reports_native_imagegen_without_api_key():
    result = _run_cli("doctor", "--platform", "codex", env_overrides={
        "OPENAI_API_KEY": None,
        "GOOGLE_API_KEY": None,
        "GEMINI_API_KEY": None,
        "GOOGLE_GENERATIVE_AI_API_KEY": None,
    })

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["production_renderer"] == "codex-native-imagegen"
    assert payload["api_key_required"] is False
    assert "ImageGen 2" in payload["message"]


def test_claude_doctor_reports_openai_then_google_readiness():
    result = _run_cli("doctor", "--platform", "claude-code", env_overrides={
        "OPENAI_API_KEY": "set",
        "GOOGLE_API_KEY": "set",
        "CLAUDE_IMAGEGEN_PROVIDER": None,
        "VIRAL_CAROUSEL_IMAGEGEN_PROVIDER": None,
    })

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["openai_api_key_set"] is True
    assert payload["google_image_api_key_set"] is True
    assert payload["provider_order"][1] == "OpenAI Images API via OPENAI_API_KEY"
    assert payload["provider_order"][2] == "Google image API via GOOGLE_API_KEY/GEMINI_API_KEY"


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
