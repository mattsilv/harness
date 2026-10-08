# Frontend review

Applies when **Frontend review** is `on` in PROJECT_CONFIG.md.

## Setup once

- Create `docs/ui/templates.json` with `viewports` and `templates`, giving each distinct page template or materially different state a stable `id`, `title`, representative `path`, optional `parent`, and a visible `ready` selector; data-only variants share an entry.
- Wrap the configured capture command with the project's server startup and safe sample-data setup, using `--setup <module>` when a capture needs authentication or interaction.
- Keep captures reproducible with fixed data, fonts, and rendering environment, and wire `--check` into PR verification for UI, styles, layouts, assets, dependencies, or capture-setup changes.

Manifest shape (replace the example route and selector):

```json
{
  "viewports": {
    "desktop": { "width": 1440, "height": 900 },
    "mobile": { "width": 390, "height": 844 }
  },
  "templates": [
    { "id": "home", "title": "Home", "path": "/", "ready": "main" },
    { "id": "detail", "title": "Detail", "parent": "home", "path": "/items/example", "ready": "main" }
  ]
}
```

The optional setup module exports `prepare(context)` for authentication and
`ready(page, template)` for interactions and data readiness after navigation.
Keep credentials and browser session files out of source control.

## Capture and review

- Run the capture command after frontend changes, including copy that can affect fit, and commit the generated `docs/ui/README.md` sitemap and `docs/ui/screenshots/<id>/{desktop,mobile}.png` with the change.
- Give the configured reviewer the sitemap, affected images, intended change, and previous images for comparison before shipping.
- Check clear controls and hierarchy, consistent spacing and alignment, purposeful whitespace, readable text and contrast, usable mobile targets, and clipping or overflow.
- Prefer short, specific action labels and familiar words understandable around an eighth-grade reading level, keeping text needed to explain consequences or prevent mistakes.
- Fix findings by template ID and viewport, regenerate the batch, and have the reviewer verify fixes within the existing review-cycle limit.
- Link the sitemap and record the reviewed code commit and result in the PR; report unavailable capture or visual review as a blocker.

The CLI reuses one browser for the batch; `--check` compares without overwriting.
Image comparison allows one color level of rounding noise per channel.
These captures supply the screenshots required by AGENTS.md.
