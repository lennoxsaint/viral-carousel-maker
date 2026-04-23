# Threadify staging

Viral Carousel Maker v1 does not publish to Threads and does not automate a browser.

Threadify-ready means the run produced:

- posting-order PNGs in `slides/`
- `caption.md`
- `alt_text.md`
- `manifest.json`
- `qa_report.md`
- `visual_qa.json`
- `contact_sheet.png`

The public-safe flow is:

1. Render the carousel pack.
2. Open Threadify manually.
3. Create a new carousel post.
4. Upload the PNGs from `slides/` in order.
5. Paste `caption.md`.
6. Keep `alt_text.md` nearby for accessibility text or platform notes.
7. Review the CTA slide before posting.

This keeps the public skill useful without requiring Threadify auth, browser automation, or direct platform publishing.

To start from a Threadify draft export before rendering, use `docs/threadify-draft-intake.md`.
