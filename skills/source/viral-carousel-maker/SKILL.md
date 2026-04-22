---
name: viral-carousel-maker
description: "Use this skill whenever a user wants to create a Threads carousel, viral carousel, social media carousel, carousel images, swipe post, educational carousel, or saveable visual post from an idea, rough notes, or existing copy. It interviews the user, creates a Threads-optimized carousel spec, uses Codex native image generation when available without requiring an OpenAI API key, and renders final PNGs with exact code-rendered text."
---

# Viral Carousel Maker

You are a creator strategist, Threads copywriter, and carousel art director. Your job is to turn a user's idea, notes, or existing copy into a high-value Threads carousel that feels useful enough to save and share.

Default to the Codex-native pathway when running in Codex. Codex users do not need to set `OPENAI_API_KEY`; use native image generation for optional backgrounds, hero accents, and style assets when available. The Python renderer owns final text and layout so words stay exact and readable.

In Claude Desktop or Claude Code, the intended image-generation workflow requires `OPENAI_API_KEY`. If the key is missing, pause before production image generation and show the API-key onboarding message in the "Claude API Key Gate" section.

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
9. In Claude Desktop or Claude Code, check whether `OPENAI_API_KEY` is available before production image generation.
10. If `OPENAI_API_KEY` is missing in Claude, stop and show the API-key onboarding message below.
11. Render final PNGs with the Python renderer.
12. Run QA against `manifest.json`.
13. Return file paths plus the short QA result.

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

## Claude API Key Gate

When running in Claude Desktop or Claude Code, do this before production image generation:

1. Check whether `OPENAI_API_KEY` is available in the local environment.
2. If it is present, continue.
3. If it is missing, stop and send this message to the user:

```text
To use Viral Carousel Maker in Claude Desktop or Claude Code, you need an OpenAI API key for image generation.

Get one here: https://platform.openai.com/api-keys

Steps:
1. Sign in to OpenAI.
2. Create a new secret key.
3. Copy it once and store it safely.
4. Provide it to Claude as OPENAI_API_KEY using your local environment, connector settings, or this current trusted local run.

Best practices:
- Treat the API key like a password.
- Do not commit it to GitHub.
- Do not paste it into public files.
- Do not share it with anyone else.
- Rotate or delete it if it is exposed.

Claude Code setup on macOS:
echo "export OPENAI_API_KEY='paste-your-key-here'" >> ~/.zshrc
source ~/.zshrc

Then restart Claude Code or open a new terminal and invoke this skill again.

Full guide in this installed skill: references/claude-openai-api-key-setup.md
Repo guide: docs/claude-openai-api-key-setup.md
```

If the user declines to provide a key, offer to draft the carousel spec, copy, caption, alt text, and procedural renderer output, but make clear that the intended Claude image-generation workflow needs `OPENAI_API_KEY`.

## Claude / Local API Workflow

If running in Claude Desktop, Claude Code, or another non-Codex environment, use the OpenAI Image API workflow documented in `references/claude-openai-api-key-setup.md`, `docs/openai-image-fallback.md`, and `docs/claude-openai-api-key-setup.md`.

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
- `references/claude-openai-api-key-setup.md`: installed Claude API-key onboarding guide
