# Viral Carousel Maker

Viral Carousel Maker is a public Claude Code + Codex skill for turning an idea, rough notes, or existing copy into a Threads-optimized carousel.

It is built for creators who want useful, saveable carousels that feel native to a social feed, not generic slide decks.

## What it creates

Default carousel:

1. One hook image
2. Five insight images by default, with 3, 5, 7, or 9 body slides supported
3. One recap / TL;DR image
4. One CTA image

Default export size is `1080x1350` for Threads-friendly mobile viewing. Square and widescreen exports are available from the renderer.

Every slide includes the creator's Threads handle in the bottom-left corner.

## Preferred path: Codex, no API key needed

If you are using this skill inside Codex, you do not need to set an OpenAI API key for the preferred workflow.

Codex can use its native image generation capability for style boards, backgrounds, hero accents, and visual objects. The Python renderer then places all final text itself so words stay crisp and correct.

That means:

- Codex handles image generation when available
- Python/Pillow handles exact layout and text rendering
- No `OPENAI_API_KEY` is required for the Codex-native path

## Claude or local CLI path

If you are using Claude Code or running the renderer outside Codex, you can still use the skill.

The local renderer works without API calls by using procedural textures and code-rendered layouts. If you want the optional OpenAI Image API asset-generation fallback, set `OPENAI_API_KEY` and install the image API extras:

```bash
uv pip install -e ".[image-api]"
```

The API fallback targets `gpt-image-2`.

## Quick start

```bash
cd /Users/lennoxsaint/viral-carousel-maker
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema python -m viral_carousel_maker.cli render examples/specs/ai-framework.yaml --out-dir output/ai-framework
```

Validate the output:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema python -m viral_carousel_maker.cli qa output/ai-framework/manifest.json
```

Render the Claude and Codex skill copies:

```bash
python scripts/render_skills.py
```

Install locally:

```bash
bash scripts/install.sh
```

## Public skill behavior

When invoked, the skill:

- Checks for a saved local style profile
- Runs a strategic but friendly interview if the profile is missing or thin
- Chooses one of 12 content-mechanic template families
- Drafts the carousel spec
- Scores hook strength, saveability, clarity, CTA fit, and proof quality
- Shows the spec before paid or native image generation
- Renders final PNGs and a production pack
- Runs QA before calling the pack done

## Template families

The 12 v1 content-mechanic families are:

- Story
- List
- Framework
- Timeline
- Debate
- Examples
- Data
- Quote
- Map
- Mistakes
- Recap
- CTA

One family is inspired by the attached reference direction: textured paper, big condensed headlines, bold whitespace, navy/orange accents, progress markers, and subtle swipe cues. It is one family, not the entire product.

## Output pack

Each run writes:

- `slides/*.png`
- `caption.md`
- `alt_text.md`
- `prompts.jsonl`
- `profile_snapshot.yaml`
- `qa_report.md`
- `manifest.json`

## Threadify staging

V1 does not publish or automate browser posting.

The renderer produces Threadify-ready files and copy. See [docs/threadify-staging.md](docs/threadify-staging.md) for the optional manual staging workflow.

## Safety and proof

The skill does not fabricate evidence. Stats, claims, and examples must come from the user, user-provided sources, or clearly labeled qualitative reasoning.

Logo fetching is best-effort. If a logo cannot be safely fetched, the renderer uses a text badge instead.

## Development

```bash
uv run --with pytest --with Pillow --with PyYAML --with jsonschema pytest
python scripts/render_skills.py --check
```
