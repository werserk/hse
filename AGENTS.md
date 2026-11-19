# Agents: how to make a case for hse.werserk.dev

This repo is public and every push to `main` deploys https://hse.werserk.dev. Build and kit reference: `README.md`.

## What a case is

A catalogue card is a **case** («кейс»). The items inside it are its **materials**: a **konspekt** (the text, its page) plus
slides, speaker mode, PDF, document, code, video. The case's own page is the **overview**: the card, a tile per material
it has, and the konspekt read inline under them. Each material opens on its own page under the same header (`case_chrome()` in `build.py`, styles in `kit/head.css`) with the same switcher (Обзор · Конспект · Слайды …, PDF at `pdf/`); change the header there only, never per page type;
full schema of `entry.json`: README § Cases and materials.

```
content/<course>/<entry>/              published as
  entry.json   title, date, event,     
               summary (1 sentence)    
  overview.md  optional text     →     /<course>/<entry>/          above the tiles on the overview (a few paragraphs)
  notes.md     konspekt          →     /<course>/<entry>/notes/    the material's page; written FIRST
  deck.html    presentation      →     /<course>/<entry>/slides/   our deck engine, made AFTER the konspekt
  site/        or a prebuilt one →     /<course>/<entry>/slides/   in a frame under the header (one of the two)
  widgets/     one-file widgets used by notes.md and deck.html
  <entry>.pdf  print of the deck (optional; CI prints one otherwise)
  *.pdf        downloads; labels via "downloads": {"Label": "file.pdf"} in entry.json
```

A document-only case (a PDF or PPTX) names it in `"file"`. It opens at `/doc/` under the same header.
An external link is `"type": "link", "url": …`. `"status": "planned"` shows a dashed card and builds nothing.
Without `notes.md` the case has no «Конспект» tile; the overview shows what exists. Section anchors work on the overview itself
(`/<course>/<entry>/#anchor`); `notes/` stays as the standalone konspekt page.
Optional fields add materials: `"video"` (file or YouTube/Rutube link), `"code"` (a `code/` folder or a link), `"links"`, `"status"` (`ready`/`draft`).

## Workflow

1. **Start from the template.**

   ```bash
   python3 build.py new <course>/<entry> "Title" --date 2026-11-19 --event "НИС АДНЖ"
   ```

   This copies `kit/starter/`. Write the one-sentence `summary` in `entry.json`.

2. **Konspekt first** (`notes.md`). It is a text for a reader who did not hear the talk. It has its own sections,
   explanations, figures and widgets, and it is not a transcript of the slides or of the speaker's words.
   - `##` and `###` headings build the contents.
   - Cite sources.
   - Put widgets where interaction explains better than prose.
   - Formulas: `$…$` inline, `$$…$$` display, KaTeX syntax. They render at build time (needs `node`; the build
     fails on a TeX error and names the formula). A literal dollar outside code is `\$`.
   - The HTML blocks are listed in README § Konspekt.

3. **Presentation second** (`deck.html`): a shorter telling of the konspekt, using the same widgets.
   - Speaker text goes in `<aside class="notes">`.
   - Reveal points with `.step`.
   - A talk that already has its own engine goes in `site/` instead. Its keys must keep working inside the frame.

4. **Check locally**, through the pages a reader and a presenter use:

   ```bash
   uv run --with markdown python build.py entry content/<course>/<entry> /tmp/<entry> --pdf
   ```

   Open `/tmp/<entry>/index.html` (the overview) and check:
   - the tiles are the materials the case has; the konspekt (`notes/`) reads on its own and its contents work;
   - on the slides: «Конспект» and «Обзор» in the header go back; PgDn/PgUp move slides, also after a click inside a widget; S opens the speaker view; O lists the slides;
   - the PDF has one page per slide and opens at `pdf/` under the same header; the speaker tab (↗) opens a window that follows the slides.

   For regression scripts with Playwright, pass `screen=` larger than the viewport. Otherwise a desktop page counts as fullscreen (F11) and hides the header; touch screens never do.

5. **Publish as beta.**
   - A new case is beta: it goes to `/beta/<course>/<entry>/`, not to the home page (README § `entry.json`, `review`).
     Never set `"review": "reviewed"` yourself; the owner does that after reviewing the case.
   - Commit only your entry folder and push to `main`; CI deploys in about a minute.
   - Check that `https://hse.werserk.dev/beta/<course>/<entry>/` and `…/slides/` return 200 and look right.

## Decomposition and naming

- A case is a topic, not a file: it answers one question of the subject (a method, a model, a class of problems),
  usually one lecture or one paper. Cut along the course's own structure, never along assessments or homework.
- 3–6 chapters, each building on the previous; about 15–50 KB of konspekt. More than 7 loosely related chapters is
  several cases; under ~10 KB, merge into a neighbour.
- A case reads alone: question and prerequisites (links), chapters, traps and limits, sources. A derivation lives in
  one case; others recap in a paragraph and link.
- One readable body per case: the konspekt inline on the case page, or a short info page for a hub. Decks, PDFs,
  widgets and links are supporting materials in the row, never a second body. No PDF-only cases.
- At most one hub case per course: problem map (cue → case/chapter), mock tests, whole-course print sheets. It links,
  it does not derive. Only the hub may name an assessment in its title.
- Topics of the programme not written yet appear as `"status": "planned"` cards.
- Title: «Topic: qualifier», 2–6 words, the course's own term. No format, event, version or homework number in it.
- `summary`: the question the case answers, one sentence ≤ 160 chars, «Как…/Почему…», no formulas.
- Download labels say content and use, not file version. `event` is the occasion, never the course name again.
- Slugs are English topic names (`markov-chains`, not `kr2`). Reference examples: `genomics/loter`, `genomics/runtime`.

(Rationale and the per-course layout: `docs/cases-proposal.md`.)

## Ownership and limits

- A talk's thread owns its entry folder. `build.py`, `kit/`, `assets/`, `site.json` and this file belong to the
  hse.werserk.dev platform thread: ask it for changes instead of editing them.
- Content is in Russian; code, file names and docs for agents are in English.
- Everything pushed is public, beta included (it is only unlisted): no secrets, no private data, no unpublished third-party
  material, no homework solutions, no contacts.
- On a talk day, do not move or break a presentation URL without telling the presenter.
