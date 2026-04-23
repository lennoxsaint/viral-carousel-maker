# Larry-Inspired Growth Loop

LarryBrain/Larry Marketing is useful because it treats social content as an experiment loop, not a one-off asset. Viral Carousel Maker adopts the useful public principles while staying Threads-native and avoiding TikTok/Postiz automation in v1.

## Adopted principles

- Start with onboarding, not generation.
- Research competitors/trends when the user grants permission and tools are available.
- Save a reusable profile so future outputs get more consistent.
- Use visual prompt anchors instead of one-off vague prompts.
- Track performance by post so winners and losers become future strategy.
- Diagnose why a post failed instead of blindly making more.

## Not adopted in v1

- No direct Threads publishing.
- No Postiz automation.
- No TikTok account warmup flow.
- No RevenueCat integration.
- No scheduled posting bot.

## Optional research stage

If tools are available and the user gives permission:

1. Search 3-5 adjacent creators or competitors.
2. Note their strongest hook categories.
3. Identify repeated visual structures.
4. Identify obvious gaps or overused patterns.
5. Use findings to shape hook candidates and visual thesis.

If research tools are unavailable, continue with user-provided context and note the limitation.

## Feedback loop

After publishing manually, ask the user to paste metrics with:

```bash
viral-carousel metrics add output/run-name/manifest.json --views 12000 --likes 300 --replies 40 --reposts 18 --saves 90 --clicks 12
```

Then review recent patterns:

```bash
viral-carousel metrics report --days 30
```

Diagnostic rules:

- High views / low saves: value may be shallow.
- Low views / high saves: hook or first-slide problem.
- High clicks / low conversions: offer or landing-page mismatch.
- Low everything: reset angle, hook, and value promise.

Use these findings to update `~/.viral-carousel-maker/profile.yaml` with winning hook categories, visual anchors, CTA defaults, and anti-patterns.
