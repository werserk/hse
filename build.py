#!/usr/bin/env python3
"""Build hse.werserk.dev.

  python3 build.py new <course>/<entry> "Title"                 start a material from kit/starter
  python3 build.py entry SRC_DIR OUT_DIR [--pdf]                 one material as on the site (konspekt + resources)
  python3 build.py site [--out _site] [--pdf] [--style paper]   catalogue + every material
  python3 build.py deck SRC_DIR OUT_DIR [--pdf] [--style paper]  one deck → offline HTML (+ PDF)

Stdlib only; `markdown` is used for notes entries when installed. PDF needs Chrome/Chromium
(CHROME env var, PATH, or the Playwright cache).
"""
import argparse, glob, html, json, os, re, shutil, subprocess, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KIT = ROOT / "kit"
CONTENT = ROOT / "content"


def read(p): return Path(p).read_text(encoding="utf-8")
def esc(s): return html.escape(str(s), quote=True)


def site_cfg():
    return json.loads(read(ROOT / "site.json"))


# ---------- deck packer ----------

WIDGET_HEAD = """<!doctype html><html data-style="{style}"><head><meta charset="utf-8"><base target="_blank">
<style>{theme}
body{{margin:0;background:transparent;color:var(--foreground);font:14px/1.45 var(--font-sans);zoom:{zoom};accent-color:var(--brand)}}</style></head><body>"""
WIDGET_TAIL = """<script>(()=>{const r=()=>parent.postMessage({type:'widget-height',h:Math.ceil(document.documentElement.scrollHeight)},'*');
new ResizeObserver(r).observe(document.documentElement);addEventListener('load',r);r();})();</script>{keys}</body></html>"""
# On slides a focused widget hands the deck's keys over, so a clicker keeps working after a click on a slider.
WIDGET_KEYS = """<script>(()=>{const nav=['PageDown','PageUp','ArrowRight','ArrowLeft','ArrowDown','ArrowUp',' ','Home','End','f','F','а','А','s','S','ы','Ы','o','O','щ','Щ','Escape'];
addEventListener('keydown',e=>{if(e.ctrlKey||e.metaKey||e.altKey)return;const t=e.target,typing=t.isContentEditable||/^(TEXTAREA|SELECT)$/.test(t.tagName)||(t.tagName==='INPUT'&&!/^(range|checkbox|radio|button)$/.test(t.type));
if(!nav.includes(e.key)||(typing&&!e.key.startsWith('Page')))return;e.preventDefault();parent.postMessage({type:'widget-key',key:e.key},'*');},true);})();</script>"""


def pack_widget(path, style, zoom, keys=True):
    src = re.sub(r"(?is)^\s*<!doctype[^>]*>", "", read(path))
    return WIDGET_HEAD.format(style=style, theme=read(KIT / "theme.css"), zoom=zoom) + src + WIDGET_TAIL.replace("{keys}", WIDGET_KEYS if keys else "")


class _Q:
    """Match adapter: group(2) is the widget path whichever quote style was used."""
    def __init__(self, m): self.m = m
    def group(self, i): return self.m.group(0) if i == 0 else self.m.group(1) if i == 1 else (self.m.group(2) or self.m.group(3))


MARK = ".hse-build"  # written into every output folder; only such folders (or empty ones) get replaced


def safe_out(src, out):
    """Refuse an output folder that overlaps the source or the repo, or holds files this tool did not write."""
    s, o = Path(src).resolve(), Path(out).resolve()
    if o == s or o in s.parents or s in o.parents or o == ROOT or o in ROOT.parents:
        sys.exit(f"refusing to write into {o}: it overlaps the source {s}")
    if o.exists() and (not o.is_dir() or (any(o.iterdir()) and not (o / MARK).exists())):
        sys.exit(f"refusing to replace {o}: not an earlier build output (no {MARK}); remove it yourself")


def fresh_out(out):
    if out.exists(): shutil.rmtree(out)


WIDGET = re.compile(r'<iframe\b[^>]*?\b(data-src=(?:"([^"]+)"|\'([^\']+)\'))[^>]*>')
LINK = re.compile(r'<link rel="stylesheet" href="(?!https?:|//)([^"]+)">')
SCRIPT = re.compile(r'<script src="(?!https?:|//)([^"]+)"></script>')


def inline_local(doc, src, style, where, keys=True):
    """Inline widgets (as srcdoc with the theme), local stylesheets and scripts; HTML comments stay untouched.
    Exits before anything is written when a referenced file is missing."""
    parts = re.split(r"(<!--.*?-->)", doc, flags=re.S)
    live = [p for p in parts if not p.startswith("<!--")]
    refs = [_Q(w).group(2) for p in live for w in WIDGET.finditer(p)] + [r for p in live for r in LINK.findall(p) + SCRIPT.findall(p)]
    missing = [r for r in refs if not (src / r).is_file()]
    if missing: sys.exit(f"{where}: file not found: {', '.join(missing)}")

    def widget(m):
        tag = m.group(0)
        zm = re.search(r'data-zoom=["\']([^"\']+)', tag)
        return tag.replace(m.group(1), f'srcdoc="{esc(pack_widget(src / m.group(2), style, zm.group(1) if zm else "1.6", keys))}"', 1)

    def inline(p):
        if p.startswith("<!--"): return p
        p = WIDGET.sub(lambda m: widget(_Q(m)), p)
        p = LINK.sub(lambda m: f"<style>{read(src / m.group(1))}</style>", p)
        return SCRIPT.sub(lambda m: f"<script>{read(src / m.group(1))}</script>", p)

    return "".join(inline(p) for p in parts)


def copy_media(src, out, skip=()):
    """Fresh output folder with the entry's media (sources and PDFs are handled separately).
    skip = names left out at the top level only (the code folder and video file have pages of their own)."""
    safe_out(src, out); fresh_out(out)
    base = shutil.ignore_patterns("deck.html", "*.md", "entry.json", "*.pdf", "site", ".*")
    shutil.copytree(src, out, ignore=lambda d, names: set(base(d, names)) | ({n for n in names if n in skip} if Path(d) == Path(src) else set()))
    (out / MARK).write_text("")


def pack_deck(src, out, style, pdf=False, home=None, name=None, has_pdf=False, title=None, chrome=None, skip=()):
    """deck.html → one offline HTML. `chrome` = the case's shared header (case_chrome); without a case a plain one with the
    title and a link to `home`."""
    src, out = Path(src), Path(out)
    doc = read(src / "deck.html")
    name = name or src.name
    m = re.search(r'<html\b[^>]*\bdata-style=["\']([^"\']+)', doc)
    style = m.group(1) if m else style
    if not m:  # before any inlining, so the <html> found is the page's own
        doc = re.sub(r"(?i)<html\b", f'<html data-style="{style}"', doc, count=1) if re.search(r"(?i)<html\b", doc) \
            else f'<!doctype html><html data-style="{style}">' + re.sub(r"(?is)^\s*<!doctype[^>]*>", "", doc)
    doc = inline_local(doc, src, style, src / "deck.html")
    copy_media(src, out, skip)
    metas = {"file": f"{name}.html", "pdf": f"{name}.pdf" if pdf or has_pdf else None}
    head = "".join(f'<meta name="deck:{k}" content="{esc(v)}">\n' for k, v in metas.items() if v)
    ttl = title or (re.search(r"(?is)<title>(.*?)</title>", doc) or [0, src.name])[1].strip()
    head += f'<template id="deck-chrome"><div class="cs-wrap">{chrome or plain_chrome(ttl, home or "/")}</div></template>\n'
    head += f"<style>{read(KIT / 'theme.css')}\n{read(KIT / 'head.css')}\n{read(KIT / 'deck.css')}</style>\n"
    if re.search(r"(?i)</head>", doc):
        doc = re.sub(r"(?i)</head>", lambda _: head + "</head>", doc, count=1)
    else:  # no </head>: keep doctype first and the charset inside the first 1024 bytes
        at = re.match(r"(?is)(?:\s|<!--.*?-->)*(<!doctype[^>]*>)?\s*(<html\b[^>]*>)?\s*(<head\b[^>]*>)?", doc).end()
        doc = doc[:at] + '<meta charset="utf-8">\n' + head + doc[at:]
    js = f"<script>{read(KIT / 'deck.js')}</script>\n"
    doc = re.sub(r"(?i)</body>", lambda _: js + "</body>", doc, count=1) if re.search(r"(?i)</body>", doc) else doc + js
    (out / "index.html").write_text(doc, encoding="utf-8")
    if pdf: print_pdf(out / "index.html", out / f"{name}.pdf")
    return out / "index.html"


CODE = re.compile(r"(```.*?```|~~~.*?~~~|`[^`\n]*`)", re.S)
MATH = re.compile(r"(?<!\\)\$\$(.+?)\$\$|(?<![\\$])\$(?![\s$])([^$\n]+?)(?<![\s\\])\$(?!\d)", re.S)


def katex(formulas):
    """[(tex, display)] → [html], rendered once at build time by the vendored KaTeX (kit/katex, needs node)."""
    node = shutil.which("node")
    if not node: sys.exit("formulas need node (KaTeX renders at build time)")
    r = subprocess.run([node, str(KIT / "katex" / "render.js")], input=json.dumps(formulas), capture_output=True, text=True)
    if r.returncode: sys.exit("KaTeX: " + r.stderr.strip())
    return json.loads(r.stdout)


def math_out(md):
    """Swap $…$ / $$…$$ (outside code) for tokens Markdown leaves alone; returns (md, restore(html))."""
    found = []
    def take(m):
        found.append((m.group(1) or m.group(2), m.group(1) is not None))
        return f"KATEXMATH{len(found) - 1}X"
    md = "".join(p if CODE.fullmatch(p) else MATH.sub(take, p).replace("\\$", "&#36;") for p in CODE.split(md))
    if not found: return md, lambda h: h
    rendered = katex(found)
    return md, lambda h: re.sub(r"KATEXMATH(\d+)X", lambda m: rendered[int(m.group(1))], h)


def katex_css(cfg):
    """KaTeX CSS for a page with formulas; the fonts live once per site in /assets/katex/fonts/ (absolute URL, so the
    downloaded copy uses them too; fully offline it falls back to local fonts)."""
    base = f"https://{cfg['domain']}/assets/katex/fonts/" if cfg.get("domain") else "/assets/katex/fonts/"
    return read(KIT / "katex" / "katex.min.css").replace("url(fonts/", f"url({base}")


def md_to_html(md):
    try:
        import markdown
        from markdown.extensions.toc import slugify_unicode
    except ImportError:
        sys.exit("konspekt needs the markdown package: uv run --with markdown python build.py ...")
    return markdown.markdown(md, extensions=["tables", "fenced_code", "attr_list", "md_in_html", "toc"],
                             extension_configs={"toc": {"slugify": slugify_unicode}})


def link(label, href, dl=False, attrs=""):
    """dl: False, True (keep the file name) or the name to save as."""
    d = "" if not dl else " download" if dl is True else f' download="{esc(dl)}"'
    return f'<a{attrs} href="{esc(href)}"{d}>{esc(label)}</a>'


def konspekt(src, style, md_name, up=""):
    """A Markdown file (+ HTML, widgets, formulas) → (body, contents [(level, id, text)]). `up` = prefix that turns links
    written for the case folder into links from the page's own folder (the konspekt page is notes/index.html)."""
    md, restore = math_out(read(src / md_name))
    body = restore(inline_local(md_to_html(md), src, style, src / md_name, keys=False))
    if up: body = re.sub(r'(\s(?:src|href|poster)=")(?!https?:|//|/|#|data:|mailto:|\.\./)([^"]+)"', lambda m: f'{m[1]}{up}{m[2]}"', body)
    toc = [(int(l), i, re.sub(r"<[^>]+>", "", t)) for l, i, t in re.findall(r'<h([23]) id="([^"]+)">(.*?)</h\1>', body)]
    return body, toc


MONTHS = "января февраля марта апреля мая июня июля августа сентября октября ноября декабря".split()
STATUS = {"ready": "готов", "draft": "черновик", "planned": "скоро"}


def ru_date(s):
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s or "")
    return f"{int(m[3])} {MONTHS[int(m[2]) - 1]} {m[1]}" if m and 1 <= int(m[2]) <= 12 else (s or "")


def tab_href(f, prefix): return f["href"] if f["ext"] else prefix + f["href"]


def tab_link(f, prefix, cls="", extra=""):
    new = f["ext"] or f.get("blank")  # an outside link, or a page for a second screen: a new tab
    on = ' class="%s"' % cls if cls else ""
    return (f'<a{on} href="{esc(tab_href(f, prefix))}"{" target=_blank rel=noopener" if new else ""}{extra}>'
            f'{esc(f["label"])}{" ↗" if new else ""}</a>')


def home_of(e, c):
    """The catalogue a case belongs to: the main page, or /beta/ until the owner has reviewed it."""
    b = e.get("base", "")
    return f"{b}/#{c['slug']}" if c["slug"] else f"{b}/"


def case_top(e, c): return f'<nav class="cs-top"><a href="{home_of(e, c)}">← Материалы</a></nav>'


def case_chrome(e, c, active, prefix):
    """The header shared by every page of a case except its overview card: back link, number · subject · date, title and the
    switcher between the materials. `prefix` leads from the page to the case folder. Slides and documents use it too."""
    cs = c["slug"]
    kick = " · ".join(x for x in [esc(e.get("number", "")),
                                  f'<a href="{home_of(e, c)}" title="{esc(c.get("full", ""))}">{esc(c["title"])}</a>' if cs else ""] if x)
    event = e.get("event") if e.get("event") != c["title"] else ""
    st = e.get("status")
    meta = "".join(f"<span>{esc(x)}</span>" for x in [ru_date(e.get("date", "")), event] if x) + \
           (f'<span class="cs-pill {esc(st)}">{esc(STATUS.get(st, st))}</span>' if st else "")
    tabs = "".join(tab_link(f, prefix, "cs-tab on" if f["key"] == active else "cs-tab", " data-speaker" if f["key"] == "speaker" else "") for f in e["formats"])
    return (f'{case_top(e, c)}<header class="cs-head"><p class="cs-kick">{kick}{meta}</p><h1>{esc(e["title"])}</h1></header>'
            f'<nav class="cs-tabs">{tabs}</nav>')


def plain_chrome(title, home="/"):
    """The same header for a deck or document that is not part of a case (build.py deck)."""
    return f'<nav class="cs-top"><a href="{esc(home)}">← Материалы</a></nav><header class="cs-head"><h1>{esc(title)}</h1></header>'


def case_page(e, c, active, main, style, cover, prefix="", side="", css="", js=""):
    """A page of a case. The overview (active="overview", at the case's URL) has the branded card: cover, number, subject,
    title, date, status, summary, and below it the choice of materials. A material's page has the shared header (case_chrome)."""
    cs = c["slug"]
    if active == "overview":
        course_url = home_of(e, c)
        kick = " · ".join(x for x in [esc(e.get("number", "")),
                                      f'<a href="{course_url}" title="{esc(c.get("full", ""))}">{esc(c["title"])}</a>' if cs else ""] if x)
        event = e.get("event") if e.get("event") != c["title"] else ""
        meta = "".join(f"<span>{esc(x)}</span>" for x in [ru_date(e.get("date", "")), event] if x)
        st = e.get("status")
        pill = f'<span class="cs-pill {esc(st)}">{esc(STATUS.get(st, st))}</span>' if st else ""
        lead = f'<p class="cs-lead">{esc(e["summary"])}</p>' if e.get("summary") else ""
        cv = f'<span class="cs-cv"><img src="{esc(prefix + cover)}" alt="" onerror="this.parentNode.remove()"></span>' if cover else ""
        head = case_top(e, c) + (f'<header class="cs-card">{cv}<div class="cs-info"><p class="cs-kick">{kick}</p><h1>{esc(e["title"])}</h1>'
                              f'<div class="cs-meta">{meta}{pill}</div>{lead}</div></header>')
    else:
        head = case_chrome(e, c, active, prefix)
    return f"""<!doctype html><html lang="ru" data-style="{style}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(e["title"])}{" — " + esc(c["title"]) if cs else ""}</title>
<script>if(/[?&]bare(&|$)/.test(location.search))document.documentElement.classList.add("bare")</script>
<script>/* in the head: a widget reports its height once it loads, possibly before the end of the page is parsed */
addEventListener("message",e=>{{if(e.data?.type!=="widget-height")return;for(const f of document.querySelectorAll("iframe.widget"))if(f.contentWindow===e.source)f.style.height=e.data.h+"px"}})</script>
<style>{read(KIT / 'theme.css')}
{read(KIT / 'head.css')}
{read(KIT / 'case.css')}{css}</style></head>
<body class="cs"><div class="cs-wrap">{head}
<div class="cs-body{" has-side" if side else ""}">{side}<main class="cs-main">{main}</main></div></div>{js}</body></html>"""


def file_size(f):
    kb = Path(f).stat().st_size / 1024
    return f"{kb / 1024:.1f} МБ".replace(".", ",") if kb >= 1024 else f"{kb:.0f} КБ"


def plural(n, forms):
    """1 слайд, 2 слайда, 5 слайдов."""
    k = n % 100
    return f"{n} " + (forms[2] if 11 <= k <= 14 else forms[0] if n % 10 == 1 else forms[1] if 2 <= n % 10 <= 4 else forms[2])


def overview_main(e, p, dest, toc, widgets, text=""):
    """The overview's body: the case's own text (overview.md), the choice of materials (each with what it holds),
    the konspekt's contents, files and links."""
    d = e["dir"]; info = {}
    if p["md"]:
        secs = sum(1 for l, _, _ in toc if l == 2)
        info["notes"] = "Текст с рисунками" + (f" и виджетами: {plural(widgets, ('виджет', 'виджета', 'виджетов'))}" if widgets else "") + \
                        (f" · {plural(secs, ('раздел', 'раздела', 'разделов'))}" if secs else "")
    if p["deck"]:
        slides = re.split(r'<section\b[^>]*class="[^"]*\bslide\b', read(d / "deck.html"))[1:]
        info["slides"] = f"Презентация · {plural(len(slides), ('слайд', 'слайда', 'слайдов'))}"
        noted = sum(1 for sl in slides if re.search(r'<aside\b[^>]*class="[^"]*\bnotes\b', sl))
        info["speaker"] = f"Заметки докладчика и таймер · к {noted} из {len(slides)} слайдов" if noted != len(slides) else f"Заметки докладчика и таймер · {plural(noted, ('слайд', 'слайда', 'слайдов'))}"
    elif p["site"]: info["slides"] = "Презентация"
    pdf = dest / "slides" / p["dpdf"] if p["deck_pdf"] else dest / p["doc"] if p["doc"] and p["doc"].lower().endswith(".pdf") else None
    if pdf and pdf.exists():
        info["pdf"] = "Печатная версия · " + file_size(pdf)
    if p["doc"]: info["doc"] = "Документ · " + Path(p["doc"]).suffix.lstrip(".").upper()
    if p["code"]: info["code"] = "Внешний репозиторий" if p["code"]["ext"] else "Исходники · " + plural(len([x for x in p["code"]["dir"].rglob("*") if x.is_file()]), ("файл", "файла", "файлов"))
    if p["video"]: info["video"] = {"file": "Видеофайл", "embed": "Запись, встроенная на страницу", "link": "Ссылка на видео"}[p["video"]["kind"]]
    mats = [f for f in e["formats"] if f["key"] != "overview"]
    tiles = "".join(f'<a class="mt{" main" if i == 0 else ""}" href="{esc(tab_href(f, ""))}"{" target=_blank rel=noopener" if f["ext"] or f.get("blank") else ""}><b>{esc(f["label"])}{" ↗" if f["ext"] or f.get("blank") else ""}</b>'
                    f'<span>{esc(info.get(f["key"], ""))}</span></a>' for i, f in enumerate(mats))
    out = f'<div class="ov-text nt-body">{text}</div>' if text else ""
    out += f'<h2 class="cs-h2">Материалы</h2><div class="mts">{tiles}</div>' if tiles else '<p class="empty">Материалов пока нет.</p>'
    if p["md"] and sum(1 for l, _, _ in toc if l == 2) > 1:
        out += '<h2 class="cs-h2">Содержание конспекта</h2><ul class="ov-toc">' + "".join(f'<li><a href="notes/index.html#{esc(i)}">{t}</a></li>' for l, i, t in toc if l == 2) + "</ul>"
    files = [(label, f, True) for label, f in e["files"].items()] + ([("HTML (конспект, офлайн)", "notes/index.html", f"{e['slug']}.html")] if p["md"] else [])
    files = [link(*x) for x in files] + [link(label + " ↗", url, attrs=' target="_blank" rel="noopener"') for label, url in (e.get("links") or {}).items()]
    if files: out += f'<h2 class="cs-h2">Файлы и ссылки</h2><p class="cs-files">{"".join(files)}</p>'
    return out


FULL_SVG = ('<svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.6">'
            '<path d="M1 5V1h4M9 1h4v4M13 9v4H9M5 13H1V9"/></svg>')


def pack_frame(out, style, title, src, chrome, label="", links=()):
    """A resource that is not our deck (a prebuilt site, a PDF, a PPTX viewer) inside the case's shared header (`chrome`):
    a bar with what it is and its downloads, the resource below, F / ⛶ for fullscreen. links = [(label, href, download)]."""
    acts = "".join(link(*x) for x in links) + f'<button type="button" data-a="full" title="Во весь экран (F)">{FULL_SVG}<span>Во весь экран</span></button>'
    (out / "index.html").write_text(f"""<!doctype html><html lang="ru" data-style="{style}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>
<style>{read(KIT / 'theme.css')}
{read(KIT / 'head.css')}
{read(KIT / 'deck.css')}</style></head>
<body class="deck-body frame"><div class="cs-wrap">{chrome}</div>
<div class="fr-box"><div class="fr-bar"><b>{esc(label)}</b><span class="sp"></span>{acts}</div>
<iframe class="fr-view" data-src="{esc(src)}" title="{esc(title)}" allow="fullscreen" allowfullscreen></iframe></div>
<script>{read(KIT / 'frame.js')}</script></body></html>""", encoding="utf-8")


def find_chrome():
    cands = [os.environ.get("CHROME")] + [shutil.which(n) for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")]
    cands += sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome")), reverse=True)
    return next((c for c in cands if c and os.path.exists(c)), None)


def print_pdf(page, pdf):
    chrome = find_chrome()
    if not chrome: sys.exit("PDF: no Chrome/Chromium found (set CHROME)")
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                    "--run-all-compositor-stages-before-draw", "--virtual-time-budget=8000",
                    f"--print-to-pdf={pdf}", page.resolve().as_uri()], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("pdf", pdf)


def shoot(url, png):
    """Screenshot a 1280×720 page into a 640×360 PNG; False when there is no Chrome."""
    chrome = find_chrome()
    if not chrome: return False
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--window-size=1280,720",
                    "--force-device-scale-factor=0.5", "--virtual-time-budget=5000", f"--screenshot={png}", url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return png.exists()


def figure_slide(page):
    """Number of the first slide that shows a figure (widget, chart, picture), else 1."""
    slides = re.split(r'<section\b[^>]*class="[^"]*\bslide\b', read(page))[1:]
    return next((i + 1 for i, sl in enumerate(slides) if re.search(r"<(iframe|svg|img|video|canvas)\b", sl.split("</section>")[0])), 1)


def make_cover(e, dest, konspekt=False):
    """Card preview: "cover" in entry.json (a file, or a slide number), else the presentation's first figure slide,
    the first page of the document, or (konspekt=True, once the page is built) the konspekt's first screen."""
    d, cov = e["dir"], e.get("cover")
    dest.mkdir(parents=True, exist_ok=True)
    if isinstance(cov, str):
        name = "cover" + Path(cov).suffix
        shutil.copy(d / cov, dest / name); return name
    png, deck, site, doc = dest / "cover.png", dest / "slides" / "index.html", dest / "slides" / "site" / "index.html", e.get("file")
    if site.exists(): shoot(f"{site.resolve().as_uri()}#{cov or figure_slide(site)}", png)
    elif deck.exists(): shoot(f"{deck.resolve().as_uri()}?bare#{cov or figure_slide(deck)}", png)
    elif doc and doc.lower().endswith(".pdf") and shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-png", "-singlefile", "-f", "1", "-l", "1", "-scale-to-x", "640", "-scale-to-y", "-1",
                        str(d / doc), str(dest / "cover")], check=False)
    elif konspekt and (dest / "notes" / "index.html").exists(): shoot((dest / "notes" / "index.html").resolve().as_uri() + "?bare", png)
    return png.name if png.exists() else None


# ---------- cases: what a case has, its catalogue card and pages ----------
# A case is a folder content/<course>/<case>/ (entry.json). Its page is the overview; its materials (formats) are found
# from the folder and entry.json:  Конспект notes.md (→ notes/) · Слайды deck.html or site/ · Режим спикера (deck has <aside class="notes">) · PDF (print of the deck,
#   or "file" is a PDF) · Документ ("file", PPTX etc.) · Код (code/ folder or "code") · Видео ("video").
# The page and the card show only the formats that exist.

URL = re.compile(r"https?://")
VIDEO_EXT = (".mp4", ".webm", ".ogv", ".mov")


def case_code(e):
    """{"href", "ext", "dir"?}: "code" is a URL, a folder name in the case, or absent (then a code/ folder, if any)."""
    d, c = e["dir"], e.get("code")
    if isinstance(c, str) and URL.match(c): return {"href": c, "ext": True}
    name = c if isinstance(c, str) else "code"
    if (d / name).is_dir() and (c or any(not x.name.startswith(".") for x in (d / name).rglob("*") if x.is_file())): return {"href": "code/index.html", "ext": False, "dir": d / name, "name": name}
    if c: sys.exit(f"{d}: code folder not found: {c}")


def case_video(e):
    """{"kind": file|embed|link, "src"|"href", "href", "ext"}: a file in the case, a YouTube or Rutube link (embedded),
    a direct video URL, or any other link (opened in a new tab)."""
    d, v = e["dir"], e.get("video")
    if not v: return None
    if not URL.match(v):
        if not (d / v).is_file(): sys.exit(f"{d}: video not found: {v}")
        return {"kind": "file", "src": v, "href": "video/index.html", "ext": False}
    yt = re.search(r"(?:youtube\.com/watch\?(?:[^#]*&)?v=|youtu\.be/)([\w-]{6,})", v)
    rt = re.search(r"rutube\.ru/video/([0-9a-f]{32})", v)
    if yt: return {"kind": "embed", "src": f"https://www.youtube-nocookie.com/embed/{yt[1]}", "href": "video/index.html", "ext": False}
    if rt: return {"kind": "embed", "src": f"https://rutube.ru/play/embed/{rt[1]}", "href": "video/index.html", "ext": False}
    if v.lower().split("?")[0].endswith(VIDEO_EXT): return {"kind": "file", "src": v, "href": "video/index.html", "ext": False}
    return {"kind": "link", "href": v, "ext": True}


def inspect_case(e, pdf):
    """Everything the case has, from its folder and entry.json: sources, downloads and the ordered formats
    [{"key", "label", "href", "ext"}]; exits on a missing file."""
    d, slug = e["dir"], e["slug"]
    md = next((n for n in (e.get("notes"), "notes.md") if n and (d / n).is_file()), None)
    deck, site, doc = (d / "deck.html").is_file(), (d / "site" / "index.html").is_file(), e.get("file")
    if deck and site: sys.exit(f"{d}: one presentation per case: deck.html or site/, not both")
    if doc and not (d / doc).is_file(): sys.exit(f"{d}: file not found: {doc}")
    dpdf = f"{slug}.pdf"
    committed = deck and (d / dpdf).exists()  # a locally printed PDF wins over a CI print
    deck_pdf = deck and (pdf or committed)
    files = dict((e.get("downloads") or {}).items())  # label → file in the case folder
    files.update({p.name: p.name for p in sorted(d.glob("*.pdf")) if p.name not in files.values() and p.name != doc
                  and not (deck_pdf and p.name == dpdf)})
    for f in files.values():
        if not (d / f).is_file(): sys.exit(f"{d}: download not found: {f}")
    code, video = case_code(e), case_video(e)
    fm = [("overview", "Обзор", "index.html", False)]
    if md: fm.append(("notes", "Конспект", "notes/index.html", False))
    if deck or site: fm.append(("slides", "Слайды", "slides/index.html", False))
    if deck and re.search(r'<aside\b[^>]*class="[^"]*\bnotes\b', read(d / "deck.html")):
        fm.append(("speaker", "Режим спикера", "slides/index.html?speaker", False, True))  # for a second screen: a new tab
    if deck_pdf: fm.append(("pdf", "PDF", "pdf/index.html", False))
    if doc: fm.append(("doc", "PDF" if doc.lower().endswith(".pdf") and not deck_pdf else "Документ", "doc/index.html", False))
    if code: fm.append(("code", "Код", code["href"], code["ext"]))
    if video: fm.append(("video", "Видео", video["href"], video["ext"]))
    return {"md": md, "deck": deck, "site": site, "doc": doc, "dpdf": dpdf, "committed": committed, "deck_pdf": deck_pdf,
            "files": files, "code": code, "video": video,
            "formats": [dict(zip(("key", "label", "href", "ext", "blank"), f)) for f in fm]}


# ---------- catalogue: sections by subject, case cards ----------

REVIEW = ("beta", "reviewed")
BETA_HEAD = '<meta name="robots" content="noindex, nofollow">'
BETA_NOTE = ('<div class="beta-note" role="note" style="position:fixed;left:12px;bottom:12px;z-index:2147483647;'
             'padding:6px 12px;border-radius:999px;background:#b3261e;color:#fff;font:600 13px/1.2 system-ui,sans-serif;'
             'box-shadow:0 2px 8px rgba(0,0,0,.25);pointer-events:none">β · не проверено автором</div>')


def mark_beta(root):
    """Every page under /beta/: noindex, and a banner that the author has not reviewed it (not inside a prebuilt site's frame)."""
    for f in root.rglob("*.html"):
        doc = read(f)
        if "noindex" not in doc:  # a fragment without <head> (a copied widget) gets the tag first, in its implied head
            doc = re.sub(r"(?i)<head\b[^>]*>", lambda m: m[0] + BETA_HEAD, doc, count=1) if re.search(r"(?i)<head\b", doc) else BETA_HEAD + doc
        if not re.search(r"/(site|widgets)/", "/" + f.relative_to(root).as_posix()) and "beta-note" not in doc:
            doc = re.sub(r"(?i)<body\b[^>]*>", lambda m: m[0] + BETA_NOTE, doc, count=1)
        f.write_text(doc, encoding="utf-8")


def load_content():
    courses = []
    for cdir in sorted(p for p in CONTENT.iterdir() if (p / "course.json").exists()):
        c = json.loads(read(cdir / "course.json")); c["slug"] = cdir.name
        c["entries"] = []
        for edir in sorted(p for p in cdir.iterdir() if (p / "entry.json").exists()):
            e = json.loads(read(edir / "entry.json")); e["slug"] = edir.name; e["dir"] = edir; e["course"] = c["slug"]
            e["review"] = e.get("review", "beta")  # only the owner sets "reviewed"; until then the case lives under /beta/
            if e["review"] not in REVIEW: sys.exit(f"{edir}/entry.json: review must be one of {', '.join(REVIEW)}")
            e["base"] = "" if e["review"] == "reviewed" else "/beta"
            if e.get("status") != "planned":
                e["href"] = e["url"] if e.get("type") == "link" else f"{e['base']}/{c['slug']}/{edir.name}/"
            c["entries"].append(e)
        c["entries"].sort(key=lambda e: e.get("date", ""), reverse=True)
        courses.append(c)
    courses.sort(key=lambda c: (c.get("order", 99), c["slug"]))
    return courses


def page(cfg, title, body, style, cls="", head=""):
    return f"""<!doctype html><html lang="ru" data-style="{style}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>{head}
<link rel="stylesheet" href="/assets/theme.css"><link rel="stylesheet" href="/assets/site.css"></head>
<body class="{cls}">{body}</body></html>"""


def card(e):
    """A card is a preview and the title, with the case's number above it (owner, 2026-11-18, 2026-11-19)."""
    cov = f'<img src="{esc(e.get("base", ""))}/{esc(e["course"])}/{esc(e["slug"])}/{esc(e["cover_name"])}" alt="" loading="lazy">' if e.get("cover_name") else ""
    inner = f'<span class="cv">{cov}</span><span class="t">' + (f'<span class="no">{esc(e["number"])}</span>' if e.get("number") else "") + f'{esc(e["title"])}</span>'
    if not e.get("href"): return f'<div class="card soon" title="Скоро">{inner}</div>'
    ext = ' target="_blank" rel="noopener"' if e.get("type") == "link" else ""
    return f'<a class="card" href="{esc(e["href"])}"{ext}>{inner}</a>'


def info(text):
    return f'<span class="info" tabindex="0" role="note" aria-label="{esc(text)}" data-tip="{esc(text)}">?</span>' if text else ""


def section(c):
    """A subject on the home page: an underlined heading and the cards of its cases (the heading is not a link:
    subjects have no page of their own; /<course>/ redirects here, to #<course>)."""
    cards = "".join(card(e) for e in c["entries"]) or '<p class="empty">Пока пусто.</p>'
    return (f'<section class="subject" id="{esc(c["slug"])}"><h2>{esc(c["title"])}{info(c.get("full", "")) if c["title"].startswith("НИС") else ""}</h2>'
            f'<div class="cards">{cards}</div></section>')


def switch(base):
    """Stable / Beta toggle in the catalogue header (base "" = stable, "/beta" = beta)."""
    on = lambda b: ' class="on" aria-current="page"' if b == base else ""
    return f'<nav class="switch" aria-label="Версия каталога"><a href="/"{on("")}>Stable</a><a href="/beta/"{on("/beta")}>Beta</a></nav>'


def catalogue(courses):
    return "".join(section(c) for c in courses)


def redirect(cfg, c, style, base=""):
    """/<course>/ stays a working URL: subjects are not a page any more, it opens the catalogue at the subject's section."""
    to = f"{base}/#{c['slug']}"
    return page(cfg, c["title"], f'<main><p>Страницы предмета больше нет: <a href="{to}">кейсы «{esc(c["title"])}»</a>.</p></main>'
                f'<script>location.replace({json.dumps(to)})</script>', style,
                head=f'<meta http-equiv="refresh" content="0; url={to}"><link rel="canonical" href="https://{cfg.get("domain", "")}/">')


def code_page(e, c, p, dest, style, cover):
    """code/index.html: the case's code folder as a list of files with their text (files over 300 kB or binary: download only)."""
    src, out = p["code"]["dir"], dest / "code"
    skip = lambda parts: any(x.startswith(".") or x in ("__pycache__", "node_modules") for x in parts)
    files = [f for f in sorted(src.rglob("*")) if f.is_file() and not skip(f.relative_to(src).parts)]
    if not files: sys.exit(f"{src}: no files for the code format")
    side, views = [], []
    def readable(f):
        try: return f.stat().st_size <= 300_000 and f.read_bytes().decode("utf-8") is not None
        except UnicodeDecodeError: return False
    files.sort(key=lambda f: not readable(f))  # files shown here first (stable: names stay alphabetical)
    for i, f in enumerate(files):
        rel = f.relative_to(src).as_posix()
        (out / "files" / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy(f, out / "files" / rel)
        text = None
        if f.stat().st_size <= 300_000:
            try: text = f.read_text(encoding="utf-8")
            except UnicodeDecodeError: pass
        href = "files/" + urllib.parse.quote(rel)
        side.append(f'<a href="#f{i}" data-i="{i}">{esc(rel)}</a>')
        body = f"<pre><code>{esc(text)}</code></pre>" if text is not None else '<p class="cf-note">Файл не показывается здесь (бинарный или больше 300 КБ): скачайте его.</p>'
        views.append(f'<section class="cf" id="f{i}"><div class="cf-h"><code>{esc(rel)}</code><a href="{href}" download>Скачать</a></div>{body}</section>')
    js = """<script>(()=>{const s=[...document.querySelectorAll('.cf')],l=[...document.querySelectorAll('.cf-list a')];
const show=()=>{const k=Math.max(0,s.findIndex(x=>'#'+x.id===location.hash));s.forEach((x,i)=>x.hidden=i!==k);l.forEach((a,i)=>a.classList.toggle('on',i===k));};
addEventListener('hashchange',show);show();})();</script>"""
    (out / "index.html").write_text(case_page(e, c, "code", "".join(views), style, cover, "../", f'<nav class="cf-list">{"".join(side)}</nav>', js=js), encoding="utf-8")


def video_page(e, c, p, dest, style, cover):
    """video/index.html: a player for a video file, or an embed of a YouTube/Rutube link."""
    v = p["video"]
    src = v["src"] if URL.match(v["src"]) else "../" + urllib.parse.quote(v["src"])
    player = (f'<video controls preload="metadata" src="{esc(src)}"></video>' if v["kind"] == "file" else
              f'<iframe src="{esc(v["src"])}" title="{esc(e["title"])}" allow="fullscreen; picture-in-picture" allowfullscreen></iframe>')
    (dest / "video").mkdir(exist_ok=True)
    (dest / "video" / "index.html").write_text(case_page(e, c, "video", f'<div class="cs-video">{player}</div>', style, cover, "../"), encoding="utf-8")


def build_entry(cfg, c, e, dest, style, pdf):
    """Every case: the overview /<course>/<slug>/ (card, choice of materials) plus a page per material that needs one:
    notes/ (notes.md), slides/ (deck.html, or a prebuilt site/), pdf/ (the printed deck), doc/ ("file"), code/, video/;
    downloads ("downloads", committed *.pdf). Every page has the same header and switcher (case_chrome)."""
    if not e.get("href") or e.get("type") == "link": return
    d, slug = e["dir"], e["slug"]
    p = inspect_case(e, pdf)
    e["formats"], e["files"] = p["formats"], p["files"]
    code_dir = {p["code"]["name"]} if p["code"] and "dir" in p["code"] else set()
    deck_skip = code_dir | ({p["video"]["src"]} if p["video"] and p["video"]["kind"] == "file" and not URL.match(p["video"]["src"]) else set())
    copy_media(d, dest, code_dir)
    for f in set(p["files"].values()) | ({p["doc"]} if p["doc"] else set()): shutil.copy(d / f, dest)
    up = [(label, f"../{f}", True) for label, f in p["files"].items()]
    chrome = lambda active, prefix="../": case_chrome(e, c, active, prefix)
    if p["deck"]:
        pack_deck(d, dest / "slides", style, pdf=pdf and not p["committed"], name=slug, has_pdf=p["committed"],
                  title=e["title"], chrome=chrome("slides"), skip=deck_skip)
        if p["committed"]: shutil.copy(d / p["dpdf"], dest / "slides")
    if p["site"]:
        shutil.copytree(d / "site", dest / "slides" / "site")
        pack_frame(dest / "slides", style, e["title"], "site/index.html", chrome("slides"), "Презентация", up)
    if p["deck_pdf"]:  # the printed deck, read inside the site
        (dest / "pdf").mkdir()
        f = dest / "slides" / p["dpdf"]
        pack_frame(dest / "pdf", style, e["title"], f"../slides/{p['dpdf']}#view=FitH", chrome("pdf"),
                   f"{p['dpdf']} · {file_size(f)}", [("Скачать", f"../slides/{p['dpdf']}", True)])
    if p["doc"]:
        (dest / "doc").mkdir()
        if p["doc"].lower().endswith(".pdf"): src = f"../{p['doc']}#view=FitH"
        else: src = "https://view.officeapps.live.com/op/embed.aspx?src=" + urllib.parse.quote(f"https://{cfg['domain']}{e.get('base', '')}/{e['course']}/{slug}/{p['doc']}", safe="")
        pack_frame(dest / "doc", style, e["title"], src, chrome("doc"), f"{p['doc']} · {file_size(d / p['doc'])}", [("Скачать", f"../{p['doc']}", True)])
    toc, widgets = [], 0
    if p["md"]:  # the konspekt lives in notes/, one level down: links written for the case folder get "../"
        body, toc = konspekt(d, style, p["md"], up="../")
        widgets = body.count("<iframe")
        side = ('<nav class="nt-toc"><ol>' + "".join(f'<li class="l{l}"><a href="#{i}">{t}</a></li>' for l, i, t in toc) + "</ol></nav>") if len(toc) > 1 else ""
        css = ("\n" + read(KIT / "notes.css") + (katex_css(cfg) if 'class="katex"' in body else ""))
        (dest / "notes").mkdir(exist_ok=True)
        (dest / "notes" / "index.html").write_text(
            case_page(e, c, "notes", f'<article class="nt-body">{body}</article>', style, None, "../", side=side, css=css,
                      js=f"<script>{read(KIT / 'notes.js')}</script>"), encoding="utf-8")
    cover = make_cover(e, dest, konspekt=bool(p["md"]))  # last: the konspekt page may be the card's only picture
    e["cover_name"] = cover
    text, css = "", ""
    if (d / "overview.md").is_file():  # the case's own words above the choice of materials
        text, _ = konspekt(d, style, "overview.md")
        css = "\n" + read(KIT / "notes.css") + (katex_css(cfg) if 'class="katex"' in text else "")
    # links from the old address of the konspekt (/<course>/<slug>/#anchor) lead to it
    js = '<script>if(location.hash)location.replace("notes/index.html"+location.hash)</script>' if p["md"] else ""
    (dest / "index.html").write_text(case_page(e, c, "overview", overview_main(e, p, dest, toc, widgets, text), style, cover, css=css, js=js), encoding="utf-8")
    if p["code"] and "dir" in p["code"]: code_page(e, c, p, dest, style, cover)
    if p["video"] and p["video"]["kind"] != "link": video_page(e, c, p, dest, style, cover)


def build_site(out, style=None, pdf=False):
    cfg = site_cfg(); style = style or cfg.get("style", "paper")
    out = Path(out)
    safe_out(CONTENT, out); fresh_out(out)
    (out / "assets").mkdir(parents=True); (out / MARK).write_text("")
    shutil.copy(ROOT / "assets" / "site.css", out / "assets" / "site.css")
    shutil.copy(KIT / "theme.css", out / "assets" / "theme.css")
    shutil.copytree(KIT / "katex" / "fonts", out / "assets" / "katex" / "fonts")
    courses = load_content()
    foot = f'<footer class="foot">{esc(cfg.get("footer", ""))}</footer>'
    for c in courses:
        for e in c["entries"]:
            dest = out / e["base"].strip("/") / c["slug"] / e["slug"]
            build_entry(cfg, c, e, dest, style, pdf)
            if not e.get("cover_name") and e.get("cover"): e["cover_name"] = make_cover(e, dest)  # planned/link cases
    # the main catalogue shows only what the owner reviewed; the rest is the beta catalogue at /beta/
    for base in ("", "/beta"):
        root = out / base.strip("/"); root.mkdir(parents=True, exist_ok=True)
        part = [dict(c, entries=[e for e in c["entries"] if e["base"] == base]) for c in courses]
        part = [c for c in part if c["entries"]]
        title = cfg["title"] + (" · beta" if base else "")
        head = f'<header class="hero"><h1><a href="{base}/">{esc(title)}</a></h1>{switch(base)}</header>'
        for c in part:
            (root / c["slug"]).mkdir(parents=True, exist_ok=True)
            (root / c["slug"] / "index.html").write_text(redirect(cfg, c, style, base), encoding="utf-8")
        lead = '<p class="beta-lead">Черновые материалы: автор их ещё не проверил.</p>' if base else ""
        (root / "index.html").write_text(page(cfg, title, head + f"<main>{lead}{catalogue(part) or '<p class="empty">Пока пусто.</p>'}</main>" + foot, style), encoding="utf-8")
    mark_beta(out / "beta")
    (out / "404.html").write_text(page(cfg, "Не найдено", f'<header class="hero"><h1><a href="/">{esc(cfg["title"])}</a></h1></header>'
                                       '<main><p>Такой страницы нет. <a href="/">На главную</a></p></main>', style), encoding="utf-8")
    if cfg.get("domain"): (out / "CNAME").write_text(cfg["domain"] + "\n")
    (out / ".nojekyll").write_text("")
    n = [e["base"] for c in courses for e in c["entries"]]
    print("site", out, n.count(""), "reviewed cases,", n.count("/beta"), "beta")


def new_entry(path, title, date="", event=""):
    """content/<course>/<entry>/ from kit/starter: konspekt, deck and a widget to replace, entry.json with the title."""
    dest = CONTENT / path
    if len(Path(path).parts) != 2: sys.exit("path must be <course>/<entry>, e.g. genomics/loter")
    if not (dest.parent / "course.json").exists(): sys.exit(f"{dest.parent}: no course.json; create the course first")
    if dest.exists(): sys.exit(f"{dest} exists")
    shutil.copytree(KIT / "starter", dest)
    e = {"title": title, "date": date, "event": event, "summary": ""}
    (dest / "entry.json").write_text(json.dumps({k: v for k, v in e.items() if v or k == "summary"}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(dest, "\nnext: write notes.md (konspekt), then deck.html; check with: uv run --with markdown python build.py entry", dest, "/tmp/" + dest.name)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("site"); s.add_argument("--out", default="_site"); s.add_argument("--pdf", action="store_true"); s.add_argument("--style")
    d = sub.add_parser("deck"); d.add_argument("src"); d.add_argument("out"); d.add_argument("--pdf", action="store_true"); d.add_argument("--style", default="paper")
    m = sub.add_parser("entry", help="konspekt + slides of one folder, as on the site"); m.add_argument("src"); m.add_argument("out")
    m.add_argument("--pdf", action="store_true"); m.add_argument("--style", default="paper")
    n = sub.add_parser("new", help="start a material from kit/starter"); n.add_argument("path", help="<course>/<entry>"); n.add_argument("title")
    n.add_argument("--date", default=""); n.add_argument("--event", default="")
    a = ap.parse_args()
    if a.cmd == "new": new_entry(a.path, a.title, a.date, a.event)
    elif a.cmd == "site": build_site(a.out, a.style, a.pdf)
    elif a.cmd == "deck": print(pack_deck(a.src, a.out, a.style, a.pdf, home="/"))
    else:
        src = Path(a.src); e = json.loads(read(src / "entry.json")) if (src / "entry.json").exists() else {}
        e = {"title": src.name, "type": "", **e, "dir": src, "slug": src.name, "course": "", "href": "."}
        build_entry(site_cfg(), {"slug": "", "title": "Материалы"}, e, Path(a.out), a.style, a.pdf); print(Path(a.out) / "index.html")


if __name__ == "__main__":
    main()
