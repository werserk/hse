# hse.werserk.dev

Public catalogue of Maxim Kirilyuk's materials for HSE courses: talks, slides, notes, exam prep.
Every push to `main` builds and deploys the site with GitHub Pages (`.github/workflows/pages.yml`).
DNS: Cloudflare CNAME `hse` → `werserk.github.io` (DNS-only). Design note and history:
`genomics` workspace, `docs/interactive-materials.md`.

## Layout

```
site.json                          site title, domain, style (paper | hse | coal), footer
content/<course>/course.json       {"title", "full" (shown in the ? badge), "order"}
content/<course>/<case>/entry.json  a case; schema below
build.py                           site + deck builder (stdlib; Chrome for PDF)
kit/                               theme.css (tokens), deck.css/js (slides), frame.js (header over a site/document),
                                   notes.css/js (konspekt), starter/ (template for `build.py new`)
AGENTS.md                          how to make a material (workflow for agents)
assets/                            catalogue CSS/JS
```

URL of a case: `https://hse.werserk.dev/<course>/<case>/`.

## Cases and materials

How to make a case, the folder layout and the workflow: `AGENTS.md`. A catalogue card is a **case** («кейс»): one folder `content/<course>/<case>/` with an `entry.json`. The things inside a case
are its **materials** (formats): konspekt, slides, speaker mode, PDF, document, code, video. The home page has one section per
subject (`course.json`) with a card per case: a preview and the title, with the number above it. A subject has no page of
its own: `/<course>/` redirects to its section on the home page.

A case lives at `/<course>/<case>/`: a branded card (cover, number, subject, title, date, status, files) and a switcher
between the materials the case has. Only the existing ones are shown. Each material has its own URL, and slides and documents
keep the full-window header with the same switcher:

| Material (tab) | Appears when | URL under `/<course>/<case>/` |
|---|---|---|
| Конспект (or «Обзор» without `notes.md`) | always | `/` |
| Слайды | `deck.html` or a prebuilt `site/` | `slides/` |
| Режим спикера | the deck has `<aside class="notes">` | `slides/?speaker` |
| PDF | CI prints the deck, or a committed `<case>.pdf`; or `"file"` is a PDF | `slides/<case>.pdf`, `doc/` |
| Документ | `"file"` is a PPTX or another document | `doc/` |
| Код | a `code/` folder (or `"code": "<folder>"`), or `"code": "https://…"` | `code/` (files with their text), or the link |
| Видео | `"video"` | `video/` (a player or an embed), or the link |

### `entry.json`

```json
{"number": "01", "title": "LAI: LOTER", "date": "2026-11-19", "event": "НИС АДНЖ", "status": "ready",
 "summary": "One sentence.", "cover": "cover.webp",
 "downloads": {"Заметки докладчика (PDF)": "talk-notes.pdf"},
 "links": {"Статья": "https://…"}, "video": "talk.mp4", "code": "https://github.com/…"}
```

| Field | Meaning |
|---|---|
| `title`, `summary` | card and page title; one sentence under it |
| `number` | `"01"`: above the title on the card and the page; keep it out of `title` |
| `date` | `YYYY-MM-DD`: shown as «19 ноября 2026»; cases are sorted by it, newest first |
| `event` | where it was presented; shown on the page when it differs from the subject |
| `status` | `ready` («готов»), `draft` («черновик»), or `planned` (dashed card, nothing is built). No status: no label |
| `cover` | a file in the folder, or a slide number; default: the deck's first figure slide, the document's first page, the konspekt's first screen |
| `notes` | konspekt file name if it is not `notes.md` |
| `file` | a PDF or PPTX shown at `doc/` |
| `downloads` | `{"Label": "file.pdf"}`; other `*.pdf` in the folder are listed too |
| `video` | a file in the folder, a direct `.mp4`/`.webm` URL, a YouTube or Rutube link (embedded), any other URL (opens in a new tab) |
| `code` | `https://…` link, or the name of a folder in the case (default `code/`; each file shown, big or binary ones for download) |
| `links` | `{"Label": "https://…"}`: extra links under the card |
| `type`, `url` | `"type": "link", "url": …`: the card is an external link; nothing is built |
| `tags` | free labels (not shown yet) |

## Konspekt

`notes.md` is Markdown with HTML allowed:
- `##`/`###` build the contents on the left;
- `<iframe class="widget" data-src="widgets/x.html">` embeds a widget (arrow keys stay in the widget);
- `<figure class="right" markdown>` floats a figure beside the text;
- `<details class="answer" markdown>` hides an answer.
- `$…$` / `$$…$$` are formulas, rendered to HTML+MathML at build time by the vendored KaTeX 0.19.1 (`kit/katex/`,
  run with `node`). The page inlines the KaTeX CSS; the fonts are served once per site from `/assets/katex/fonts/`
  (an absolute URL, so a downloaded copy uses them too; without network it falls back to local fonts).

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
- Header: back to the subject's section on the home page, title, the case's switcher (Конспект, Слайды, PDF, Код, …), slide
  counter (click or **O** = list of slides), Докладчик, fullscreen, HTML. In fullscreen it hides and shows when the mouse reaches the top. `?bare` hides it.
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
