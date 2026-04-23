# Visual Art Direction

Every carousel needs a visual thesis before rendering. A visual thesis is a short creative decision that explains mood, material, energy, and the one dominant visual idea.

Example:

```text
Textured white editorial paper, sharp navy/orange hierarchy, one proof-stat object per slide, sparse and confrontational.
```

## Design principles

- One dominant visual idea per slide.
- One dominant message per slide.
- Strong hierarchy: headline first, proof/body second, handle last.
- Use whitespace as structure.
- Use grids for comparisons, taxonomies, receipts, and proof.
- Use hero numbers when a stat is the point.
- Avoid generic cards unless the card itself carries meaning.
- Avoid decorative visuals that do not teach, prove, or create tension.
- Keep final readable text code-rendered, never baked into generated images.
- Keep visual assets text-free unless they are deliberately non-final background elements.
- Default to the browser renderer for final production. Use Pillow only as a fallback.
- Choose a named `design_pack` before rendering so the carousel has a coherent visual system.
- Generate image assets only when they carry meaning: proof, contrast, scene, object, texture, or emotional setting.

## Design packs

Use `design_pack` at the spec root:

- `editorial-paper`: textured paper, big hierarchy, navy/orange creator-education energy.
- `brutal-proof`: black/white/red, stark receipts, confrontational proof-first posts.
- `quiet-luxury`: refined minimalism for premium, advisory, finance, or high-trust topics.
- `founder-field-notes`: notebook/research energy for founder lessons and build-in-public insights.
- `photo-anchor`: image-led layouts where a visual object or scene carries the narrative.
- `data-lab`: grids, proof, numbers, and technical clarity.
- `myth-truth`: visual contrast between false belief and useful replacement.
- `template-marketplace`: clear modular layouts for reusable systems, checklists, and templates.

## Visual modes

Use `visual_mode` per slide when helpful:

- `editorial-paper`: textured paper, large type, restrained accents.
- `shock-stat`: one oversized stat or symbol as visual gravity.
- `proof-grid`: grid-based receipts, metrics, or examples.
- `myth-truth`: split old belief vs new belief.
- `taxonomy`: multiple labels organized as a map.
- `quiet-truth`: sparse, emotional, low-clutter.
- `receipt`: proof, audit, checklist, or source-feeling slide.
- `contrast-table`: bad/good, before/after, myth/truth.
- `field-note`: observational, handwritten/research-note energy.
- `photo-anchor`: image-led slide with one strong object/scene anchor.

## Contact-sheet QA

The renderer writes `contact_sheet.png`, `visual_qa.json`, and `visual_qa_report.md`. Review them before final delivery:

- Does slide 1 stop the eye immediately?
- Does the sequence alternate tension and payoff?
- Do all slides feel like the same brand world?
- Is there a clear rhythm of big/small, dense/sparse, proof/emotion?
- Are any slides visually redundant?
- Is the bottom-left handle visible on every slide?
- Would the carousel still make sense on a phone crop?
- Did machine QA pass text fit, contrast, crop safety, handle placement, dimensions, and slide count?
- If this is a makeover, did `visual_qa.makeover_scale.score` clear the requested bar?

If the contact sheet looks flat, fix the visual thesis or mode mix before regenerating.

## Hook slide standards (Threads plus thumbnail logic)

For slide 1, adapt strong thumbnail principles to Threads:

- One dominant claim, not a paragraph.
- A conflict word that creates tension (for example: not, wrong, dead, invisible, stop).
- One focal visual element that supports the claim.
- No visual overlap with readable text blocks.
- Clear hierarchy in under one second.

Use `strategy.hook_priority: high|extreme|thumbnail` when the user explicitly asks for maximum scroll-stop performance.

## Makeover Rule

When upgrading an older weak carousel, the new version must not be a polite rerender.

Require:

- A named non-default design pack when the old version looked generic.
- At least 3 distinct visual modes for 6+ slide carousels.
- A visible rhythm shift between hook, body, recap, and CTA.
- Stronger first-slide visual gravity than the old version.
- A `makeover_scale.score` of `8.5/10` or higher when the user asks for a large upgrade.
