#!/usr/bin/env python3
"""Build hse.werserk.dev.

  python3 build.py site [--out _site] [--pdf] [--style paper]   catalogue + every entry
  python3 build.py deck SRC_DIR OUT_DIR [--pdf] [--style paper]  one deck → offline HTML (+ PDF)

Stdlib only; `markdown` is used for notes entries when installed. PDF needs Chrome/Chromium
(CHROME env var, PATH, or the Playwright cache).
"""
import argparse, glob, html, json, os, re, shutil, subprocess, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KIT = ROOT / "kit"
CONTENT = ROOT / "content"
TYPE_LABEL = {"deck": "доклад", "site": "доклад", "pdf": "PDF", "pptx": "презентация", "notes": "конспект", "link": "ссылка"}


def read(p): return Path(p).read_text(encoding="utf-8")
def esc(s): return html.escape(str(s), quote=True)


def site_cfg():
    return json.loads(read(ROOT / "site.json"))


# ---------- deck packer ----------

WIDGET_HEAD = """<!doctype html><html data-style="{style}"><head><meta charset="utf-8"><base target="_blank">
<style>{theme}
body{{margin:0;background:transparent;color:var(--foreground);font:14px/1.45 var(--font-sans);zoom:{zoom};accent-color:var(--brand)}}</style></head><body>"""
WIDGET_TAIL = """<script>(()=>{const r=()=>parent.postMessage({type:'widget-height',h:Math.ceil(document.documentElement.scrollHeight)},'*');
new ResizeObserver(r).observe(document.documentElement);addEventListener('load',r);r();
const nav=['PageDown','PageUp','ArrowRight','ArrowLeft','ArrowDown','ArrowUp',' ','Home','End','f','F','а','А','s','S','ы','Ы'];
addEventListener('keydown',e=>{if(e.ctrlKey||e.metaKey||e.altKey)return;const t=e.target,typing=t.isContentEditable||/^(TEXTAREA|SELECT)$/.test(t.tagName)||(t.tagName==='INPUT'&&!/^(range|checkbox|radio|button)$/.test(t.type));
if(!nav.includes(e.key)||(typing&&!e.key.startsWith('Page')))return;e.preventDefault();parent.postMessage({type:'widget-key',key:e.key},'*');},true);})();</script></body></html>"""


def pack_widget(path, style, zoom):
    src = re.sub(r"(?is)^\s*<!doctype[^>]*>", "", read(path))
    return WIDGET_HEAD.format(style=style, theme=read(KIT / "theme.css"), zoom=zoom) + src + WIDGET_TAIL


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


def pack_deck(src, out, style, pdf=False, home=None, name=None, has_pdf=False):
    src, out = Path(src), Path(out)
    doc = read(src / "deck.html")
    name = name or src.name
    m = re.search(r'<html\b[^>]*\bdata-style=["\']([^"\']+)', doc)
    style = m.group(1) if m else style
    if not m:  # before any inlining, so the <html> found is the page's own
        doc = re.sub(r"(?i)<html\b", f'<html data-style="{style}"', doc, count=1) if re.search(r"(?i)<html\b", doc) \
            else f'<!doctype html><html data-style="{style}">' + re.sub(r"(?is)^\s*<!doctype[^>]*>", "", doc)
    parts = re.split(r"(<!--.*?-->)", doc, flags=re.S)  # HTML comments stay untouched
    live = [p for p in parts if not p.startswith("<!--")]
    widget = re.compile(r'<iframe\b[^>]*?\b(data-src=(?:"([^"]+)"|\'([^\']+)\'))[^>]*>')
    link = re.compile(r'<link rel="stylesheet" href="(?!https?:|//)([^"]+)">')
    script = re.compile(r'<script src="(?!https?:|//)([^"]+)"></script>')
    refs = [_Q(w).group(2) for p in live for w in widget.finditer(p)] + [r for p in live for r in link.findall(p) + script.findall(p)]
    missing = [r for r in refs if not (src / r).is_file()]
    if missing: sys.exit(f"{src / 'deck.html'}: file not found: {', '.join(missing)}")
    safe_out(src, out); fresh_out(out)
    shutil.copytree(src, out, ignore=shutil.ignore_patterns("deck.html", "*.pdf", ".*"))
    (out / MARK).write_text("")

    def inline_widget(m):
        tag = m.group(0)
        zm = re.search(r'data-zoom=["\']([^"\']+)', tag)
        srcdoc = esc(pack_widget(src / m.group(2), style, zm.group(1) if zm else "1.6"))
        return tag.replace(m.group(1), f'srcdoc="{srcdoc}"', 1)

    def inline(p):
        if p.startswith("<!--"): return p
        p = widget.sub(lambda m: inline_widget(_Q(m)), p)
        p = link.sub(lambda m: f"<style>{read(src / m.group(1))}</style>", p)
        return script.sub(lambda m: f"<script>{read(src / m.group(1))}</script>", p)

    doc = "".join(inline(p) for p in parts)
    metas = [f'<meta name="deck:file" content="{esc(name)}.html">']
    if pdf or has_pdf: metas.append(f'<meta name="deck:pdf" content="{esc(name)}.pdf">')
    if home: metas.append(f'<meta name="deck:home" content="{esc(home)}">')
    head = "\n".join(metas) + f"\n<style>{read(KIT / 'theme.css')}\n{read(KIT / 'deck.css')}</style>\n"
    if re.search(r"(?i)</head>", doc):
        doc = re.sub(r"(?i)</head>", lambda _: head + "</head>", doc, count=1)
    else:  # no </head>: keep doctype first and the charset inside the first 1024 bytes
        at = re.match(r"(?is)(?:\s|<!--.*?-->)*(<!doctype[^>]*>)?\s*(<html\b[^>]*>)?\s*(<head\b[^>]*>)?", doc).end()
        doc = doc[:at] + '<meta charset="utf-8">\n' + head + doc[at:]
    js = f"<script>{read(KIT / 'read.js')}</script>\n<script>{read(KIT / 'deck.js')}</script>\n"
    doc = re.sub(r"(?i)</body>", lambda _: js + "</body>", doc, count=1) if re.search(r"(?i)</body>", doc) else doc + js
    (out / "index.html").write_text(doc, encoding="utf-8")
    if pdf: print_pdf(out / "index.html", out / f"{name}.pdf")
    return out / "index.html"


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


def make_cover(e, dest):
    """Card preview: "cover" in entry.json (a file, or a slide number), else the first figure slide / first PDF page."""
    d, t, cov = e["dir"], e["type"], e.get("cover")
    dest.mkdir(parents=True, exist_ok=True)
    if isinstance(cov, str):
        name = "cover" + Path(cov).suffix
        shutil.copy(d / cov, dest / name); return name
    png = dest / "cover.png"
    if t in ("deck", "site") and (dest / "index.html").exists():
        n = cov or figure_slide(dest / "index.html")
        shoot(f"{(dest / 'index.html').resolve().as_uri()}#{n}", png)
    elif t == "pdf" and shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-png", "-singlefile", "-f", "1", "-l", "1", "-scale-to-x", "640", "-scale-to-y", "-1",
                        str(d / e["file"]), str(dest / "cover")], check=False)
    return png.name if png.exists() else None


# ---------- catalogue: subject sections → material cards → material page ----------

def load_content():
    courses = []
    for cdir in sorted(p for p in CONTENT.iterdir() if (p / "course.json").exists()):
        c = json.loads(read(cdir / "course.json")); c["slug"] = cdir.name
        c["entries"] = []
        for edir in sorted(p for p in cdir.iterdir() if (p / "entry.json").exists()):
            e = json.loads(read(edir / "entry.json")); e["slug"] = edir.name; e["dir"] = edir; e["course"] = c["slug"]
            if e.get("status") != "planned":
                e["href"] = e["url"] if e["type"] == "link" else f"/{c['slug']}/{edir.name}/"
            c["entries"].append(e)
        c["entries"].sort(key=lambda e: e.get("date", ""), reverse=True)
        courses.append(c)
    courses.sort(key=lambda c: (c.get("order", 99), c["slug"]))
    return courses


def page(cfg, title, body, style, cls=""):
    return f"""<!doctype html><html lang="ru" data-style="{style}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>
<link rel="stylesheet" href="/assets/theme.css"><link rel="stylesheet" href="/assets/site.css"></head>
<body class="{cls}">{body}</body></html>"""


def card(e):
    meta = " · ".join(x for x in [TYPE_LABEL.get(e["type"], e["type"]), e.get("date", ""), e.get("event", "")] if x)
    cov = (f'<img src="/{esc(e["course"])}/{esc(e["slug"])}/{esc(e["cover"])}" alt="" loading="lazy">' if e.get("cover_file")
           else f'<span class="ph">{esc(TYPE_LABEL.get(e["type"], e["type"]))}</span>')
    cap = f'<span class="t">{esc(e["title"])}</span><span class="m">{esc(meta if e.get("href") else "скоро")}</span>'
    inner = f'<span class="cv">{cov}</span><span class="cap">{cap}</span>'
    if not e.get("href"): return f'<div class="card soon">{inner}</div>'
    ext = ' target="_blank" rel="noopener"' if e["type"] == "link" else ""
    return f'<a class="card" href="{esc(e["href"])}"{ext} title="{esc(e.get("summary", ""))}">{inner}</a>'


def section(c, heading="h2"):
    cards = "".join(card(e) for e in c["entries"]) or '<p class="empty">Пока пусто.</p>'
    return (f'<section class="subject" id="{esc(c["slug"])}"><{heading}><a href="/{esc(c["slug"])}/">{esc(c["title"])}</a></{heading}>'
            f'<p class="sub">{esc(c.get("subtitle", ""))}</p><div class="cards">{cards}</div></section>')


def viewer(cfg, c, e, inner, style, downloads=()):
    dl = "".join(f'<a href="{esc(f)}" download>{esc(label)}</a>' for label, f in downloads)
    bar = (f'<header class="bar"><a href="/{esc(c["slug"])}/" title="{esc(c["title"])}">← {esc(c["title"])}</a>'
           f'<span class="bt">{esc(e["title"])}</span><span class="dl">{dl}</span></header>')
    return page(cfg, e["title"], bar + f'<div class="view">{inner}</div>', style, "viewer")


def build_entry(cfg, c, e, out, style, pdf):
    """Every material gets /<course>/<slug>/: decks and sites are that page; pdf/md/pptx get a viewer page."""
    if not e.get("href") or e["type"] == "link": return
    d, dest, t = e["dir"], out / e["course"] / e["slug"], e["type"]
    if t == "deck":
        committed = (d / f"{e['slug']}.pdf").exists()  # a locally printed PDF wins over a CI print
        pack_deck(d, dest, style, pdf=pdf and not committed, home="/", name=e["slug"], has_pdf=committed)
        for p in d.glob("*.pdf"): shutil.copy(p, dest)
        return
    if t == "site":
        shutil.copytree(d / "site", dest, dirs_exist_ok=True)
        for p in d.glob("*.pdf"): shutil.copy(p, dest)
        return
    shutil.copytree(d, dest, ignore=shutil.ignore_patterns("entry.json", ".*"), dirs_exist_ok=True)
    if t == "pdf":
        f = e["file"]
        html_ = viewer(cfg, c, e, f'<iframe class="doc" src="{esc(f)}" title="{esc(e["title"])}"></iframe>', style, [("Скачать PDF", f)])
    elif t == "pptx":
        f = e["file"]
        src = urllib.parse.quote(f"https://{cfg['domain']}/{e['course']}/{e['slug']}/{f}", safe="")
        html_ = viewer(cfg, c, e, f'<iframe class="doc" src="https://view.officeapps.live.com/op/embed.aspx?src={src}" title="{esc(e["title"])}"></iframe>',
                       style, [("Скачать PPTX", f)])
    elif t == "notes":
        md = read(d / e.get("file", "index.md"))
        try:
            import markdown
            inner = markdown.markdown(md, extensions=["tables", "fenced_code", "toc"])
        except ImportError:
            inner = f"<pre>{esc(md)}</pre>"
        html_ = viewer(cfg, c, e, f'<article class="prose">{inner}</article>', style, [("Скачать .md", e.get("file", "index.md"))])
    else:
        sys.exit(f"{d}: unknown type {t}")
    (dest / "index.html").write_text(html_, encoding="utf-8")


def build_site(out, style=None, pdf=False):
    cfg = site_cfg(); style = style or cfg.get("style", "paper")
    out = Path(out)
    safe_out(CONTENT, out); fresh_out(out)
    (out / "assets").mkdir(parents=True); (out / MARK).write_text("")
    shutil.copy(ROOT / "assets" / "site.css", out / "assets" / "site.css")
    shutil.copy(KIT / "theme.css", out / "assets" / "theme.css")
    courses = load_content()
    head = f'<header class="hero"><h1><a href="/">{esc(cfg["title"])}</a></h1><p>{esc(cfg.get("intro", ""))}</p></header>'
    foot = f'<footer class="foot">{esc(cfg.get("footer", ""))}</footer>'
    for c in courses:
        for e in c["entries"]:
            build_entry(cfg, c, e, out, style, pdf)
            if e.get("href") or e.get("cover"):
                e["cover"] = make_cover(e, out / c["slug"] / e["slug"]); e["cover_file"] = bool(e["cover"])
        (out / c["slug"]).mkdir(exist_ok=True)
        (out / c["slug"] / "index.html").write_text(page(cfg, c["title"], head + f"<main>{section(c, 'h1')}</main>" + foot, style), encoding="utf-8")
    body = head + "<main>" + "".join(section(c) for c in courses) + "</main>" + foot
    (out / "index.html").write_text(page(cfg, cfg["title"], body, style), encoding="utf-8")
    (out / "404.html").write_text(page(cfg, "Не найдено", head + '<main><p>Такой страницы нет. <a href="/">На главную</a></p></main>', style), encoding="utf-8")
    if cfg.get("domain"): (out / "CNAME").write_text(cfg["domain"] + "\n")
    (out / ".nojekyll").write_text("")
    print("site", out, sum(len(c["entries"]) for c in courses), "entries")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("site"); s.add_argument("--out", default="_site"); s.add_argument("--pdf", action="store_true"); s.add_argument("--style")
    d = sub.add_parser("deck"); d.add_argument("src"); d.add_argument("out"); d.add_argument("--pdf", action="store_true"); d.add_argument("--style", default="paper")
    a = ap.parse_args()
    if a.cmd == "site": build_site(a.out, a.style, a.pdf)
    else: print(pack_deck(a.src, a.out, a.style, a.pdf))


if __name__ == "__main__":
    main()
