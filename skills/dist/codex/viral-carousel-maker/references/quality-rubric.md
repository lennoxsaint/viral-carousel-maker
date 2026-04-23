# Virality and slide quality gates

Quality gates are mandatory. Do not finish a carousel until both gates pass.

## Gate 1: Strategy and spec quality

Score before rendering. Revise until:

- Average score is `9.0/10` or higher.
- No category is below `8/10`.
- Hook strength is `9/10` or higher.
- Saveability is `9/10` or higher.
- CTA fit is `8/10` or higher.

Categories:

- Hook strength: does slide 1 stop a fast Threads feed scroll?
- Belief shift: is the old belief and new belief obvious?
- Audience specificity: would a precise viewer feel seen?
- Curiosity chain: does each slide make the next slide feel worth swiping to?
- Saveability: would the target viewer come back to this later?
- Shareability: would the target viewer send this to someone?
- Specificity: are claims concrete instead of generic?
- Proof integrity: are stats and strong claims supported?
- Clarity: is every slide understandable on mobile?
- Density control: is there one core idea per slide?
- Visual fit: does the chosen template match the niche, topic, and user taste?
- CTA fit: does the final ask feel earned?

Common revisions:

- Replace broad claims with specific viewer pain.
- Cut body slides to one main idea per slide.
- Turn generic tips into named steps, examples, or contrasts.
- Move proof closer to the claim it supports.
- Make the hook sharper but not misleading.
- Make the CTA softer if the carousel has not earned a hard ask.
- Remove words that feel like generic AI advice.

## Gate 2: Per-slide finished image quality

Run this after rendering every slide. Every slide must pass before final delivery.

Hard blockers:

- Wrong slide count.
- Wrong dimensions or inconsistent aspect ratio.
- Missing handle in the bottom-left corner.
- Hook starts with "How to", "Here are", "Want to", "Save this", "Follow for", or a plain numbered tips opener.
- Hook is a homework question instead of a statement or identity mirror.
- Hook uses fake urgency, generic trigger words, or unsupported transformation bait.
- Selected hook does not create a clear old-belief-to-new-belief shift.
- Text is clipped, too small, crowded, or visually unclear.
- Hook or body copy is overlong for mobile feed speed.
- CTA slide does not match the selected CTA type.
- Offer CTA is missing the visible short URL.
- CTA is high-pressure before value has been earned.
- Any unsupported factual claim appears without a warning.
- Any generated visual contains unwanted text, fake UI, fake logos, or obvious artifacts.
- A body slide contains more than one main idea.
- Hook slide opens with the brand instead of the viewer's pain/desire.
- Hook slide looks visually weak, generic, cluttered, or like a bland slide deck.

Per-slide review checklist:

- Hook slide: strong pain/desire, clear curiosity gap, no generic headline.
- Body slides: one idea per slide, each slide advances the reader, no filler.
- Recap slide: compresses the body into a memorable TL;DR.
- CTA slide: asks for one action and feels earned.
- Visual hierarchy: headline, body, accent, and handle are clearly separated.
- Visual thesis: mood, material, energy, and one dominant visual idea are clear.
- Contact sheet: the full sequence has rhythm and does not repeat the same visual beat.
- Mobile readability: all text can be read on a phone without zooming.
- Pacing: the carousel alternates tension, clarity, and reward.
- Brand fit: colors, tone, and layout match the user's profile.
- Threads-native feel: looks like a high-value social post, not a corporate slide deck.

## Required revision loop

If any gate fails:

1. Name the failing category or slide.
2. Explain the specific issue in one sentence.
3. Revise the copy, layout, template choice, or visual prompt.
4. Rerender or regenerate only what is needed.
5. Rerun the gate.

Do not say "done" while any blocker remains.

## CLI gates

Before final rendering, run:

```bash
viral-carousel score path/to/spec.yaml
```

After rendering, run:

```bash
viral-carousel qa output/run-name/manifest.json
```

The manifest must include `virality`, `strategy`, `visual_thesis`, `design.contact_sheet`, and per-slide `visual_mode` metadata.

## Final QA statement

Only finish with a statement like:

```text
QA passed: slide count, dimensions, bottom-left handle, CTA behavior, text fit, proof policy, and per-slide virality gate all passed.
```
