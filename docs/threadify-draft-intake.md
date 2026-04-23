# Threadify draft intake

The v1 intake system turns a draft into a human-editable carousel seed spec. It is not a publishing integration.

## Accepted inputs

- Pasted text via `--text`
- Local `.md`, `.markdown`, or `.txt` files
- Threadify-style `.json` exports or pasted JSON

## Text or markdown

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli intake examples/intake/threadify-draft.md --out output/threadify-seed.yaml
```

## JSON

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli intake examples/intake/threadify-draft.json --format json --out output/threadify-seed.yaml
```

## Best-effort JSON mapping

The intake command looks for common fields and continues when some are missing.

| Normalized field | Common JSON keys |
| --- | --- |
| Title / hook | `title`, `topic`, `hook`, `headline`, `name`, first slide title |
| Handle | `handle`, `threads_handle`, `author_handle`, `username`, `profile.handle`, `user.handle` |
| Draft text | `content`, `body`, `text`, `draft`, `notes`, `caption`, slide text |
| CTA | `cta`, `offer_url`, `url`, `link`, `cta_url` |

Missing fields become warnings in the seed spec. The skill still asks the mandatory interrogation questions before generation.

## Output

The command writes a valid starter YAML spec with:

- A default framework carousel structure
- The extracted handle/title/body where possible
- `intake.mapping: best-effort`
- `intake.warnings` for anything that needs confirmation

The seed is intentionally editable. The skill should still pressure-test audience, proof, belief shift, CTA, and visual direction before rendering.
