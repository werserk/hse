# hse.werserk.dev

Public catalogue of Maxim Kirilyuk's materials for HSE courses: talks, slides, notes, exam prep.
Every push to `main` builds and deploys the site with GitHub Pages (`.github/workflows/pages.yml`).
DNS: Cloudflare CNAME `hse` → `werserk.github.io` (DNS-only). Design note and history:
`genomics` workspace, `docs/interactive-materials.md`.

## Layout

```
site.json                          site title, intro, domain, style (paper | hse | coal)
content/<course>/course.json       {"title", "subtitle", "order"}
content/<course>/<entry>/entry.json
build.py                           site + deck builder (stdlib; Chrome for PDF)
kit/                               theme.css (tokens), deck.css, deck.js, starter/
assets/                            catalogue CSS/JS
```

URL of an entry: `https://hse.werserk.dev/<course>/<entry>/`.

## entry.json

The home page shows one section per subject (`course.json`) with a card per material; a card opens
the material page `/<course>/<entry>/`.

```json
{"title": "…", "type": "deck", "date": "2026-11-19", "event": "НИС АДНЖ",
 "summary": "One sentence.", "status": "planned"}
```

| type | folder holds | material page |
|---|---|---|
| `deck` | `deck.html`, `widgets/`, media, optional `<entry>.pdf` | the packed deck itself (menu: PDF, offline HTML, speaker view) |
| `site` | `site/` (prebuilt, has `index.html`), optional `*.pdf` | the site itself, copied as is |
| `pdf` | the file named in `"file"` | viewer with a download button |
| `pptx` | the file named in `"file"` | Office Online viewer + download (public URL needed) |
| `notes` | `index.md` (or `"file"`) + images | rendered Markdown + download |
| `link` | — (`"url"` in entry.json) | the external URL, new tab |

`"status": "planned"` shows a dashed «скоро» card and builds nothing. Remove it to publish.

## Decks

Write `deck.html` with one `<section class="slide">` per slide; see `kit/starter/deck.html`.

- `.step` elements appear one per → press (clicker-friendly).
- `<aside class="notes">` is shown only in the speaker view (key **S**, or the S button).
- Widgets: `<iframe class="widget" data-src="widgets/x.html" data-zoom="1.6">`. A widget is one HTML
  file styled only with bb inline-vis tokens (`var(--foreground)`, `var(--chart-1)`, `var(--brand)`, …),
  so the same file works in bb chat and on a slide. The packer inlines it with the theme.
- Local `<link rel="stylesheet">` and `<script src>` are inlined; other files (images, video) are copied.
- Keys: → / Space / PgDn next, ← / PgUp back, Home/End, F fullscreen, S speaker view; `#n` = slide n.

Build one deck (offline folder + PDF) and open it from disk:

```bash
python3 build.py deck content/genomics/runtime /tmp/runtime --pdf
```

The result `index.html` is self-contained except copied media; it is also the offline/flash-drive copy.
Commit `<entry>.pdf` next to `deck.html` when the CI print (different fonts) is not good enough.

## Site

```bash
python3 build.py site --out _site && python3 -m http.server -d _site 8000
```

Notes need `markdown` (`uv run --with markdown python build.py site`); CI installs it.
