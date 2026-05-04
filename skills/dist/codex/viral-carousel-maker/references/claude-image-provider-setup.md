# Claude image-generation provider setup

Use this guide when running Viral Carousel Maker in Claude Desktop or Claude Code.

Codex production runs must use native Codex ImageGen. Do not use API image generation from Codex.

## Provider order

1. Use a Claude-connected image-generation provider/tool when the end user has one configured.
2. If no provider is connected and production image generation is still necessary, use Gemini image generation as the emergency fallback.
3. If neither exists, pause before production image generation. Procedural browser/Pillow output is a draft-only fallback.

## Gemini key setup

For one terminal session:

```bash
export GOOGLE_API_KEY='paste-your-key-here'
```

For future terminal sessions on macOS with zsh:

```bash
echo "export GOOGLE_API_KEY='paste-your-key-here'" >> ~/.zshrc
source ~/.zshrc
```

Then open a new terminal or restart Claude Code before invoking the skill again.

Check that the variable exists without printing the secret:

```bash
test -n "$GOOGLE_API_KEY" && echo "GOOGLE_API_KEY is set"
```

## Secret safety

Treat API keys like passwords:

- Do not post them online.
- Do not commit them to GitHub.
- Do not put them in screenshots, docs, or public examples.
- Do not share them with other people.
- Store them in a password manager if you need to keep them.
- Rotate or delete them if you think they were exposed.

## What the skill should do if no provider is present

When running in Claude Desktop or Claude Code and no connected image provider or Gemini key is available, the skill should pause before production image generation and show this message:

```text
To use Viral Carousel Maker production image generation in Claude Desktop or Claude Code, connect an image-generation provider to Claude or provide a Gemini image API fallback.

Steps:
1. Use your Claude connector/settings to enable the image-generation provider you want this skill to use.
2. If no provider is available, create a Google/Gemini API key for image generation.
3. Copy the key once and store it safely.
4. Provide it to Claude as GOOGLE_API_KEY or GEMINI_API_KEY using your local environment, connector settings, or this current trusted local run.

Do not commit the key to GitHub, paste it into public files, or share it with anyone else.
```
