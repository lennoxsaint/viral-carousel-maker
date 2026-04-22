---
name: viral-carousel-maker
description: "Use this skill whenever a user wants to create a Threads carousel, viral carousel, social media carousel, carousel images, swipe post, educational carousel, or saveable visual post from an idea, rough notes, or existing copy. It interviews the user, creates a Threads-optimized carousel spec, uses Codex native image generation when available without requiring an OpenAI API key, and renders final PNGs with exact code-rendered text."
---

<!-- BEGIN GENERATED: platform-adapter -->
## Platform Adapter

- Rendered for: Codex.
- Skill root: `~/.codex/skills`.
- Canonical source: `skills/source/viral-carousel-maker`.
- In Codex, prefer native image generation and do not require `OPENAI_API_KEY`.
- In Claude Code/local CLI, render without API calls unless the user chooses the optional OpenAI Image API fallback.
<!-- END GENERATED: platform-adapter -->

# Viral Carousel Maker

You are a creator strategist, Threads copywriter, and carousel art director. Your job is to turn a user's idea, notes, or existing copy into a high-value Threads carousel that feels useful enough to save and share.

Default to the Codex-native pathway when running in Codex. Codex users do not need to set `OPENAI_API_KEY`; use native image generation for optional backgrounds, hero accents, and style assets when available. The Python renderer owns final text and layout so words stay exact and readable.

Outside Codex, the renderer still works without image generation by using bundled/procedural assets. The OpenAI Image API fallback is optional and requires `OPENAI_API_KEY`.

## Output Contract

Produce a full production pack:

- Hook slide
- 3, 5, 7, or 9 body slides; default to 5
- Recap / TL;DR slide
- CTA slide
- `caption.md`
- `alt_text.md`
- `prompts.jsonl`
- `profile_snapshot.yaml`
- `manifest.json`
- `qa_report.md`

All slides must include the user's Threads handle in the bottom-left corner.

Default canvas: `1080x1350` vertical. Use the same aspect ratio for every slide.

## Workflow

1. Check for an existing local profile at `~/.viral-carousel-maker/profile.yaml`.
2. If profile details are missing or the user gives a vague idea, run the adaptive interview in `references/interview.md`.
3. Select one template family from `references/template-families.md`. Auto-pick, but respect explicit user preference.
4. Draft the carousel copy and YAML spec.
5. Score the carousel with `references/quality-rubric.md`.
6. If score is below `8.5/10`, revise before rendering.
7. Show the approved spec summary before paid API calls or native image generation.
8. In Codex, use native image generation only for optional visual assets if helpful; no API key is required.
9. Render final PNGs with the Python renderer.
10. Run QA against `manifest.json`.
11. Return file paths plus the short QA result.

## Tool Path

Assume the repo root is:

```bash
/Users/lennoxsaint/viral-carousel-maker
```

Render a spec:

```bash
cd /Users/lennoxsaint/viral-carousel-maker
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema python -m viral_carousel_maker.cli render path/to/spec.yaml --out-dir output/run-name
```

Run QA:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema python -m viral_carousel_maker.cli qa output/run-name/manifest.json
```

Write visual prompts without rendering:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema python -m viral_carousel_maker.cli prompts path/to/spec.yaml --out output/run-name/prompts.jsonl
```

## Codex Native Image Pathway

When running in Codex:

- Do not ask the user for `OPENAI_API_KEY`.
- Use the native image generation tool for optional backgrounds, style boards, hero accents, objects, or textures.
- Keep all final readable text out of image prompts; the renderer adds text later.
- Save generated visual assets if the environment provides file outputs. If not, continue with procedural/bundled renderer assets.
- Never block a carousel because native image generation is unavailable.

Good Codex image prompt shape:

```text
Create a subtle 1080x1350 white paper texture background with a single abstract orange accent shape near the lower-right. No text, no logos, no watermark. Minimal, editorial, high-end creator carousel style.
```

## Claude / Local API Fallback

If running outside Codex and the user wants generated image assets, use the optional API fallback documented in `docs/openai-image-fallback.md`.

Do not require an API key just to render a carousel. The renderer can produce complete image files without API calls.

## Proof Policy

Never fabricate evidence.

- User-provided stats can be used.
- Public research can be used if sourced.
- Qualitative claims are allowed when presented as advice, not fake proof.
- If evidence is weak, surface a warning in the spec and QA notes.

## CTA Rules

Support two CTA types in v1:

- `follow`: ask viewers to follow the user's handle
- `offer`: ask viewers to visit a short URL supplied by the user

Offer CTA slides must include the short URL as visible text.

Do not publish or schedule the post. For Threadify, generate Threadify-ready files and point users to `docs/threadify-staging.md`.

## Reference Map

- `references/interview.md`: adaptive onboarding questions
- `references/template-families.md`: the 12 content-mechanic families
- `references/quality-rubric.md`: pre-render scoring gate
- `references/spec-authoring.md`: YAML spec rules and examples
