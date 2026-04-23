# Pattern Bank And Private Corpus

The skill uses two pattern layers:

1. Public derived pattern bank in the repo.
2. Optional private local corpus summaries on the user's machine.

The public repo must never contain raw private posts, private performance logs, secrets, or API keys.

## Public derived pattern bank

Use this as the default prior:

- Observation before instruction.
- Short, certain hooks beat bloated teaching hooks.
- Statements beat homework questions unless the question is a sharp identity mirror.
- Long carousels need proof, story, or raw stakes.
- High-pressure CTAs are a reach tax unless the carousel has clearly earned the ask.

Reusable hook archetypes:

- `lie`: breaks a shared false belief.
- `identity_mirror`: makes the right viewer feel seen.
- `private_room_observation`: says the thing insiders say privately.
- `proof_receipt`: starts from evidence or lived result.
- `enemy_belief`: names the belief hurting the reader.

## Private local corpus import

Users can import their own examples locally:

```bash
viral-carousel corpus import /path/to/posts --local-only
```

The importer stores derived summaries under:

```text
~/.viral-carousel-maker/corpus/
```

It stores counts, rates, and derived rules. It does not store raw posts.

## How to use private summaries

If a private corpus summary exists, use it as a local prior for:

- Hook length
- Question-vs-statement preference
- Weak opener frequency
- Trigger-word risk
- Numeric hook frequency
- The user's own winning patterns

Do not quote or reproduce imported private posts unless the user explicitly provides that text in the current conversation.
