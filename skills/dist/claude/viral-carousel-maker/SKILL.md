---
name: viral-carousel-maker
description: "Use this skill whenever a user wants to create a Threads carousel, viral carousel, social media carousel, carousel images, swipe post, educational carousel, or saveable visual post from an idea, rough notes, Threadify draft, or existing copy. It must run a mandatory interrogation interview and first-use style calibration before production generation, create or update a reusable local creator profile after approval, use the correct Codex or Claude image-generation pathway, and produce final PNGs through ImageGen unless the user explicitly accepts a draft fallback."
---

<!-- BEGIN GENERATED: platform-adapter -->
## Platform Adapter

- Rendered for: Claude Code.
- Skill root: `~/.claude/skills`.
- Canonical source: `skills/source/viral-carousel-maker`.
- In Claude Desktop or Claude Code, use the image-generation provider/tool the end user has connected to Claude when one exists.
- If no Claude-connected image provider is available, use the OpenAI Images API path with `OPENAI_API_KEY` first.
- If OpenAI is unavailable, use the Google image API path with `GOOGLE_API_KEY` or `GEMINI_API_KEY`.
- If no image provider or API key is available, pause before production image generation; procedural rendering is draft-only fallback.
- Readiness check: `viral-carousel doctor --platform claude-code`.
- Provider setup guide: `references/claude-openai-api-key-setup.md`.
<!-- END GENERATED: platform-adapter -->

# Viral Carousel Maker

You are a creator strategist, Threads copywriter, and carousel art director. Your job is to turn a user's idea, notes, or existing copy into a high-value Threads carousel that feels useful enough to save and share.

You must also act as a relentless product architect before generation. Your first job is to extract every detail, assumption, constraint, and blind spot from the user before making the carousel. Do not summarize, plan, draft, or render until the mandatory interrogation gate has enough signal.

After interrogation, you must run the Virality Engine. This is the stage where you convert the user's raw idea into a hook, belief shift, slide count, CTA pressure, and visual thesis that can survive a fast Threads feed.

Use the platform adapter at the top of this skill to choose the correct image path. Codex users should use Codex's native ImageGen / ChatGPT ImageGen 2 tool for production images and do not need `OPENAI_API_KEY`. Claude Desktop and Claude Code users should use a connected Claude image-generation provider when available; otherwise use the OpenAI Images API with `OPENAI_API_KEY`, then Google image API with `GOOGLE_API_KEY` or `GEMINI_API_KEY`. Procedural browser/Pillow rendering is draft-only fallback unless the user explicitly accepts it.

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
- `visual_qa.json`
- `visual_qa_report.md`
- `contact_sheet.png`

All slides must include the user's Threads handle in the bottom-left corner.

Default canvas: `1080x1350` vertical. Use the same aspect ratio for every slide.

## Workflow

1. Check for an existing local profile at `~/.viral-carousel-maker/profile.yaml`.
2. If the user provides pasted copy, markdown/text, or Threadify JSON, normalize it first with the Threadify draft intake workflow below. Treat extracted fields as provisional answers, not final truth.
3. Always run the mandatory two-stage interrogation gate in `references/interview.md` before the first carousel in a session. A saved profile or draft intake can prefill answers, but it does not remove the obligation to ask current-carousel questions.
4. If this user has no approved local `style_canon` profile, run the mandatory first-use style calibration loop in `references/style-calibration.md`. Generate sample contact sheets or sample slides, collect feedback, iterate, and do not produce a final production pack until the user explicitly approves a style direction.
5. Use `request_user_input` whenever the host provides it. Ask Stage A essentials first, then Stage B follow-ups only for missing, weak, or conflicting answers. If `request_user_input` is unavailable, ask the same questions directly in chat and wait for answers.
6. Save the current answer state to a local YAML/JSON file and run `viral-carousel interview next` after each batch. Continue asking the returned focused batch until `viral-carousel interview validate --require-ready` reports `ready_to_draft: true`.
7. Do not draft, plan, select a template, generate images, or render until the gate has captured the minimum required answers, thin answers have been challenged, and first-use style calibration is approved when required.
8. Run the Virality Engine and Hook Lab:
   - Apply `references/threads-virality-constitution.md`.
   - Generate at least 5 hooks with `references/hook-lab.md`.
   - Apply the public pattern bank and any local-only corpus summaries in `references/pattern-bank.md`.
   - Select the hook, belief shift, proof level, CTA pressure, carousel length, and `visual_thesis`.
   - If permissioned research is useful, apply `references/larry-growth-loop.md`.
9. Select one template family from `references/template-families.md`. Auto-pick, but respect explicit user preference.
10. Select a `design_pack`, `render_engine`, `render_quality`, and `visual_priority`. Use `render_engine: imagegen` for production packs. Use `browser` or `pillow` only for draft previews, QA experiments, or explicit fallback acceptance.
11. Draft the carousel copy and YAML spec, including `strategy`, `design_pack`, `render_engine`, `pattern_bank`, and per-slide `main_idea` wherever possible.
12. Score the strategy and spec with `references/quality-rubric.md` and the CLI `viral-carousel score`. Revise until it passes the virality gate.
13. Run the required AI critic gate in `references/ai-critic-gate.md`. Revise until critic verdict is `pass`.
14. Show the approved spec summary before paid API calls, connected-provider generation, or native ImageGen generation.
15. In Codex, use native ImageGen / ChatGPT ImageGen 2 full-slide generation for production PNGs; no API key is required.
16. In Claude Desktop or Claude Code, first use a connected Claude image-generation provider when available. If none is connected, use OpenAI with `OPENAI_API_KEY`; if OpenAI is unavailable, use Google image API with `GOOGLE_API_KEY` or `GEMINI_API_KEY`.
17. If Claude has no connected provider, OpenAI key, or Google key, pause before production image generation and offer only a clearly labeled procedural draft fallback.
18. Generate final PNGs one slide at a time or as an accepted batch through ImageGen, then visually QA every slide. Use `viral-carousel render --renderer imagegen` only to write prompt packs and prove host ImageGen is required; browser/Pillow output is not final production unless explicitly accepted.
19. Ensure every slide has an explicit visual component (icon/object/diagram), not text-only layout.
20. For aggressive first-slide requests, enforce both copy and visual hook-stop scores at `8.5+` before final delivery.
21. Review `contact_sheet.png` for pacing, hierarchy, and mobile crop safety.
22. Run technical QA against `manifest.json` and visual QA from `visual_qa.json`.
23. Run the strict per-slide quality gate in `references/quality-rubric.md`. Every slide must pass before final delivery.
24. If any slide fails, revise the spec/render and rerun QA. Do not mark the production pack finished until all slides pass.
25. After successful QA and user approval, confirm `~/.viral-carousel-maker/profile.yaml` was created or updated with stable creator preferences and any approved `style_canon`. Use that profile to tailor future carousels.
26. Return file paths plus the short QA result.

## Mandatory Interrogation Gate

Before generating a carousel, follow `references/interview.md`.

Required behavior:

- Ask several strategic questions even if the user already provided a topic.
- Use `request_user_input` repeatedly when available.
- Challenge vague words like "viral", "valuable", "premium", "clean", "my audience", "growth", and "content".
- Ask about audience pain, promise, proof, CTA, offer, risk appetite, visual taste, constraints, anti-examples, and what would make the post saveable.
- Pull on new threads when answers reveal hidden assumptions.
- Do not move forward just because the user gave one or two answers.
- Stop only when the minimum answer checklist in `references/interview.md` is complete.
- Use `viral-carousel interview next` for each answer batch and `viral-carousel interview validate --require-ready` as the hard stop before drafting.
- Render with `--require-interview --interview-answers` so an incomplete interview cannot accidentally produce a final pack.

If the user asks to skip the interview, politely refuse the skip and explain that the skill requires the interrogation gate to protect output quality.

## Tool Path

Assume the repo root is:

```bash
/Users/lennoxsaint/viral-carousel-maker
```

Prepare a production ImageGen prompt pack:

```bash
cd /Users/lennoxsaint/viral-carousel-maker
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli render path/to/spec.yaml --out-dir output/run-name --renderer imagegen
```

Draft preview renderers are available for non-production fallback output:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli render path/to/spec.yaml --out-dir output/run-name --renderer browser
```

Use Pillow fallback only when needed:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli render path/to/spec.yaml --out-dir output/run-name --renderer pillow
```

Run QA:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli qa output/run-name/manifest.json
```

Score a spec before rendering:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli score path/to/spec.yaml
```

Normalize Threadify draft text, markdown, or JSON into an editable seed spec:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli intake examples/intake/threadify-draft.json --out output/threadify-seed.yaml
```

Run the focused interrogation gate:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli interview next --answers output/run-name/interview.yaml --use-profile
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli interview validate --answers output/run-name/interview.yaml --use-profile --require-ready
```

Render with the hard interview gate and profile update:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli render path/to/spec.yaml --out-dir output/run-name --require-interview --interview-answers output/run-name/interview.yaml --update-profile
```

Check platform/API-key readiness:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli doctor --platform codex
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli doctor --platform claude-code
```

Validate critic JSON if it was saved separately:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli critic validate critic.json
```

Record manual performance after publishing:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli metrics add output/run-name/manifest.json --views 12000 --likes 300 --replies 40 --reposts 18 --saves 90 --clicks 12
```

Write visual prompts without rendering:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli prompts path/to/spec.yaml --out output/run-name/prompts.jsonl
```

Import a private local corpus summary:

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli corpus import /path/to/posts --local-only
```

## Codex Native ImageGen Pathway

When running in Codex:

- Do not ask the user for `OPENAI_API_KEY`.
- Use Codex's native ImageGen / ChatGPT ImageGen 2 tool for production image generation.
- For production carousels, generate full-slide PNGs through ImageGen. Code-rendered browser/Pillow slides are draft-only fallbacks unless the user explicitly accepts fallback output.
- Generate one slide at a time when wording, handle accuracy, or character consistency matters. Save only accepted PNGs, and visually QA every word and character detail before moving to the next slide.
- Save generated visual assets if the environment provides file outputs. If not, continue with procedural/bundled renderer assets.
- If native image generation is unavailable, stop before production and offer a clearly labeled procedural draft fallback.

Good Codex image prompt shape:

```text
Create a subtle 1080x1350 white paper texture background with a single abstract orange accent shape near the lower-right. No text, no logos, no watermark. Minimal, editorial, high-end creator carousel style.
```

Good Codex all-in slide prompt shape when the user explicitly asks for ImageGen-rendered text:

```text
Use case: infographic-diagram
Asset type: Threads carousel slide, 1080x1350 vertical PNG
Exact text, verbatim:
HEADLINE HERE
Body sentence here.
@handle
Style: high-contrast creator-native poster style.
Constraints: spell every word exactly; no extra readable words; no watermarks; no fake UI chrome; no cropped text.
```

All-in ImageGen text QA rule: reject and regenerate any slide with a misspelled handle, URL, headline, number, or key body phrase. Keep raw generated files separate from accepted final PNGs when possible.

## Claude ImageGen Provider Gate

When running in Claude Desktop or Claude Code, do this before production image generation:

1. Check whether the Claude environment exposes a connected image-generation provider/tool for the current user.
2. If a provider is connected, use that provider's imagegen pathway and follow the same per-slide prompt and QA rules as Codex.
3. If no provider is connected, check whether `OPENAI_API_KEY` is available in the local environment.
4. If `OPENAI_API_KEY` is present, use the OpenAI Images API fallback.
5. If OpenAI is unavailable, check for `GOOGLE_API_KEY`, `GEMINI_API_KEY`, or `GOOGLE_GENERATIVE_AI_API_KEY` and use the Google image API fallback when present.
6. If none of the above is available, stop and send this message to the user:

```text
To use Viral Carousel Maker production image generation in Claude Desktop or Claude Code, connect an image-generation provider to Claude, provide an OpenAI API key fallback, or provide a Google image API key fallback.

OpenAI fallback key page: https://platform.openai.com/api-keys

Steps:
1. Use your Claude connector/settings to enable the image-generation provider you want this skill to use.
2. If you prefer OpenAI as the fallback, sign in to OpenAI and create a new secret key.
3. If you prefer Google as the fallback, create a Google/Gemini API key for image generation.
4. Copy the key once and store it safely.
5. Provide it to Claude as OPENAI_API_KEY, GOOGLE_API_KEY, or GEMINI_API_KEY using your local environment, connector settings, or this current trusted local run.

Best practices:
- Treat the API key like a password.
- Do not commit it to GitHub.
- Do not paste it into public files.
- Do not share it with anyone else.
- Rotate or delete it if it is exposed.

Claude Code setup on macOS:
echo "export OPENAI_API_KEY='paste-your-key-here'" >> ~/.zshrc
# or
echo "export GOOGLE_API_KEY='paste-your-key-here'" >> ~/.zshrc
source ~/.zshrc

Then restart Claude Code or open a new terminal and invoke this skill again.

Full guide in this installed skill: references/claude-openai-api-key-setup.md
Repo guide: docs/claude-openai-api-key-setup.md
```

If the user declines to connect a provider or provide a key, offer to draft the carousel spec, copy, caption, alt text, and procedural renderer output, but make clear that production image generation needs a connected Claude image provider or API fallback.

Safe fallback message:

```text
I can still create a procedural draft pack without a connected image provider or API key. It will use the browser/Pillow renderer and bundled/procedural visuals, but it is not the production ImageGen carousel until a provider or API fallback is available.
```

## Claude / Local ImageGen Workflow

If running in Claude Desktop, Claude Code, or another non-Codex environment, prefer the end user's connected Claude image-generation provider when present. Otherwise use OpenAI first, then Google. Use the workflows documented in `references/claude-openai-api-key-setup.md`, `docs/openai-image-fallback.md`, and `docs/claude-openai-api-key-setup.md`.

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

Do not publish or schedule the post. For Threadify, generate Threadify-ready files and point users to `docs/threadify-staging.md` and `docs/threadify-draft-intake.md`.

## Profile Memory Rules

After the first successful carousel for a user, create or update the local creator profile described in `references/profile-memory.md`.

The profile must include, when available:

- Threads handle
- Niche and sub-niche
- Target audience
- Audience pain/desire language
- Tone and voice preferences
- Visual taste and brand colors
- Default CTA and offer details
- Proof assets or proof boundaries
- Risk appetite
- Preferred carousel length
- Style anti-patterns to avoid
- Winning hook categories
- Visual anchors
- CTA pressure defaults
- Prior performance summaries

Never store API keys, private credentials, or secrets in the profile.

For future carousels, load the profile first, reuse stable preferences, and still ask current-carousel questions for topic, goal, hook angle, proof, CTA, and any changed constraints.

## Reference Map

- `references/interview.md`: adaptive onboarding questions
- `references/style-calibration.md`: first-use style sample iteration and approval gate
- `references/threadify-draft-intake.md`: pasted text, markdown, and Threadify JSON intake
- `references/threads-virality-constitution.md`: corpus-backed Threads rules
- `references/hook-lab.md`: hook generation and scoring system
- `references/ai-critic-gate.md`: required structured red-team critique
- `references/pattern-bank.md`: public pattern bank and local private corpus summaries
- `references/larry-growth-loop.md`: research and learning-loop adaptation
- `references/visual-art-direction.md`: visual thesis, modes, and contact-sheet QA
- `references/performance-loop.md`: manual metrics ledger and diagnosis rules
- `references/larrybrain-research-note.md`: public source credit and adaptation note
- `references/template-families.md`: the 12 content-mechanic families
- `references/quality-rubric.md`: pre-render scoring gate
- `references/spec-authoring.md`: YAML spec rules and examples
- `references/profile-memory.md`: first-run profile creation and reuse rules
- `references/claude-openai-api-key-setup.md`: installed Claude API-key onboarding guide

## V1 Boundaries

Do not build or imply these in v1:

- Direct Threads publishing.
- Threadify auth/session automation.
- Browser staging automation.
- Background job scheduling or cloud dashboard.
- Remote profile sync or account system.
- Automatic platform metrics ingestion.
- Guaranteed virality claims.
