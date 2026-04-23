"""Public derived Threads pattern bank.

This file contains derived principles and synthetic examples only. It must not
contain raw private corpus posts.
"""

from __future__ import annotations

from typing import Any


PUBLIC_PATTERN_BANK: dict[str, Any] = {
    "version": 2,
    "source_policy": "derived-principles-only",
    "hook_archetypes": {
        "lie": {
            "job": "Break a shared false belief.",
            "synthetic_examples": [
                "{topic} is a lie",
                "The {niche} advice that keeps failing",
            ],
            "best_for": ["reach", "authority"],
        },
        "identity_mirror": {
            "job": "Make the right viewer feel personally seen.",
            "synthetic_examples": [
                "You are not bad at {topic}",
                "The problem is not your discipline",
            ],
            "best_for": ["saves", "community"],
        },
        "private_room_observation": {
            "job": "Say the thing insiders say privately.",
            "synthetic_examples": [
                "Most {niche} posts die before slide two",
                "The quiet part of {topic}",
            ],
            "best_for": ["reach", "authority"],
        },
        "proof_receipt": {
            "job": "Lead with evidence, then teach the shift.",
            "synthetic_examples": [
                "After {proof}, I stopped believing {old_belief}",
                "The receipt that changed how I see {topic}",
            ],
            "best_for": ["conversion", "authority"],
        },
        "enemy_belief": {
            "job": "Name the belief that makes the audience lose.",
            "synthetic_examples": [
                "Stop treating {topic} like a checklist",
                "The trap behind {common_advice}",
            ],
            "best_for": ["reach", "saves"],
        },
    },
    "copy_rules": [
        "Prefer observation over instruction in the hook.",
        "Keep first-slide language short, certain, and compressed.",
        "Default to 3 body slides for reach and 5 for saveable education.",
        "Make long carousels earn their length with proof, story, or raw stakes.",
        "Treat high-pressure CTAs as a reach tax.",
    ],
    "cta_risk_patterns": {
        "low": ["follow for more", "save if useful"],
        "medium": ["grab the checklist", "join the waitlist"],
        "high": ["book a call", "buy now", "dm me"],
    },
}


def select_pattern_bundle(spec: dict[str, Any]) -> dict[str, Any]:
    strategy = spec.get("strategy") if isinstance(spec.get("strategy"), dict) else {}
    goal = str(strategy.get("goal", "saves"))
    requested = str(strategy.get("hook_archetype", "")).strip()
    archetypes = PUBLIC_PATTERN_BANK["hook_archetypes"]
    if requested in archetypes:
        selected = requested
    else:
        selected = next(
            (
                name
                for name, data in archetypes.items()
                if goal in data.get("best_for", [])
            ),
            "private_room_observation",
        )
    return {
        "version": PUBLIC_PATTERN_BANK["version"],
        "selected_hook_archetype": selected,
        "selected_pattern": archetypes[selected],
        "copy_rules": PUBLIC_PATTERN_BANK["copy_rules"],
        "source_policy": PUBLIC_PATTERN_BANK["source_policy"],
    }
