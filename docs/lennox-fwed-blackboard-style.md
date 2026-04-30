# Lennox/Fwed Blackboard Style Canon

This is Lennox Saint's personal Viral Carousel Maker style lock.

It is reference-locked, not pixel-deterministic. Full-slide image generation can be forced toward an approved canon through reference images, strict prompt contracts, and visual QA, but it cannot guarantee identical pixels across runs. The production rule is: regenerate until the result matches the canon closely enough to approve.

## Production Renderer

- Codex: use native Codex ImageGen / ChatGPT ImageGen 2 for final carousel PNGs.
- Claude Code / Claude Desktop: use OpenAI Images API when `OPENAI_API_KEY` is present, then Google image API when `GOOGLE_API_KEY`, `GEMINI_API_KEY`, or `GOOGLE_GENERATIVE_AI_API_KEY` is present.
- Browser and Pillow renderers are draft/spec-preview/QA fallbacks only. Do not treat code-rendered output as Lennox's final production style unless Lennox explicitly accepts a fallback draft.

## Canon Name

`lennox_fwed_midnight_blackboard_fable`

## Core Look

- Deep true-black chalkboard background: `#050505` / `#080808`.
- Chalk/storybook texture: dusty, smudged, hand-authored, uneven, warm.
- Accent palette from Lennox's portrait:
  - Golden yellow: `#FCBF12`
  - Coral red: `#E2665B`
  - Bright blue: `#4988F2`
  - Warm white chalk
  - Dark espresso ink
- Every carousel feels like a tiny illustrated fable plus a Threads growth mental model.
- The viewer should feel: "this is unbelievably cute, beautiful, emotionally true, and I need to share it."

## Character Canon

### Fwed

- Threadify mascot and emotional protagonist.
- Very cute small red bear, oversized rounded head, tiny soft paws, white muzzle, glossy black eyes, gentle innocent expression.
- Red/coral plush body translated from the pixel mascot into chalk/storybook texture.
- Fwed appears on every slide and carries the story.
- Never render Fwed as pixel-only in production.

### Lennox

- Gentle guide/teacher.
- Cute stylized Lennox with dark messy hair, moustache, warm clever expression, rounded storybook proportions.
- Tight fitted red t-shirt. No hoodie.
- Thin black metal glasses with soft octagonal / rounded-square lenses, delicate bridge, visible nose pads, slim temples, slight lens reflection.
- Thin silver chain necklace with a vertical rectangle pendant.
- Appears on 3-4 slides, not as the protagonist.

## Typography

- Titles: chunky readable hand-lettered chalk caps.
- Supporting text: visibly human handwriting, uneven baseline, imperfect spacing, raw chalk/marker pressure.
- Avoid fake-perfect script, typed-looking handwriting, and AI-clean lettering.
- Keep text short, crop-safe, and legible.

## Story Rules

- One slide must lead to the next through arrows, repeated props, and character movement.
- Use a recurring glowing yellow spark as the idea.
- Use simple mental-model objects: lever, bridge, pocket/vault, doors, loop.
- The story must create curiosity first, then deliver a moral.
- Preferred comment-maximizing final question: "What is your post missing: tension, replies, or save value?"

## Default Story Arc

Working title: `Fwed and the Idea Nobody Noticed`

Moral: tiny ideas grow when you make people feel, answer, and save them.

1. Hook: "Nobody saw Fwed's idea..." or "Nobody saw Fwed's idea because it was too nice."
2. Lever: tension gives people a reason to stop.
3. Bridge: replies give people a way into the conversation.
4. Pocket: save value makes the idea useful later.
5. Doors: one truth can enter through different formats.
6. Moral: small ideas grow when they help someone else.

## Slide 1 Signature Move

Slide 1 should include the white-version blue signal-shadow move:

- A big rough bright-blue signal aura behind Fwed and the tiny yellow idea spark.
- Fwed sits holding the spark, hopeful and a little sad.
- Lennox kneels beside him, pointing to a tiny blue lever.
- The image should be cute and emotionally immediate, but also high-contrast enough to stop a fast Threads scroll.

## Anti-Patterns

- Hoodie or loose top on Lennox.
- Wrong glasses.
- Missing silver chain or rectangle pendant.
- Fwed as pixel-only.
- Corporate vector art.
- Fake app UI.
- Stock icons.
- Generic creator carousel templates.
- Too-clean AI lettering.
- Unreadable scribbles.
- Watermarks or logos.
- Misspelled handle. The handle is exactly `@lennox_saint`.
