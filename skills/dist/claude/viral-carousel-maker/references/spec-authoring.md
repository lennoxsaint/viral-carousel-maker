# Spec authoring

Specs are YAML files validated by `schemas/carousel.schema.json`.

Minimum shape:

```yaml
version: 1
title: "The carousel title"
handle: "@creator"
template_family: "framework"
aspect_ratio: "vertical"
design_pack: "editorial-paper"
render_engine: "browser"
render_quality: "high"
theme:
  palette:
    text: "#05063f"
    accent: "#e84b05"
strategy:
  goal: "saves"
  visual_priority: "high"
  hook_archetype: "enemy_belief"
  belief_shift: "Old: more ideas creates better content. New: one sharper idea travels farther."
  proof_level: "lived-experience"
  cta_pressure: "soft"
  hook_priority: "high"
  scroll_stop_priority: "high"
  visual_thesis: "Textured paper, bold navy/orange hierarchy, one simple system accent per slide."
  virality_principles:
    - "observation-over-how-to"
    - "one-idea-per-slide"
critic:
  verdict: "pass"
  scores:
    hook_strength: 9
    belief_shift: 9
    specificity: 8.5
    proof_integrity: 9
    cta_fit: 8
    visual_thesis: 9
    slide_density: 8.5
    saveability: 9
    shareability: 8.5
  blockers: []
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
- `visual_priority`: `standard`, `high`, `extreme`, or `thumbnail` visual dominance target.
- `hook_archetype`: selected Hook Lab archetype.
- `belief_shift`: old belief to new belief.
- `proof_level`: none, lived-experience, example, data, or receipt.
- `cta_pressure`: none, soft, medium, or hard.
- `visual_thesis`: mood, material, energy, and one dominant visual idea.
- `virality_principles`: short list of constitution rules applied.

## V2 fields

- `design_pack`: one of `editorial-paper`, `brutal-proof`, `quiet-luxury`, `founder-field-notes`, `photo-anchor`, `data-lab`, `myth-truth`, or `template-marketplace`.
- `render_engine`: `browser` by default, `pillow` only for fallback.
- `render_quality`: `standard`, `high`, or `ultra` (browser renderer).
- `critic`: structured AI critic output from `ai-critic-gate.md`.
- `pattern_bank`: selected public or private pattern summary.
- `learning`: optional profile/performance prior used to shape the carousel.

## Slide fields

Prefer adding:

- `main_idea`: one sentence explaining the slide's job.
- `visual_mode`: one of `editorial-paper`, `shock-stat`, `proof-grid`, `myth-truth`, `taxonomy`, `quiet-truth`, `receipt`, `contrast-table`, `field-note`, or `photo-anchor`.
- `hook_signal`: optional oversized hook keyword for `shock-stat` hooks.

## Scoring

Before rendering:

```bash
viral-carousel score path/to/spec.yaml
```

Revise if the score is below `8.5/10`, if the hook uses a banned opener, or if body slides are too dense.

If `strategy.hook_priority` or `strategy.scroll_stop_priority` is `high`, `extreme`, or `thumbnail`, the hook must also clear:

- `virality.metrics.hook_stop_score >= 8.5`
- `visual_qa.hook_stop.score >= 8.5`

If `strategy.visual_priority` is `high`, `extreme`, or `thumbnail`, every slide must include a visual component and pass visual-area thresholds in QA.

Render with the browser engine:

```bash
viral-carousel render path/to/spec.yaml --out-dir output/run-name
```

Use Pillow fallback only when browser rendering is unavailable:

```bash
viral-carousel render path/to/spec.yaml --out-dir output/run-name --renderer pillow
```
