# Viral Carousel Maker

Viral Carousel Maker is a public Claude Code + Codex skill for turning an idea, Threadify draft, rough notes, or existing copy into a Threads-optimized carousel.

It is built for creators who want useful, saveable carousels that feel native to a social feed, not generic slide decks.

The current public v1 adds a Threads Virality Engine: staged interrogation, mandatory first-use style calibration, Threadify draft intake, hook lab, corpus-derived rules, AI critic gate, ImageGen-first production, quality gates, and a local performance loop.

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

## Preferred path: Codex native ImageGen, no API key needed

If you are using this skill inside Codex, you do not need to set an OpenAI API key for the preferred workflow.

Codex uses native ImageGen / ChatGPT ImageGen 2 as the production path for final carousel PNGs. Browser/Pillow renderers remain available for draft previews, prompt packs, and QA fallback output, but code-rendered slides are not the final production path unless the user explicitly accepts a fallback.

That means:

- Codex handles production image generation through native ImageGen when available
- Python/browser/Pillow output is draft-only fallback unless explicitly accepted
- No `OPENAI_API_KEY` is required for the Codex-native path

## Claude Desktop or Claude Code path

If you are using this skill in Claude Desktop or Claude Code, the intended image-generation workflow uses whichever image-generation provider/tool the end user has connected to Claude.

If no provider is connected, the OpenAI Images API is the first fallback and requires an OpenAI API key. If OpenAI is unavailable, use a Google image API key fallback.

When the skill is invoked in Claude Desktop or Claude Code and no connected provider or API fallback is available, it should pause before production image generation and tell the user:

```text
To use Viral Carousel Maker production image generation in Claude Desktop or Claude Code, connect an image-generation provider to Claude, provide an OpenAI API key fallback, or provide a Google image API key fallback.

OpenAI fallback key page: https://platform.openai.com/api-keys

Follow the setup guide in docs/claude-openai-api-key-setup.md, then either connect a Claude image provider, provide OPENAI_API_KEY, or provide GOOGLE_API_KEY/GEMINI_API_KEY.
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

The renderer can still make draft/procedural carousel PNGs without API calls, but Claude Desktop and Claude Code users should expect to connect an image provider, provide `OPENAI_API_KEY`, or provide a Google image API key before production image generation.

Install the API extras:

```bash
uv pip install -e ".[image-api]"
```

The OpenAI API fallback targets `gpt-image-2`.

## Quick start

```bash
cd /Users/lennoxsaint/viral-carousel-maker
uv run python -m playwright install chromium
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli render examples/specs/ai-framework.yaml --out-dir output/ai-framework --renderer imagegen
```

`--renderer imagegen` writes the prompt pack and returns `host_imagegen_required`; generate final PNGs through Codex native ImageGen or the configured Claude image provider/API fallback.

The Playwright/browser renderer is still available for draft previews. It uses HTML/CSS/SVG-style layouts and screenshots them into exact PNGs.

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

The installer regenerates the Claude/Codex skill bundles from canonical source, copies them into `~/.claude/skills/viral-carousel-maker` and `~/.codex/skills/viral-carousel-maker`, then verifies the installed copies include:

- ImageGen-first production policy with Codex native ImageGen / ChatGPT ImageGen 2
- mandatory first-use style calibration
- Claude OpenAI and Google API fallback instructions
- `references/style-calibration.md`

## Public skill behavior

When invoked, the skill:

- Checks for a saved local style profile
- Normalizes pasted copy, markdown/text files, or Threadify JSON when provided
- Runs a mandatory two-stage interrogation interview before generation, even when a profile or intake draft exists
- Uses `request_user_input` when the host provides it, or asks direct question batches when it does not
- Validates each answer batch with `viral-carousel interview next` and blocks drafting until `viral-carousel interview validate --require-ready` reports `ready_to_draft: true`
- Runs mandatory first-use style calibration and blocks production until the user approves a style sample
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
- Generates final PNGs through the active ImageGen path and assembles a production pack
- Creates or updates `~/.viral-carousel-maker/profile.yaml` after the first successful carousel
- Runs strict per-slide QA before calling the pack done

The skill is intentionally not a one-prompt generator. It asks several questions first so the final carousel can be tailored to the user's niche, voice, offer, visual taste, proof boundaries, and virality goal.

## Virality workflow

The production workflow is:

1. Normalize draft intake if the user provides text, markdown, or Threadify JSON.
2. Interrogate the idea and profile with Stage A essentials, then Stage B follow-ups.
3. Save answers to YAML/JSON and run `viral-carousel interview next` after each batch.
4. Run `viral-carousel interview validate --require-ready`; do not draft until it passes.
5. Generate and score hook candidates.
6. Select a corpus-backed virality principle.
7. Choose template family, body-slide count, CTA pressure, design pack, and visual thesis.
8. Draft the YAML spec.
9. Run `viral-carousel score`.
10. Run the AI critic gate and revise until it passes.
11. Generate ImageGen prompt packs and final PNGs through the active host/provider path.
12. Review the contact sheet and per-slide PNGs; regenerate any slide with misspelled text, wrong character details, weak hook, unreadable handwriting, or style drift.
13. Run QA.
14. Confirm local profile memory updated after successful QA.
15. Publish manually.
16. Paste metrics later with `viral-carousel metrics add`.

Run the interview gate:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli interview next --answers output/ai-framework/interview.yaml --use-profile
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli interview validate --answers output/ai-framework/interview.yaml --use-profile --require-ready
```

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
