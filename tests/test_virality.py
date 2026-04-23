import pytest

from viral_carousel_maker.spec import SpecError, validate_spec
from viral_carousel_maker.virality import (
    detect_weak_hook_opener,
    score_cta_pressure,
    score_spec,
)


def base_spec():
    return {
        "version": 1,
        "title": "Test",
        "handle": "@tester",
        "template_family": "framework",
        "aspect_ratio": "vertical",
        "slides": [
            {"role": "hook", "title": "Growth advice is lying to you", "subtitle": "The metric you watch is not the one that compounds."},
            {"role": "body", "title": "The false win", "body": "Views feel good. Saves tell you the idea survived the scroll.", "main_idea": "Views and saves signal different jobs."},
            {"role": "body", "title": "The real signal", "body": "Replies show the topic has a nerve, not just a neat headline.", "main_idea": "Replies expose emotional tension."},
            {"role": "body", "title": "The next move", "body": "Build the next post from the strongest save or reply pattern.", "main_idea": "Use response data to choose the sequel."},
            {"role": "recap", "title": "TL;DR", "bullets": ["Views are reach.", "Saves are value.", "Replies are tension."]},
            {"role": "cta", "title": "Follow", "cta": {"type": "follow", "description": "For sharper creator systems."}},
        ],
    }


def test_banned_hook_patterns_are_detected():
    assert detect_weak_hook_opener("How to grow on Threads") == "how to"
    assert detect_weak_hook_opener("Here are 7 hooks") == "here are"
    assert detect_weak_hook_opener("7 tips for better carousels") == "numbered how-to opener"


def test_validate_spec_rejects_homework_hook_question():
    spec = base_spec()
    spec["slides"][0]["title"] = "Want to grow faster?"
    with pytest.raises(SpecError, match="banned weak opener"):
        validate_spec(spec)


def test_score_spec_rewards_belief_shift_and_low_density():
    spec = base_spec()
    spec["strategy"] = {
        "goal": "reach",
        "hook_archetype": "lie",
        "belief_shift": "Old: views equal growth. New: saves and replies expose durable demand.",
        "cta_pressure": "soft",
    }
    result = score_spec(spec)
    assert result["ok"] is True
    assert result["score"] >= 8.5
    assert result["metrics"]["body_slide_count"] == 3


def test_soft_cta_detects_high_pressure_offer():
    pressure = score_cta_pressure(
        {"type": "offer", "label": "Book now", "description": "DM me for the link", "url": "https://x.test"},
        {"title": "Buy the kit"},
    )
    assert pressure >= 6
