# OpenAI Image API fallback

Codex is the preferred path for this skill because Codex users do not need to set an OpenAI API key for native image generation.

Use the API fallback only when:

- Running outside Codex
- Using Claude Code without a native image tool
- Building repeatable generated assets from a terminal workflow

Install extras:

```bash
uv pip install -e ".[image-api]"
```

Set `OPENAI_API_KEY`:

```bash
export OPENAI_API_KEY="..."
```

Generate one optional asset:

```bash
viral-carousel generate-asset \
  --prompt "Textured white paper background with a subtle orange abstract shape, no text" \
  --out output/assets/background.png
```

The renderer itself does not need this fallback to create complete PNG carousels.

