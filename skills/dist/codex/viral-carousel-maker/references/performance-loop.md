# Performance Loop

The skill should improve after each published carousel. Since v1 does not publish to Threads, performance tracking is manual and local.

## Metrics to capture

After the user posts manually, capture:

- Views
- Likes
- Replies
- Reposts
- Saves
- Clicks
- Conversions, if known
- Publish time
- Hook category
- Visual pack
- CTA type and pressure
- Body-slide count
- Notes about comments or audience reaction

## CLI commands

Add a record:

```bash
viral-carousel metrics add output/run-name/manifest.json --views 12000 --likes 300 --replies 40 --reposts 18 --saves 90 --clicks 12
```

Report recent performance:

```bash
viral-carousel metrics report --days 30
```

The report returns a `learning_summary` with:

- Winning hooks
- Weak hooks
- Best visual packs
- Best CTA pressure
- Best body-slide count
- Topics that earned saves

The local ledger lives under:

```text
~/.viral-carousel-maker/performance/
```

Never store API keys, platform tokens, private credentials, or raw private corpus dumps in the ledger.

## Diagnosis rules

- High views / low saves: the hook spread, but the value was too shallow.
- Low views / high saves: the value worked, but the hook or first slide failed reach.
- High clicks / low conversions: the offer, landing page, or promise is mismatched.
- Low everything: reset angle, hook, and value promise.

## Profile updates

After every 3-5 posts, update the local profile with:

- Winning hook categories
- Weak hook categories to avoid
- Visual anchors that seem to fit
- CTA pressure that performs best
- Audience phrases from replies
- Topics that earned saves

Keep the profile compact. It should guide future runs, not become a private data dump.
