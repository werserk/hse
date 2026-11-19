# Agents: how to make a case for hse.werserk.dev

This repo is public and every push to `main` deploys https://hse.werserk.dev. Build and kit reference: `README.md`.

## What a case is

A catalogue card is a **case** («кейс»). The items inside it are its **materials**: a **konspekt** (the text, its page) plus
slides, speaker mode, PDF, document, code, video. The case page shows a card and a switcher between the materials it has;
full schema of `entry.json`: README § Cases and materials.

```
content/<course>/<entry>/              published as
  entry.json   title, date, event,     
               summary (1 sentence)    
  notes.md     konspekt          →     /<course>/<entry>/          the material's page; written FIRST
  deck.html    presentation      →     /<course>/<entry>/slides/   our deck engine, made AFTER the konspekt
  site/        or a prebuilt one →     /<course>/<entry>/slides/   in a frame under the header (one of the two)
  widgets/     one-file widgets used by notes.md and deck.html
  <entry>.pdf  print of the deck (optional; CI prints one otherwise)
  *.pdf        downloads; labels via "downloads": {"Label": "file.pdf"} in entry.json
```

A document-only case (a PDF or PPTX) names it in `"file"`. It opens at `/doc/` under the same header.
An external link is `"type": "link", "url": …`. `"status": "planned"` shows a dashed card and builds nothing.
Until `notes.md` exists, the page shows `summary` and «Текстовый конспект готовится», and the build prints a warning.
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

   Open `/tmp/<entry>/index.html` and check:
   - the konspekt reads on its own, its contents work, and «▶ Презентация» opens the slides;
   - on the slides: «Конспект» goes back; PgDn/PgUp move slides, also after a click inside a widget; S opens the speaker view; O lists the slides;
   - the PDF has one page per slide.

   For regression scripts with Playwright, pass `screen=` larger than the viewport. Otherwise the page counts as fullscreen and hides the header.

5. **Publish.**
   - Commit only your entry folder and push to `main`; CI deploys in about a minute.
   - Check that `https://hse.werserk.dev/<course>/<entry>/` and `…/slides/` return 200 and look right.

## Ownership and limits

- A talk's thread owns its entry folder. `build.py`, `kit/`, `assets/`, `site.json` and this file belong to the
  hse.werserk.dev platform thread: ask it for changes instead of editing them.
- Content is in Russian; code, file names and docs for agents are in English.
- Everything pushed is public: no secrets, no private data, no unpublished third-party material.
- On a talk day, do not move or break a presentation URL without telling the presenter.
