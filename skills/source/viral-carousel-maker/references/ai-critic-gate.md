# AI Critic Gate

The AI critic gate is required before final rendering. It is a red-team pass, not a decoration.

Run it after the spec draft and before browser rendering.

## Critic job

The critic must inspect:

- Hook strength
- Old-belief-to-new-belief shift
- Specificity
- Proof integrity
- CTA pressure
- Visual thesis strength
- Slide density
- Saveability
- Shareability

The critic must not fabricate proof, invent stats, or override proof policy.

## Required output shape

Save or attach the critic result in the carousel spec under `critic`:

```json
{
  "verdict": "pass",
  "scores": {
    "hook_strength": 9,
    "belief_shift": 9,
    "specificity": 8.5,
    "proof_integrity": 9,
    "cta_fit": 8,
    "visual_thesis": 9,
    "slide_density": 8.5,
    "saveability": 9,
    "shareability": 8.5
  },
  "blockers": [],
  "revision_notes": [
    "Keep the hook as a contradiction, not a tutorial."
  ]
}
```

Valid verdicts are `pass`, `revise`, or `fail`.

The critic cannot pass if any score is below `8/10`.

## Revision loop

If the critic says `revise` or `fail`:

1. Name the exact blocker.
2. Revise the hook, copy, CTA, visual thesis, slide count, or proof language.
3. Run the critic again.
4. Only render when the critic verdict is `pass` and deterministic gates are clean.

## CLI validation

If the critic output is saved as JSON:

```bash
viral-carousel critic validate critic.json
```

The CLI validates shape only. It does not replace the actual AI critique.
