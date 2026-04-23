# Profile memory

Use the first successful carousel to create a reusable local creator profile.

Profile path:

```bash
~/.viral-carousel-maker/profile.yaml
```

The profile improves future carousel generation by preserving stable creator preferences while still forcing current-carousel questions.

## When to write the profile

Write or update the profile after the first carousel passes QA.

Do not wait for the user to ask. Treat profile creation as part of the production workflow.

If a profile already exists, merge new stable preferences into it instead of overwriting useful details.

## What to store

Store stable creator information:

```yaml
handle: "@creator"
niche: "creator education"
sub_niche: "AI-assisted content systems"
audience: "solo creators selling digital products"
audience_pains:
  - "blank page anxiety"
  - "inconsistent posting"
audience_desires:
  - "saveable content ideas"
  - "clearer positioning"
tone:
  primary: "strategic but friendly"
  avoid:
    - "generic AI voice"
    - "hype without proof"
visual_preferences:
  styles:
    - "clean"
    - "high contrast"
    - "paper texture"
  colors:
    primary: "#05063f"
    accent: "#e84b05"
  avoid:
    - "busy gradients"
    - "tiny text"
cta_default:
  type: "follow"
  offer_url: ""
risk_appetite: 7
preferred_body_slide_count: 5
hook_preferences:
  winning_categories: []
  weak_categories: []
  banned_openers:
    - "How to"
    - "Here are"
visual_anchors:
  - "paper texture"
  - "large condensed headlines"
style_anti_patterns:
  - "generic AI voice"
  - "fake urgency"
cta_defaults:
  pressure: "soft"
  follow_copy: "Follow for sharper systems."
performance_summary:
  top_hooks: []
  best_visual_modes: []
  best_cta_pressure: "soft"
  last_reviewed_at: ""
proof_boundaries:
  - "do not invent stats"
  - "flag unsupported claims"
template_preferences:
  preferred:
    - "framework"
    - "mistakes"
  avoid: []
last_updated: "YYYY-MM-DD"
```

## What never to store

Never store:

- OpenAI API keys.
- Tokens.
- Passwords.
- Private credentials.
- Sensitive client data.
- Payment details.
- Anything the user explicitly says not to remember.

## How to use the profile later

On future carousels:

1. Load the profile first.
2. Tell the user which stable preferences you found.
3. Ask current-carousel questions anyway:
   - topic
   - desired outcome
   - current audience pain
   - proof for this claim
   - hook archetype and belief shift
   - CTA for this post
   - CTA pressure
   - any style changes
4. Use the profile to tailor tone, visuals, CTA defaults, hook categories, visual anchors, and risk level.
5. Update the profile only with stable new information.
6. If the user provides performance metrics, update only summarized learnings. Do not paste private raw comments or secrets into the profile.

## Profile write message

After writing or updating the profile, tell the user:

```text
I saved a local creator profile at ~/.viral-carousel-maker/profile.yaml so future carousels can reuse your handle, niche, tone, CTA defaults, visual preferences, and proof boundaries. I did not store API keys or secrets.
```
