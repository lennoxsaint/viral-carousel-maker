# Image-generation provider and API fallback

Codex is the preferred path for this skill because Codex users do not need to set an OpenAI API key for native ImageGen / ChatGPT ImageGen 2 production generation.

Claude Desktop and Claude Code users should use whichever image-generation provider/tool the end user has connected to Claude. If no provider is connected, use an OpenAI API key first, then a Google image API key when OpenAI is unavailable. See [Claude image-generation provider and OpenAI API key setup](claude-openai-api-key-setup.md).

Use the API workflow when:

- Running outside Codex
- Using Claude Desktop or Claude Code without a connected image-generation provider
- Building repeatable generated assets from a terminal workflow

Install extras:

```bash
uv pip install -e ".[image-api]"
```

Set `OPENAI_API_KEY` for OpenAI:

```bash
export OPENAI_API_KEY="..."
```

Create or manage keys at <https://platform.openai.com/api-keys>.

Set `GOOGLE_API_KEY` or `GEMINI_API_KEY` for the Google fallback when OpenAI is unavailable:

```bash
export GOOGLE_API_KEY="..."
```

Never commit API keys to GitHub. If a key is exposed, delete or rotate it from the OpenAI API keys page.

Generate one optional asset:

```bash
viral-carousel generate-asset \
  --prompt "Textured white paper background with a subtle orange abstract shape, no text" \
  --out output/assets/background.png
```

The renderer itself can create draft/procedural PNG carousels without API calls. In Claude Desktop and Claude Code, pause before production image generation until a connected provider, `OPENAI_API_KEY`, or Google image API key fallback is available.
