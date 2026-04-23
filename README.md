# Viral Carousel Maker

Viral Carousel Maker is a public Claude Code + Codex skill for turning an idea, Threadify draft, rough notes, or existing copy into a Threads-optimized carousel.

It is built for creators who want useful, saveable carousels that feel native to a social feed, not generic slide decks.

The current public v1 adds a Threads Virality Engine: staged interrogation, Threadify draft intake, hook lab, corpus-derived rules, AI critic gate, browser-rendered visual systems, quality gates, and a local performance loop.

Start here:

- [Public quickstart](docs/public-quickstart.md)
- [Threadify draft intake](docs/threadify-draft-intake.md)
- [Threadify manual staging](docs/threadify-staging.md)

## What it creates

Default carousel:

1. One hook image
2. Five insight images by default, with 3, 5, 7, or 9 body slides supported
3. One recap / TL;DR image
4. One CTA image

Default export size is `1080x1350` for Threads-friendly mobile viewing. Square and widescreen exports are available from the renderer.

Every slide includes the creator's Threads handle in the bottom-left corner.

For premium clarity, set `render_quality: high` or `render_quality: ultra` in the spec.
This writes both standard slides and high-resolution masters for sharper exports.

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
uv run python -m playwright install chromium
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli render examples/specs/ai-framework.yaml --out-dir output/ai-framework
```

The default renderer is the Playwright/browser renderer. It uses HTML/CSS/SVG-style layouts and screenshots them into exact PNGs.

Pillow is still available as the simple fallback:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli render examples/specs/ai-framework.yaml --out-dir output/ai-framework-pillow --renderer pillow
```

For maximum first-slide impact and sharpness, add these fields to your spec:

```yaml
render_quality: "ultra"
strategy:
  visual_priority: "extreme"
  hook_priority: "extreme"
  scroll_stop_priority: "extreme"
```

`hook_priority: extreme` activates stricter hook-stop quality gates before delivery.
`visual_priority: extreme` enforces visual-dominance and lower-copy-density gates on every slide.

Validate the output:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli qa output/ai-framework/manifest.json
```

Normalize a Threadify draft before generation:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli intake examples/intake/threadify-draft.json --out output/threadify-seed.yaml
```

Check platform readiness:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli doctor --platform codex
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli doctor --platform claude-code
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
- Normalizes pasted copy, markdown/text files, or Threadify JSON when provided
- Runs a mandatory two-stage interrogation interview before generation, even when a profile or intake draft exists
- Uses `request_user_input` when the host provides it, or asks direct question batches when it does not
- Runs a Hook Lab with at least 5 candidate hooks
- Applies the Threads Virality Constitution before template selection
- Applies the public pattern bank and optional private local corpus summaries
- Chooses the carousel job: reach, saves, authority, conversion, or community
- Sets CTA pressure deliberately: none, soft, medium, or hard
- Creates a `visual_thesis` before rendering
- Chooses a named `design_pack`
- Forces a visual component (icon/object/diagram) on every slide
- Chooses one of 12 content-mechanic template families
- Drafts the carousel spec
- Scores hook strength, saveability, shareability, clarity, CTA fit, and proof quality
- Runs a required AI critic gate before final rendering
- Shows the spec before paid or native image generation
- Renders final PNGs and a production pack
- Creates or updates `~/.viral-carousel-maker/profile.yaml` after the first successful carousel
- Runs strict per-slide QA before calling the pack done

The skill is intentionally not a one-prompt generator. It asks several questions first so the final carousel can be tailored to the user's niche, voice, offer, visual taste, proof boundaries, and virality goal.

## Virality workflow

The production workflow is:

1. Normalize draft intake if the user provides text, markdown, or Threadify JSON.
2. Interrogate the idea and profile with Stage A essentials, then Stage B follow-ups.
3. Generate and score hook candidates.
4. Select a corpus-backed virality principle.
5. Choose template family, body-slide count, CTA pressure, design pack, and visual thesis.
6. Draft the YAML spec.
7. Run `viral-carousel score`.
8. Run the AI critic gate and revise until it passes.
9. Render with the browser renderer.
10. Review `contact_sheet.png`, `visual_qa.json`, and `visual_qa_report.md`.
11. Run QA.
12. Update local profile memory after successful QA when the user is using the skill workflow.
13. Publish manually.
14. Paste metrics later with `viral-carousel metrics add`.

Score before rendering:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli score examples/specs/threads-shock-stat.yaml
```

Validate critic output if you saved it as JSON:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli critic validate critic.json
```

Record metrics after posting:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli metrics add output/run-name/manifest.json --views 12000 --likes 300 --replies 40 --reposts 18 --saves 90 --clicks 12
```

Review recent performance:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli metrics report --days 30
```

Import a private local corpus summary:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli corpus import /path/to/posts --local-only
```

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

Visual modes can be mixed inside those families:

- `shock-stat`
- `proof-grid`
- `myth-truth`
- `taxonomy`
- `quiet-truth`
- `receipt`
- `contrast-table`
- `field-note`
- `photo-anchor`

## Design packs

The browser renderer supports named visual systems:

- `editorial-paper`
- `brutal-proof`
- `quiet-luxury`
- `founder-field-notes`
- `photo-anchor`
- `data-lab`
- `myth-truth`
- `template-marketplace`

Specs without a design pack default to `editorial-paper`.

## Output pack

Each run writes:

- `slides/*.png`
- `slides_hq/*.png` (browser renderer high-resolution masters)
- `caption.md`
- `alt_text.md`
- `prompts.jsonl`
- `profile_snapshot.yaml`
- `qa_report.md`
- `visual_qa.json`
- `visual_qa_report.md`
- `manifest.json`
- `contact_sheet.png`

`manifest.json` records selected strategy fields, visual thesis, critic result, pattern bank, virality score, design pack, visual modes, visual QA, makeover scale, and contact-sheet path.

When recreating a weak older carousel, treat `visual_qa.makeover_scale.score` as the upgrade bar. Anything below `8.5/10` is still too incremental for a high-intensity makeover.

When `hook_priority` is `high`, `extreme`, or `thumbnail`, the run must also pass:

- `virality.metrics.hook_stop_score >= 8.5`
- `visual_qa.hook_stop.score >= 8.5`

When `visual_priority` is `high` or `extreme`, the run must also pass:

- per-slide `visual_component_present = true`
- per-slide visual area ratio minimums (hook/body/recap/cta)
- stricter body-copy density gates for visual-first pacing

If either fails, the carousel is blocked and must be revised before final output.

## Gallery

See [docs/gallery.md](docs/gallery.md) for curated example packs and contact sheets.

## Threadify staging

V1 does not publish or automate browser posting.

The renderer produces Threadify-ready files and copy. Threadify-ready means posting-order PNGs, caption, alt text, manifest, QA report, visual QA, and contact sheet. It does not mean Threadify auth, browser staging, direct Threads publishing, or scheduling.

See [docs/threadify-draft-intake.md](docs/threadify-draft-intake.md) for draft intake and [docs/threadify-staging.md](docs/threadify-staging.md) for the optional manual staging workflow.

## V1 boundaries

Do not expect these in public v1:

- Direct Threads publishing
- Threadify auth or session automation
- Browser staging automation
- Background jobs or a cloud dashboard
- Remote profile sync or user accounts
- Automatic platform metrics ingestion
- Guaranteed virality claims

## Safety and proof

The skill does not fabricate evidence. Stats, claims, and examples must come from the user, user-provided sources, or clearly labeled qualitative reasoning.

Logo fetching is best-effort. If a logo cannot be safely fetched, the renderer uses a text badge instead.

## Credit and data policy

This project borrows public growth-loop ideas from LarryBrain/Larry Marketing while staying Threads-native and avoiding direct publishing automation in v1:

- [LarryBrain marketplace repo](https://github.com/OllieWazza/LarryBrain-Skill)
- [LarryBrain marketplace](https://www.larrybrain.com/)
- [Larry Marketing public install API](https://www.larrybrain.com/api/skills/install?slug=larry-marketing&mode=files)

See [docs/larrybrain-credit-and-data-policy.md](docs/larrybrain-credit-and-data-policy.md).

The public repo contains derived principles and templates only. It does not commit raw private corpus material, private performance logs, API keys, tokens, or user secrets.

## Development

```bash
uv run --with pytest --with Pillow --with PyYAML --with jsonschema --with playwright pytest
python scripts/render_skills.py --check
```
