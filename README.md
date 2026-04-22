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

## Claude Desktop or Claude Code path

If you are using this skill in Claude Desktop or Claude Code, the intended image-generation workflow requires an OpenAI API key.

When the skill is invoked in Claude Desktop or Claude Code, it should pause before production image generation and tell the user:

```text
To use Viral Carousel Maker in Claude Desktop or Claude Code, you need an OpenAI API key for image generation.

Get one here: https://platform.openai.com/api-keys

Follow the setup guide in docs/claude-openai-api-key-setup.md, then provide the key to Claude as OPENAI_API_KEY.
Do not commit the key to GitHub, paste it into public files, or share it with anyone else.
```

Full setup guide:

- [Claude and OpenAI API key setup](docs/claude-openai-api-key-setup.md)
- Official OpenAI API key page: <https://platform.openai.com/api-keys>
- Official OpenAI API key safety guide: <https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety>
- Official OpenAI "where do I find my API key" guide: <https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key_>

For Claude Code on macOS, the usual setup is:

```bash
echo "export OPENAI_API_KEY='paste-your-key-here'" >> ~/.zshrc
source ~/.zshrc
```

Then restart Claude Code or open a new terminal session before invoking the skill again.

For Claude Desktop, use the safest available local environment or connector configuration for your setup. If Claude Desktop cannot read environment variables, the skill should ask the user whether they are comfortable providing the key for the current local run only. Never store it in the repo.

The renderer can still make draft/procedural carousel PNGs without API calls, but Claude Desktop and Claude Code users should expect to provide `OPENAI_API_KEY` for the intended OpenAI image-generation workflow.

Install the API extras:

```bash
uv pip install -e ".[image-api]"
```

The API image workflow targets `gpt-image-2`.

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
- Runs a mandatory interrogation interview before generation, even when a profile exists
- Uses `request_user_input` when the host provides it, or asks direct question batches when it does not
- Chooses one of 12 content-mechanic template families
- Drafts the carousel spec
- Scores hook strength, saveability, shareability, clarity, CTA fit, and proof quality
- Shows the spec before paid or native image generation
- Renders final PNGs and a production pack
- Creates or updates `~/.viral-carousel-maker/profile.yaml` after the first successful carousel
- Runs strict per-slide QA before calling the pack done

The skill is intentionally not a one-prompt generator. It asks several questions first so the final carousel can be tailored to the user's niche, voice, offer, visual taste, proof boundaries, and virality goal.

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
