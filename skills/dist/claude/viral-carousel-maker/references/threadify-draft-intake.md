# Threadify draft intake

Use this when the user provides pasted draft copy, a markdown/text path, or Threadify JSON before asking the full interrogation gate.

## Supported inputs

- Pasted text via `--text`
- Local `.md`, `.markdown`, or `.txt`
- Threadify-style JSON via `.json` files or pasted JSON

## Command

```bash
viral-carousel intake examples/intake/threadify-draft.json --format json --out output/threadify-seed.yaml
```

The command creates a human-editable seed spec. It is not a final production spec until the mandatory interrogation, Hook Lab, critic gate, and QA pass.

## best-effort JSON mapping

Map common fields when present:

- Title: `title`, `topic`, `hook`, `headline`, `name`, or first slide title.
- Handle: `handle`, `threads_handle`, `author_handle`, `username`, `profile.handle`, or `user.handle`.
- Draft text: `content`, `body`, `text`, `draft`, `notes`, `caption`, or slide text.
- CTA: `cta`, `offer_url`, `url`, `link`, or `cta_url`.

If fields are missing, keep going and record warnings in `intake.warnings`. Ask Stage B follow-ups to fill gaps.
