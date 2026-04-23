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

## Gate 2: AI critic red-team

Run the AI critic gate in `ai-critic-gate.md` after the spec draft and before final rendering.

The critic must pass:

- Hook strength
- Belief shift
- Specificity
- Proof integrity
- CTA fit
- Visual thesis
- Slide density
- Saveability
- Shareability

If the critic returns `revise` or `fail`, revise and rerun. Do not render the final pack while critic blockers remain.

## Gate 3: Per-slide finished image quality

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
- Browser visual QA fails contrast, crop safety, handle placement, dimensions, or text fit.
- All slides use the same visual mode in a 6+ slide carousel.
- A requested high-intensity makeover has a `makeover_scale.score` below `8.5/10`.
- A high-priority hook (`hook_priority` or `scroll_stop_priority` = high/extreme/thumbnail) has `hook_stop_score` below `8.5/10`.
- The first slide's visual stop score (`visual_qa.hook_stop.score`) is below `8.5/10` for a high-priority hook.
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
- Hook slide: headline+visual combination is forceful enough to interrupt fast feed scanning.
- Body slides: one idea per slide, each slide advances the reader, no filler.
- Recap slide: compresses the body into a memorable TL;DR.
- CTA slide: asks for one action and feels earned.
- Visual hierarchy: headline, body, accent, and handle are clearly separated.
- Visual thesis: mood, material, energy, and one dominant visual idea are clear.
- Contact sheet: the full sequence has rhythm and does not repeat the same visual beat.
- Makeover scale: when improving a weak prior version, the upgrade must feel visibly non-incremental.
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

If critic output is saved separately:

```bash
viral-carousel critic validate critic.json
```

After rendering, run:

```bash
viral-carousel qa output/run-name/manifest.json
```

The manifest must include `virality`, `strategy`, `visual_thesis`, `design.contact_sheet`, and per-slide `visual_mode` metadata.
It should also include `critic`, `pattern_bank`, `visual_qa`, `visual_qa.makeover_scale`, and `design.design_pack` metadata.

For browser renders, include:

- `design.render_quality`
- `design.dimensions_hq`
- per-slide `path_hq`

## Makeover Scale

Use this when recreating or upgrading an older carousel.

- `0-4`: mostly the same carousel with new rendering.
- `5-6`: cleaner, but still incremental.
- `7-8`: meaningfully better visual system and pacing.
- `8.5-10`: obvious premium upgrade; different enough that the old version feels obsolete.

If the old version was weak or visually generic, do not accept anything below `8.5`.

## First-slide stop gate

When the user requests aggressive scroll stopping:

- Set `strategy.hook_priority` to `high` or `extreme`.
- Prefer `render_quality: high` or `ultra`.
- Block final output unless both copy and visual hook-stop scores clear `8.5/10`.

## Final QA statement

Only finish with a statement like:

```text
QA passed: slide count, dimensions, bottom-left handle, CTA behavior, text fit, proof policy, and per-slide virality gate all passed.
```
