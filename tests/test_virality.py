import pytest

import viral_carousel_maker.corpus as corpus
from viral_carousel_maker.corpus import import_private_corpus, summarize_corpus_texts
from viral_carousel_maker.critic import validate_critic_output
from viral_carousel_maker.pattern_bank import select_pattern_bundle
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


def test_extreme_hook_priority_requires_higher_scroll_stop_score():
    spec = base_spec()
    spec["slides"][0]["title"] = "How to write better Threads"
    spec["strategy"] = {"hook_priority": "extreme", "belief_shift": "Old: tips win. New: tension wins."}
    with pytest.raises(SpecError, match="Hook scroll-stop score"):
        validate_spec(spec)


def test_visual_first_priority_rejects_dense_body_copy():
    spec = base_spec()
    spec["strategy"] = {"visual_priority": "extreme", "belief_shift": "Old: volume wins. New: visual tension wins."}
    spec["slides"][1]["body"] = (
        "Weak posts fail when they over-explain every caveat, stack too many frameworks, add multiple side notes, "
        "include defensive disclaimers, and bury the one point people can act on immediately after they swipe. "
        "A visual-first slide should not read like a mini essay."
    )
    with pytest.raises(SpecError, match="extreme visual priority caps at 34"):
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


def test_ai_critic_output_validation():
    critic = {
        "verdict": "pass",
        "scores": {
            "hook_strength": 9,
            "belief_shift": 9,
            "specificity": 8.5,
            "proof_integrity": 9,
            "cta_fit": 8,
            "visual_thesis": 9,
            "slide_density": 8.5,
            "saveability": 9,
            "shareability": 8.5,
        },
        "blockers": [],
    }
    ok, errors = validate_critic_output(critic)
    assert ok, errors


def test_pattern_bank_selects_goal_appropriate_bundle():
    spec = base_spec()
    spec["strategy"] = {"goal": "authority", "hook_archetype": "proof_receipt"}
    bundle = select_pattern_bundle(spec)
    assert bundle["selected_hook_archetype"] == "proof_receipt"
    assert bundle["source_policy"] == "derived-principles-only"


def test_private_corpus_summary_does_not_store_raw_posts():
    summary = summarize_corpus_texts(
        [
            "Threads growth is a lie\n\nThe real signal is saves.",
            "You are not bad at writing\n\nYour hook is too polite.",
        ]
    )
    assert summary["post_count"] == 2
    assert summary["raw_posts_stored"] is False
    assert "Threads growth is a lie" not in str(summary)


def test_private_corpus_import_writes_local_summary_only(tmp_path, monkeypatch):
    source = tmp_path / "posts"
    source.mkdir()
    (source / "posts.md").write_text(
        "Threads growth is a lie\n\nYou are not bad at hooks",
        encoding="utf-8",
    )
    monkeypatch.setattr(corpus, "CORPUS_DIR", tmp_path / "local-corpus")
    summary = import_private_corpus(source, local_only=True)
    summary_path = tmp_path / "local-corpus" / "posts-summary.json"
    assert summary["raw_posts_stored"] is False
    assert summary_path.exists()
    assert "Threads growth is a lie" not in summary_path.read_text(encoding="utf-8")
