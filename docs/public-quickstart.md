# Public quickstart

Viral Carousel Maker is local-first. It creates Threads carousel image packs, captions, alt text, prompts, manifests, and QA reports. It does not publish to Threads or Threadify for you.

## Codex path

Codex is the preferred public path because it does not require users to set `OPENAI_API_KEY`.

```bash
git clone https://github.com/lennoxsaint/viral-carousel-maker.git
cd viral-carousel-maker
uv run python -m playwright install chromium
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli doctor --platform codex
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli render examples/specs/threads-shock-stat.yaml --out-dir output/threads-shock-stat
```

In Codex, native image generation can be used for optional visual assets. Final readable text is still rendered by code so it stays crisp.

## Claude Desktop or Claude Code path

Claude users need an OpenAI API key for the intended image-generation workflow.

```bash
git clone https://github.com/lennoxsaint/viral-carousel-maker.git
cd viral-carousel-maker
uv run python -m playwright install chromium
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli doctor --platform claude-code
```

If `OPENAI_API_KEY` is missing, create one at:

```text
https://platform.openai.com/api-keys
```

Then expose it locally:

```bash
echo "export OPENAI_API_KEY='paste-your-key-here'" >> ~/.zshrc
source ~/.zshrc
```

Treat the key like a password. Do not commit it, paste it into public files, or store it in a profile.

## Threadify-ready output

Threadify-ready means the pack includes:

- `slides/*.png` in posting order
- `caption.md`
- `alt_text.md`
- `manifest.json`
- `qa_report.md`
- `visual_qa.json`
- `contact_sheet.png`

It does not mean automatic Threadify publishing, browser staging, or account login.

## Local profile memory

The skill can save stable creator preferences to:

```text
~/.viral-carousel-maker/profile.yaml
```

The profile stores preferences, not secrets. It should never contain API keys, tokens, passwords, or private credentials.
