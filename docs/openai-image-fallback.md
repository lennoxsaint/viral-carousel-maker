# OpenAI Image API workflow

Codex is the preferred path for this skill because Codex users do not need to set an OpenAI API key for native image generation.

Claude Desktop and Claude Code users need an OpenAI API key for the intended OpenAI image-generation workflow. See [Claude and OpenAI API key setup](claude-openai-api-key-setup.md).

Use the API workflow when:

- Running outside Codex
- Using Claude Desktop or Claude Code
- Building repeatable generated assets from a terminal workflow

Install extras:

```bash
uv pip install -e ".[image-api]"
```

Set `OPENAI_API_KEY`:

```bash
export OPENAI_API_KEY="..."
```

Create or manage keys at <https://platform.openai.com/api-keys>.

Never commit API keys to GitHub. If a key is exposed, delete or rotate it from the OpenAI API keys page.

Generate one optional asset:

```bash
viral-carousel generate-asset \
  --prompt "Textured white paper background with a subtle orange abstract shape, no text" \
  --out output/assets/background.png
```

The renderer itself can create draft/procedural PNG carousels without API calls. In Claude Desktop and Claude Code, pause before the intended production image-generation workflow until `OPENAI_API_KEY` is available.
