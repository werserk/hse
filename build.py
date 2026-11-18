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
new ResizeObserver(r).observe(document.documentElement);addEventListener('load',r);r();})();</script></body></html>"""


def pack_widget(path, style, zoom):
    src = re.sub(r"(?is)^\s*<!doctype[^>]*>", "", read(path))
    return WIDGET_HEAD.format(style=style, theme=read(KIT / "theme.css"), zoom=zoom) + src + WIDGET_TAIL


def pack_deck(src, out, style, pdf=False, home=None, name=None, has_pdf=False):
    src, out = Path(src), Path(out)
    doc = read(src / "deck.html")
    name = name or src.name
    m = re.search(r'<html[^>]*data-style="([^"]+)"', doc)
    style = m.group(1) if m else style
    if out.exists(): shutil.rmtree(out)
    shutil.copytree(src, out, ignore=shutil.ignore_patterns("deck.html", "*.pdf", ".*"))

    def inline_widget(m):
        tag = m.group(0)
        ref = re.search(r'data-src="([^"]+)"', tag).group(1)
        zm = re.search(r'data-zoom="([^"]+)"', tag)
        srcdoc = esc(pack_widget(src / ref, style, zm.group(1) if zm else "1.6"))
        return re.sub(r'data-src="[^"]+"', f'srcdoc="{srcdoc}"', tag, count=1)

    doc = re.sub(r'<iframe\b[^>]*\bdata-src="[^"]+"[^>]*>', inline_widget, doc)
    doc = re.sub(r'<link rel="stylesheet" href="(?!https?:)([^"]+)">', lambda m: f"<style>{read(src / m.group(1))}</style>", doc)
    doc = re.sub(r'<script src="(?!https?:)([^"]+)"></script>', lambda m: f"<script>{read(src / m.group(1))}</script>", doc)
    metas = [f'<meta name="deck:file" content="{esc(name)}.html">']
    if pdf or has_pdf: metas.append(f'<meta name="deck:pdf" content="{esc(name)}.pdf">')
    if home: metas.append(f'<meta name="deck:home" content="{esc(home)}">')
    head = "\n".join(metas) + f"\n<style>{read(KIT / 'theme.css')}\n{read(KIT / 'deck.css')}</style>\n"
    doc = doc.replace("</head>", head + "</head>", 1)
    doc = doc.replace("</body>", f"<script>{read(KIT / 'deck.js')}</script>\n</body>", 1)
    if 'data-style=' not in doc.split("<head", 1)[0]:
        doc = re.sub(r"<html\b", f'<html data-style="{style}"', doc, count=1)
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
    meta = " · ".join(x for x in [e.get("date", ""), e.get("event", "")] if x)
    inner = (f'<span class="k">{esc(TYPE_LABEL.get(e["type"], e["type"]))}</span><span class="t">{esc(e["title"])}</span>'
             f'<span class="m">{esc(meta)}</span><span class="s">{esc(e.get("summary", ""))}</span>')
    if not e.get("href"): return f'<div class="card soon">{inner}<span class="m">скоро</span></div>'
    ext = ' target="_blank" rel="noopener"' if e["type"] == "link" else ""
    return f'<a class="card" href="{esc(e["href"])}"{ext}>{inner}</a>'


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
    if out.exists(): shutil.rmtree(out)
    (out / "assets").mkdir(parents=True)
    shutil.copy(ROOT / "assets" / "site.css", out / "assets" / "site.css")
    shutil.copy(KIT / "theme.css", out / "assets" / "theme.css")
    courses = load_content()
    head = f'<header class="hero"><h1><a href="/">{esc(cfg["title"])}</a></h1><p>{esc(cfg.get("intro", ""))}</p></header>'
    foot = f'<footer class="foot">{esc(cfg.get("footer", ""))}</footer>'
    for c in courses:
        for e in c["entries"]: build_entry(cfg, c, e, out, style, pdf)
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
