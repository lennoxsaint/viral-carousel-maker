# Spec authoring

Specs are YAML files validated by `schemas/carousel.schema.json`.

Minimum shape:

```yaml
version: 1
title: "The carousel title"
handle: "@creator"
template_family: "framework"
aspect_ratio: "vertical"
theme:
  palette:
    text: "#05063f"
    accent: "#e84b05"
strategy:
  goal: "saves"
  hook_archetype: "enemy_belief"
  belief_shift: "Old: more ideas creates better content. New: one sharper idea travels farther."
  proof_level: "lived-experience"
  cta_pressure: "soft"
  visual_thesis: "Textured paper, bold navy/orange hierarchy, one simple system accent per slide."
  virality_principles:
    - "observation-over-how-to"
    - "one-idea-per-slide"
slides:
  - role: hook
    title: "Stop wasting your best ideas"
    subtitle: "A simple system for turning one insight into a full carousel."
    visual_mode: "shock-stat"
  - role: body
    title: "Find the pain"
    body: "Start with what your audience is already frustrated by."
    main_idea: "Audience pain creates attention."
  - role: body
    title: "Name the shift"
    body: "Every saveable carousel moves the reader from confusion to clarity."
  - role: body
    title: "Make it concrete"
    body: "Use steps, examples, numbers, or contrast."
  - role: recap
    title: "TL;DR"
    bullets:
      - "Pain first"
      - "One idea per slide"
      - "CTA only after value"
  - role: cta
    title: "Follow"
    cta:
      type: follow
      description: "For more daily creator systems."
```

Body slide counts must be 3, 5, 7, or 9.

Keep final slide text concise. If the CTA is an offer, include `url`.

## Strategy fields

Use `strategy` whenever possible:

- `goal`: reach, saves, authority, conversion, or community.
- `hook_archetype`: selected Hook Lab archetype.
- `belief_shift`: old belief to new belief.
- `proof_level`: none, lived-experience, example, data, or receipt.
- `cta_pressure`: none, soft, medium, or hard.
- `visual_thesis`: mood, material, energy, and one dominant visual idea.
- `virality_principles`: short list of constitution rules applied.

## Slide fields

Prefer adding:

- `main_idea`: one sentence explaining the slide's job.
- `visual_mode`: one of `editorial-paper`, `shock-stat`, `proof-grid`, `myth-truth`, `taxonomy`, `quiet-truth`, `receipt`, `contrast-table`, `field-note`, or `photo-anchor`.

## Scoring

Before rendering:

```bash
viral-carousel score path/to/spec.yaml
```

Revise if the score is below `8.5/10`, if the hook uses a banned opener, or if body slides are too dense.
