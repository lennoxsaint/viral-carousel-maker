# Image-generation provider and OpenAI API fallback

Codex is the preferred path for this skill because Codex users do not need to set an OpenAI API key for native image generation.

Claude Desktop and Claude Code users should use whichever image-generation provider/tool the end user has connected to Claude. If no provider is connected, use an OpenAI API key for the OpenAI Image API fallback. See [Claude image-generation provider and OpenAI API key setup](claude-openai-api-key-setup.md).

Use the API workflow when:

- Running outside Codex
- Using Claude Desktop or Claude Code without a connected image-generation provider
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

The renderer itself can create draft/procedural PNG carousels without API calls. In Claude Desktop and Claude Code, pause before the intended production image-generation workflow until a connected provider or `OPENAI_API_KEY` fallback is available.
