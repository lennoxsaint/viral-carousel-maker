# Image-generation provider fallback

Codex production runs must use native Codex ImageGen / ChatGPT ImageGen 2.

Do not use API image generation from Codex for Viral Carousel Maker. The final Codex carousel output must be separate full-slide PNGs, not a single contact sheet.

## Non-Codex provider order

Use this order only outside Codex:

1. A connected native image-generation provider/tool.
2. Gemini image generation as an emergency fallback.
3. Browser/Pillow output only when the user explicitly accepts a draft fallback.

## Gemini emergency fallback

Set `GOOGLE_API_KEY`, `GEMINI_API_KEY`, or `GOOGLE_GENERATIVE_AI_API_KEY` only when a non-Codex production run has no connected provider and must still generate images.

```bash
export GOOGLE_API_KEY="..."
```

Never commit API keys to GitHub. If a key is exposed, revoke or rotate it from the provider dashboard.

## Renderer role

The renderer can create draft/procedural PNG carousels without API calls. In Codex, those are QA artifacts only unless the user explicitly accepts a draft fallback. In Claude Desktop and Claude Code, pause before production image generation until a connected provider or Gemini fallback is available.
