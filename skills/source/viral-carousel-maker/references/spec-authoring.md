# Spec authoring

Specs are YAML files validated by `schemas/carousel.schema.json`.

Minimum shape:

```yaml
version: 1
title: "The carousel title"
handle: "@creator"
template_family: "framework"
aspect_ratio: "vertical"
theme:
  palette:
    text: "#05063f"
    accent: "#e84b05"
slides:
  - role: hook
    title: "Stop wasting your best ideas"
    subtitle: "A simple system for turning one insight into a full carousel."
  - role: body
    title: "Find the pain"
    body: "Start with what your audience is already frustrated by."
  - role: body
    title: "Name the shift"
    body: "Every saveable carousel moves the reader from confusion to clarity."
  - role: body
    title: "Make it concrete"
    body: "Use steps, examples, numbers, or contrast."
  - role: recap
    title: "TL;DR"
    bullets:
      - "Pain first"
      - "One idea per slide"
      - "CTA only after value"
  - role: cta
    title: "Follow"
    cta:
      type: follow
      description: "For more daily creator systems."
```

Body slide counts must be 3, 5, 7, or 9.

Keep final slide text concise. If the CTA is an offer, include `url`.

