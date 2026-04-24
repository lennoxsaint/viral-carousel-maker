from pathlib import Path
import json
import os
import subprocess
import sys

import yaml

from viral_carousel_maker.interview import evaluate_interview, next_question_batch


ROOT = Path(__file__).resolve().parents[1]


def complete_answers(**overrides):
    answers = {
        "handle": "@tester",
        "niche": "AI creator education",
        "sub_niche": "practical AI content systems",
        "target_viewer": "solo creators selling digital products with inconsistent content systems",
        "viewer_pain": "they keep starting from a blank page and missing posting days",
        "viewer_desire": "they want a repeatable system for useful content ideas",
        "belief_shift": "stop treating AI as a writer and start treating it as a content operating system",
        "topic": "a five layer prompt stack for repeatable creator content",
        "why_now": "AI tools are common now but creator workflows are still messy",
        "proof": "personal workflow experience from building repeatable prompt systems",
        "proof_strength": "lived experience",
        "carousel_job": "saves",
        "cta_type": "follow",
        "cta_pressure": "soft",
        "body_slide_count": 5,
        "tone": "direct and practical",
        "visual_taste": "clean field notes with high contrast paper texture",
        "visual_avoid": "busy gradients and tiny text",
        "brand_colors": "#05063f and #e84b05",
        "risk_appetite": 7,
        "enemy_belief": "the false belief that better prompts are just clever wording",
        "personal_stakes": "I wasted time making one off drafts before building a reusable system",
        "claims_to_avoid": "do not promise instant growth or invented performance stats",
        "saveable_reason": "the framework gives them a checklist they can reuse later",
        "shareable_reason": "it names a common workflow mistake their creator friends recognize",
        "distrust_reason": "fake certainty, hype language, or unsupported growth claims",
        "constraints": "vertical Threads carousel with code rendered text and no publishing automation",
    }
    answers.update(overrides)
    return answers


def test_first_question_batch_is_focused():
    questions = next_question_batch({})

    assert 3 <= len(questions) <= 5
    assert questions[0]["field"] == "handle"
    assert questions[-1]["field"] == "viewer_pain"


def test_saved_profile_prefills_stable_fields_but_not_current_questions():
    profile = {
        "handle": "@saved",
        "niche": "creator education",
        "sub_niche": "AI workflows",
        "audience": "solo creators",
        "audience_pains": ["blank page anxiety"],
        "tone": {"primary": "direct"},
        "visual_preferences": {"styles": ["clean"]},
        "preferred_body_slide_count": 5,
    }

    report = evaluate_interview({}, profile=profile)
    missing_fields = {item["field"] for item in report["missing"]}

    assert report["sources"]["handle"] == "profile"
    assert "target_viewer" in missing_fields
    assert "viewer_pain" in missing_fields
    assert not report["ready_to_draft"]


def test_vague_answers_trigger_follow_up_questions():
    report = evaluate_interview(
        complete_answers(
            target_viewer="creators",
            viewer_pain="growth",
        )
    )
    weak_fields = {item["field"] for item in report["weak"]}

    assert "target_viewer" in weak_fields
    assert "viewer_pain" in weak_fields
    assert not report["ready_to_draft"]


def test_offer_cta_requires_url_and_promise():
    report = evaluate_interview(
        complete_answers(
            cta_type="offer",
            offer_url="",
            offer_promise="",
        )
    )
    missing_fields = {item["field"] for item in report["missing"]}

    assert "offer_url" in missing_fields
    assert "offer_promise" in missing_fields
    assert not report["ready_to_draft"]


def test_interview_validate_require_ready_fails_and_passes(tmp_path):
    incomplete_path = tmp_path / "incomplete.yaml"
    complete_path = tmp_path / "complete.yaml"
    incomplete_path.write_text(yaml.safe_dump({"handle": "@tester"}), encoding="utf-8")
    complete_path.write_text(yaml.safe_dump(complete_answers()), encoding="utf-8")

    incomplete = _run_cli(
        "interview",
        "validate",
        "--answers",
        str(incomplete_path),
        "--require-ready",
    )
    complete = _run_cli(
        "interview",
        "validate",
        "--answers",
        str(complete_path),
        "--require-ready",
    )

    assert incomplete.returncode == 1
    assert complete.returncode == 0
    assert json.loads(complete.stdout)["ready_to_draft"] is True


def test_render_require_interview_blocks_incomplete_answers(tmp_path):
    answers_path = tmp_path / "answers.yaml"
    answers_path.write_text(yaml.safe_dump({"handle": "@tester"}), encoding="utf-8")

    result = _run_cli(
        "render",
        "examples/specs/ai-framework.yaml",
        "--out-dir",
        str(tmp_path / "pack"),
        "--dry-run",
        "--require-interview",
        "--interview-answers",
        str(answers_path),
    )

    assert result.returncode == 1
    assert json.loads(result.stdout)["ready_to_draft"] is False


def test_render_updates_profile_with_interview_fields_after_successful_qa(tmp_path):
    answers_path = tmp_path / "answers.yaml"
    profile_path = tmp_path / "profile.yaml"
    answers_path.write_text(
        yaml.safe_dump({**complete_answers(), "api_key": "sk-nope"}),
        encoding="utf-8",
    )

    result = _run_cli(
        "render",
        "examples/specs/ai-framework.yaml",
        "--out-dir",
        str(tmp_path / "pack"),
        "--renderer",
        "pillow",
        "--require-interview",
        "--interview-answers",
        str(answers_path),
        "--update-profile",
        "--profile-path",
        str(profile_path),
    )

    assert result.returncode == 0, result.stderr
    profile_text = profile_path.read_text(encoding="utf-8")
    assert "solo creators selling digital products" in profile_text
    assert "blank page" in profile_text
    assert "soft" in profile_text
    assert "sk-nope" not in profile_text


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "viral_carousel_maker.cli", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )
