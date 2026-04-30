# Claude image-generation provider and API key setup

Use this guide when running Viral Carousel Maker in Claude Desktop or Claude Code.

Codex users do not need an OpenAI API key for the preferred Codex-native ImageGen / ChatGPT ImageGen 2 path. Claude Desktop and Claude Code users should use whichever image-generation provider/tool the end user has connected to Claude. If no provider is connected, use `OPENAI_API_KEY` first, then a Google image API key when OpenAI is unavailable.

## Provider order

1. Use a Claude-connected image-generation provider/tool when the end user has one configured.
2. If no provider is connected, use the OpenAI Images API fallback with `OPENAI_API_KEY`.
3. If OpenAI is unavailable, use Google image API fallback with `GOOGLE_API_KEY`, `GEMINI_API_KEY`, or `GOOGLE_GENERATIVE_AI_API_KEY`.
4. If none exists, pause before production image generation. Procedural browser/Pillow output is a draft-only fallback.

Official OpenAI references:

- API key page: <https://platform.openai.com/api-keys>
- API key safety guide: <https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety>
- Where to find your API key: <https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key_>

## What an API key is

An API key is a secret password for software. It lets a tool call the OpenAI API using your OpenAI account.

Treat it like a credit card:

- Do not post it online.
- Do not commit it to GitHub.
- Do not put it in screenshots, docs, or public examples.
- Do not share it with other people.
- Store it in a password manager if you need to keep it.
- Rotate or delete it if you think it was exposed.

## Create an OpenAI API key

1. Open <https://platform.openai.com/api-keys>.
2. Sign in to your OpenAI account, or create one if needed.
3. If OpenAI asks you to finish account setup, billing, or verification, complete those steps.
4. Click the button to create a new secret key.
5. Name it something clear, such as `viral-carousel-maker`.
6. If OpenAI offers permissions, use the most limited permissions that still allow image generation. If unsure, start with the default key for testing and delete or rotate it later.
7. Copy the key immediately. OpenAI may only show it once.

## Give the key to Claude Code

The safest pattern is to make the key available as an environment variable named `OPENAI_API_KEY`.

For one terminal session:

```bash
export OPENAI_API_KEY='paste-your-key-here'
```

For future terminal sessions on macOS with zsh:

```bash
echo "export OPENAI_API_KEY='paste-your-key-here'" >> ~/.zshrc
source ~/.zshrc
```

Then open a new terminal or restart Claude Code before invoking the skill again.

Check that the variable exists without printing the secret:

```bash
test -n "$OPENAI_API_KEY" && echo "OPENAI_API_KEY is set"
```

## Give the key to Claude Desktop

Claude Desktop setups vary. Use the safest available local option first:

1. Put the key in the environment for the tool/server that Claude Desktop uses to run local commands.
2. If your Claude Desktop connector supports local environment variables, set `OPENAI_API_KEY` there.
3. If neither option is available, the skill may ask whether you are comfortable providing the key in the current Claude conversation for this run only.

Only provide the key in chat if you understand that you are sharing a secret with the Claude environment for this workflow. Do not ask Claude to save it in the repo.

## Local `.env` option

If you prefer a local file, create a private `.env` file in the repo root:

```bash
OPENAI_API_KEY=
# or
GOOGLE_API_KEY=
```

Paste your key after the equals sign in your private local file.

The repo ignores `.env` files by default. Do not remove that ignore rule.

## What the skill should do if no key is present

When running in Claude Desktop or Claude Code and no connected image provider, `OPENAI_API_KEY`, or Google image API key is available, the skill should pause before production image generation and show this message:

```text
To use Viral Carousel Maker production image generation in Claude Desktop or Claude Code, connect an image-generation provider to Claude, provide an OpenAI API key fallback, or provide a Google image API key fallback.

OpenAI fallback key page: https://platform.openai.com/api-keys

Steps:
1. Use your Claude connector/settings to enable the image-generation provider you want this skill to use.
2. If you prefer OpenAI as the fallback, sign in to OpenAI and create a new secret key.
3. If you prefer Google as the fallback, create a Google/Gemini API key for image generation.
4. Copy the key once and store it safely.
5. Provide it to Claude as OPENAI_API_KEY, GOOGLE_API_KEY, or GEMINI_API_KEY using your local environment, connector settings, or this current trusted local run.

Do not commit the key to GitHub, paste it into public files, or share it with anyone else.
```

## Rotate or delete a key

If a key is exposed, go back to <https://platform.openai.com/api-keys>, delete or revoke the exposed key, and create a new one.
