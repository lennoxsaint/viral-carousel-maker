# First-use style calibration

This gate is mandatory for a user's first production carousel unless an approved local `style_canon` already exists in `~/.viral-carousel-maker/profile.yaml`.

The goal is to make the carousel unmistakably theirs, not merely good-looking.

## Required behavior

1. Interview the user about visual identity, references, character/mascot rules, palette, typography, emotional tone, anti-examples, and what should make the carousel feel uniquely theirs.
2. Generate sample outputs before any final production pack. Use contact sheets, style boards, or 2-3 sample slides.
3. Ask for direct feedback and pull out concrete style rules from the user's reaction.
4. Iterate until the user explicitly approves the style direction.
5. Save the approved style canon into the local profile.
6. Use the approved canon on all future carousels, while still asking current-carousel content questions.

If the user asks to skip style calibration on first use, say:

```text
I cannot skip first-use style calibration because this skill is designed to make the carousel uniquely yours. I will keep it focused, but I need an approved visual direction before production.
```

## What to extract

- Handle and placement.
- Brand colors and image-derived palettes.
- Character, mascot, avatar, or object rules.
- Typography rules, including whether text should look typed, hand-lettered, handwritten, chalked, collaged, etc.
- Background system and texture.
- Emotional target: what the viewer should feel and why they would share.
- Virality target: comments, saves, shares, authority, offer clicks, or reach.
- Hook risk level.
- CTA and comment prompt style.
- Anti-patterns.
- Approved references and rejected references.

## Exemplar: Lennox/Fwed calibration arc

The Lennox/Fwed style was found through iterative calibration:

1. Start with Lennox's portrait colors: yellow, coral, blue, warm neutrals, dark ink.
2. Try broad creator-cartoon and editorial poster directions.
3. Reject generic, mid, overly template-like, and too-polished variants.
4. Keep the blackboard/whiteboard direction because it created the most thumbstop contrast.
5. Add raw human handwriting, mental models, and a cute storybook/fable arc.
6. Replace the generic idea creature with Fwed, Threadify's red bear mascot.
7. Lock Lennox character details: tight red t-shirt, thin black soft-octagonal glasses, silver chain, vertical rectangle pendant.
8. Add the blue signal-shadow hook move from the best white-background sample into the blackboard version.
9. Prefer comment-maximizing prompts such as "What is your post missing: tension, replies, or save value?"

This exemplar should guide the process, not be copied for every user. The public workflow must help each user reach their own distinct canon.

## Approved style profile fields

Store stable style results under these profile keys when available:

```yaml
style_canon:
  name: "short_style_name"
  reference_lock: true
  doc: "path/to/style-doc.md"
  production_renderer: "codex-native-imagegen or provider-imagegen"
  handle_position: "bottom-left"
  handle_text: "@handle"
  characters: {}
  signature_moves: []
imagegen_policy:
  codex: "Use native Codex ImageGen / ChatGPT ImageGen 2 for final PNGs."
  claude_provider_order:
    - "OpenAI Images API via OPENAI_API_KEY"
    - "Google image API via GOOGLE_API_KEY or GEMINI_API_KEY"
  code_renderers: "Draft fallback only unless explicitly accepted."
approved_reference_images: []
style_calibration:
  approved_at: "YYYY-MM-DDTHH:MM:SS+00:00"
  approved_summary: "plain English style lock"
  rejected_directions: []
```

Never store API keys, tokens, or private credentials in the profile.

## Approval gate

Before production generation, the answer must be yes to all:

- Did the user see at least one sample output?
- Did the user give concrete feedback?
- Did the user explicitly approve the final style direction?
- Is the approved style stored or ready to store in the profile?
- Does the prompt contract describe what to avoid, not just what to include?

Do not produce final ImageGen slides until the style gate passes.
