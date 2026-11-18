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
kit/                               theme.css (tokens), deck.css/js (slides), frame.js (header over a site/document),
                                   notes.css/js (konspekt), starter/ (template for `build.py new`)
AGENTS.md                          how to make a material (workflow for agents)
assets/                            catalogue CSS/JS
```

URL of an entry: `https://hse.werserk.dev/<course>/<entry>/`.

## Materials

How to make one, the folder layout and the workflow: `AGENTS.md`. In short, every material is a konspekt
(`notes.md`, its page) plus resources under one header with «Конспект»: the presentation at `slides/`
(`deck.html`, or a prebuilt `site/` in a frame), a document at `doc/` (`"file"`), and downloads.

The home page shows one section per subject (`course.json`) with a card per material: a preview and the
title, nothing else.

```json
{"title": "…", "date": "2026-11-19", "event": "НИС АДНЖ", "summary": "One sentence.",
 "downloads": {"Заметки докладчика (PDF)": "talk-notes.pdf"}, "cover": 3}
```

Card preview: the build screenshots the presentation's first slide with a figure, the document's first page, or
the konspekt's first screen (needs Chrome and `pdftoppm`). Override it with `"cover": "cover.png"` (a file in the
entry folder) or `"cover": 3` (slide number).

## Konspekt

`notes.md` is Markdown with HTML allowed:
- `##`/`###` build the contents on the left;
- `<iframe class="widget" data-src="widgets/x.html">` embeds a widget (arrow keys stay in the widget);
- `<figure class="right" markdown>` floats a figure beside the text;
- `<details class="answer" markdown>` hides an answer.

The page is one self-contained file (also the offline copy). See `kit/starter/notes.md`.

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
