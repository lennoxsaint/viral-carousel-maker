# Public quickstart

Viral Carousel Maker is local-first. It creates Threads carousel image packs, captions, alt text, prompts, manifests, and QA reports. It does not publish to Threads or Threadify for you.

## Codex path

Codex is the preferred public path because it uses native ImageGen / ChatGPT ImageGen 2 production generation.

```bash
git clone https://github.com/lennoxsaint/viral-carousel-maker.git
cd viral-carousel-maker
bash scripts/install.sh
uv run python -m playwright install chromium
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli doctor --platform codex
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli render examples/specs/threads-shock-stat.yaml --out-dir output/threads-shock-stat --renderer imagegen
```

In Codex, native ImageGen is the only production path. Generate and return separate slide PNGs. Browser/Pillow rendering remains available for draft previews and QA fallbacks, but it is not the final production image path unless explicitly accepted.

## Claude Desktop or Claude Code path

Claude users need a connected image-generation provider or a Google/Gemini image API key for the emergency production fallback.

```bash
git clone https://github.com/lennoxsaint/viral-carousel-maker.git
cd viral-carousel-maker
bash scripts/install.sh
uv run python -m playwright install chromium
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli doctor --platform claude-code
```

If no connected provider is available and you need the Gemini emergency fallback, expose a Google/Gemini image API key:

```bash
echo "export GOOGLE_API_KEY='paste-your-key-here'" >> ~/.zshrc
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
- `contact_sheet.png` as a QA artifact

It does not mean automatic Threadify publishing, browser staging, or account login.

## Local profile memory

The skill can save stable creator preferences to:

```text
~/.viral-carousel-maker/profile.yaml
```

The profile stores preferences, not secrets. It should never contain API keys, tokens, passwords, or private credentials.

Profiles may also store approved reference images and identity reference images. When those fields exist, production prompts must carry the exact paths and likeness rules forward so installed skills do not drift back to generic avatars.
