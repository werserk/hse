# hse.werserk.dev

Public catalogue of Maxim Kirilyuk's materials for HSE courses: talks, slides, notes, exam prep.
Every push to `main` builds and deploys the site with GitHub Pages (`.github/workflows/pages.yml`).
DNS: Cloudflare CNAME `hse` → `werserk.github.io` (DNS-only). Design note and history:
`genomics` workspace, `docs/interactive-materials.md`.

## Layout

```
site.json                          site title, domain, style (paper | hse | coal), footer
content/<course>/course.json       {"title", "full" (shown in the ? badge), "order"}
content/<course>/<entry>/entry.json
build.py                           site + deck builder (stdlib; Chrome for PDF)
kit/                               theme.css (tokens), deck.css/js (slides), notes.css/js (konspekt), starter/
assets/                            catalogue CSS/JS
```

URL of an entry: `https://hse.werserk.dev/<course>/<entry>/`.

## entry.json

The home page shows one section per subject (`course.json`) with a card per material: a preview and
the title, nothing else. A card opens the material page `/<course>/<entry>/`.

```json
{"title": "…", "type": "talk", "date": "2026-11-19", "event": "НИС АДНЖ", "status": "planned"}
```

| type | folder holds | material page |
|---|---|---|
| `talk`, `deck`, `notes` | `notes.md` (konspekt) and/or `deck.html` (slides), `widgets/`, media, optional `<entry>.pdf` | the konspekt; slides at `slides/` (button «▶ Презентация»). Without a konspekt the slides are the page |
| `site` | `site/` (prebuilt, has `index.html`), optional `*.pdf` | the site itself, copied as is |
| `pdf` | the file named in `"file"` | viewer with a download button |
| `pptx` | the file named in `"file"` | Office Online viewer + download (public URL needed) |
| `link` | — (`"url"` in entry.json) | the external URL, new tab |

`"status": "planned"` shows a dashed card and builds nothing. Remove it to publish.

Card preview: the build screenshots the first slide with a figure, the konspekt's first screen, or the
first PDF page (needs Chrome and `pdftoppm`). Override with `"cover": "cover.png"` (a file in the entry
folder) or `"cover": 3` (slide number).

## Konspekt first, slides second

The konspekt is the primary text: its own sections, prose, figures and widgets, written first. The
slides are a separate, shorter `deck.html` made from it afterwards; neither is generated from the other.
They share `widgets/`. See `kit/starter/` (`notes.md` + `deck.html`).

`notes.md` is Markdown with HTML allowed: `##`/`###` build the contents on the left;
`<iframe class="widget" data-src="widgets/x.html">` embeds a widget (arrow keys stay in the widget);
`<figure class="right" markdown>` floats a figure beside the text; `<details class="answer" markdown>`
hides an answer. The page is one self-contained file (also the offline copy).

## Decks

Write `deck.html` with one `<section class="slide">` per slide; see `kit/starter/deck.html`.

- `.step` elements appear one per → press (clicker-friendly).
- `<aside class="notes">` is shown only in the speaker view (key **S**, or «Докладчик» in the header).
- Widgets: `<iframe class="widget" data-src="widgets/x.html" data-zoom="1.6">`. A widget is one HTML
  file styled only with bb inline-vis tokens (`var(--foreground)`, `var(--chart-1)`, `var(--brand)`, …),
  so the same file works in bb chat and on a slide. The packer inlines it with the theme.
- Local `<link rel="stylesheet">` and `<script src>` are inlined; other files (images, video) are copied.
  Remote (CDN) scripts, styles and fonts are not inlined: the offline copy needs them bundled locally.
- Header: back to the course, title, slide counter (click or **O** = list of slides), Конспект, Докладчик,
  fullscreen, PDF, HTML. In fullscreen it hides and shows when the mouse reaches the top. `?bare` hides it.
- Keys: → / Space / PgDn next, ← / PgUp back, Home/End, F fullscreen, S speaker view, O slide list; `#n` = slide n.
  A focused widget forwards these keys to the deck, so a clicker keeps working after a click on a
  slider (arrows then move the slide, not the slider; drag it with the mouse).

Build one entry (konspekt + slides + PDF, as on the site) or only a deck, and open it from disk:

```bash
uv run --with markdown python build.py entry kit/starter /tmp/starter --pdf
python3 build.py deck content/genomics/runtime /tmp/runtime --pdf
```

The output folder must be new, empty, or an earlier output (it holds `.hse-build`).

The result `index.html` is self-contained except copied media; it is also the offline/flash-drive copy.
Commit `<entry>.pdf` next to `deck.html` when the CI print (different fonts) is not good enough.

## Site

```bash
python3 build.py site --out _site && python3 -m http.server -d _site 8000
```

A konspekt needs `markdown` (`uv run --with markdown python build.py site`); CI installs it.
