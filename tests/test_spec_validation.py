from pathlib import Path

import pytest

from viral_carousel_maker.spec import SpecError, load_spec, validate_spec


ROOT = Path(__file__).resolve().parents[1]


def test_sample_spec_validates():
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    warnings = validate_spec(spec)
    assert isinstance(warnings, list)


def test_threadify_intake_seed_spec_validates():
    spec = load_spec(ROOT / "examples" / "specs" / "threadify-intake-seed.yaml")
    warnings = validate_spec(spec)
    assert isinstance(warnings, list)


def test_body_count_gate():
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    spec["slides"] = [slide for slide in spec["slides"] if slide.get("role") != "body"][:]
    with pytest.raises(SpecError, match="3, 5, 7, or 9"):
        validate_spec(spec)


def test_offer_cta_requires_url():
    spec = load_spec(ROOT / "examples" / "specs" / "career-cta.yaml")
    spec["slides"][-1]["cta"].pop("url")
    with pytest.raises(SpecError, match="Offer CTA"):
        validate_spec(spec)


def test_strategy_fields_and_visual_modes_validate():
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    spec["strategy"] = {
        "goal": "saves",
        "hook_archetype": "enemy_belief",
        "belief_shift": "Old: prompts are one-offs. New: prompts are reusable systems.",
        "proof_level": "lived-experience",
        "cta_pressure": "soft",
        "visual_thesis": "Editorial paper with one orange system accent.",
        "virality_principles": ["observation-over-how-to"],
    }
    spec["design_pack"] = "editorial-paper"
    spec["render_engine"] = "browser"
    spec["slides"][0]["visual_mode"] = "shock-stat"
    warnings = validate_spec(spec)
    assert isinstance(warnings, list)


def test_imagegen_render_engine_validates():
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    spec["render_engine"] = "imagegen"
    warnings = validate_spec(spec)
    assert isinstance(warnings, list)


def test_unknown_design_pack_fails():
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    spec["design_pack"] = "glitter"
    with pytest.raises(SpecError, match="design_pack"):
        validate_spec(spec)


def test_unknown_visual_mode_fails():
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    spec["slides"][0]["visual_mode"] = "glitter"
    with pytest.raises(SpecError, match="visual_mode"):
        validate_spec(spec)


def test_unknown_render_quality_fails():
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    spec["render_quality"] = "insane"
    with pytest.raises(SpecError, match="render_quality"):
        validate_spec(spec)


def test_unknown_visual_priority_fails():
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    spec["strategy"] = {"visual_priority": "maximum"}
    with pytest.raises(SpecError, match="strategy.visual_priority"):
        validate_spec(spec)
