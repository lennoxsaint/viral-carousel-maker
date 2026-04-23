# Gallery

This gallery proves the public v1 browser renderer can produce polished Threads-ready packs across niches and visual systems.

Each example includes:

- `hook.png`: first-slide proof of scroll-stop direction
- `contact_sheet.png`: full carousel pacing check
- `summary.json`: compact proof summary with slide count and QA status

The source proof for each showcased pack also lives in `examples/generated/<pack>/` and includes `manifest.json` and `qa_report.md`.

The gallery contains generated public demo assets only. It does not include private corpus posts, private performance logs, API keys, or raw user data.

## Examples

| Niche | Spec | Design pack | Hook preview | Contact sheet |
| --- | --- | --- | --- | --- |
| AI | `examples/specs/ai-framework.yaml` | `editorial-paper` | ![AI hook](assets/gallery/ai-framework/hook.png) | ![AI contact sheet](assets/gallery/ai-framework/contact_sheet.png) |
| Marketing | `examples/specs/marketing-map.yaml` | `data-lab` | ![Marketing hook](assets/gallery/marketing-map/hook.png) | ![Marketing contact sheet](assets/gallery/marketing-map/contact_sheet.png) |
| Coaching | `examples/specs/coaching-story.yaml` | `quiet-luxury` | ![Coaching hook](assets/gallery/coaching-story/hook.png) | ![Coaching contact sheet](assets/gallery/coaching-story/contact_sheet.png) |
| SaaS | `examples/specs/saas-data.yaml` | `data-lab` | ![SaaS hook](assets/gallery/saas-data/hook.png) | ![SaaS contact sheet](assets/gallery/saas-data/contact_sheet.png) |
| Local business | `examples/specs/local-business-debate.yaml` | `myth-truth` | ![Local business hook](assets/gallery/local-business-debate/hook.png) | ![Local business contact sheet](assets/gallery/local-business-debate/contact_sheet.png) |
| Wellness | `examples/specs/wellness-recap.yaml` | `quiet-luxury` | ![Wellness hook](assets/gallery/wellness-recap/hook.png) | ![Wellness contact sheet](assets/gallery/wellness-recap/contact_sheet.png) |
| Finance | `examples/specs/finance-list.yaml` | `quiet-luxury` | ![Finance hook](assets/gallery/finance-list/hook.png) | ![Finance contact sheet](assets/gallery/finance-list/contact_sheet.png) |
| Creator education | `examples/specs/education-quote.yaml` | `founder-field-notes` | ![Education hook](assets/gallery/education-quote/hook.png) | ![Education contact sheet](assets/gallery/education-quote/contact_sheet.png) |
| Career | `examples/specs/career-cta.yaml` | `brutal-proof` | ![Career hook](assets/gallery/career-cta/hook.png) | ![Career contact sheet](assets/gallery/career-cta/contact_sheet.png) |
| Design | `examples/specs/design-examples.yaml` | `template-marketplace` | ![Design hook](assets/gallery/design-examples/hook.png) | ![Design contact sheet](assets/gallery/design-examples/contact_sheet.png) |
| Fitness | `examples/specs/fitness-mistakes.yaml` | `brutal-proof` | ![Fitness hook](assets/gallery/fitness-mistakes/hook.png) | ![Fitness contact sheet](assets/gallery/fitness-mistakes/contact_sheet.png) |
| Productivity | `examples/specs/productivity-timeline.yaml` | `founder-field-notes` | ![Productivity hook](assets/gallery/productivity-timeline/hook.png) | ![Productivity contact sheet](assets/gallery/productivity-timeline/contact_sheet.png) |

## Regenerate Locally

```bash
PYTHONPATH=src uv run --with Pillow --with PyYAML --with jsonschema --with playwright python -m viral_carousel_maker.cli render examples/specs/ai-framework.yaml --out-dir output/gallery-check
```

Then inspect:

```text
output/gallery-check/contact_sheet.png
output/gallery-check/visual_qa.json
output/gallery-check/visual_qa_report.md
```

Validate committed gallery proof:

```bash
python scripts/public_proof.py --check-gallery
```

Regenerate full local showcase proof under `output/public-proof`:

```bash
PYTHONPATH=src python scripts/public_proof.py --run-showcase
```
