#!/usr/bin/env python3
"""Build hse.werserk.dev.

  python3 build.py site [--out _site] [--pdf] [--style paper]   catalogue + every entry
  python3 build.py deck SRC_DIR OUT_DIR [--pdf] [--style paper]  one deck → offline HTML (+ PDF)

Stdlib only; `markdown` is used for notes entries when installed. PDF needs Chrome/Chromium
(CHROME env var, PATH, or the Playwright cache).
"""
import argparse, glob, html, json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KIT = ROOT / "kit"
CONTENT = ROOT / "content"
TYPE_LABEL = {"deck": "доклад", "site": "доклад", "pdf": "слайды", "notes": "конспект", "link": "ссылка"}


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


# ---------- catalogue ----------

def load_content():
    courses = []
    for cdir in sorted(p for p in CONTENT.iterdir() if (p / "course.json").exists()):
        c = json.loads(read(cdir / "course.json")); c["slug"] = cdir.name; c["dir"] = cdir
        c["entries"] = []
        for edir in sorted(p for p in cdir.iterdir() if (p / "entry.json").exists()):
            e = json.loads(read(edir / "entry.json")); e["slug"] = edir.name; e["dir"] = edir
            e["course"] = c["slug"]; e["url"] = e.get("url") or (f"/{c['slug']}/{edir.name}/" if e.get("status") != "planned" else None)
            c["entries"].append(e)
        c["entries"].sort(key=lambda e: e.get("date", ""), reverse=True)
        courses.append(c)
    courses.sort(key=lambda c: (c.get("order", 99), c["slug"]))
    return courses


def page(cfg, title, body, style, crumbs=()):
    nav = " / ".join([f'<a href="/">{esc(cfg["title"])}</a>'] + [f'<a href="{u}">{esc(t)}</a>' for t, u in crumbs])
    return f"""<!doctype html><html lang="ru" data-style="{style}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>
<link rel="stylesheet" href="/assets/theme.css"><link rel="stylesheet" href="/assets/site.css"></head>
<body><header class="top"><nav class="crumbs">{nav}</nav></header><main>{body}</main>
<footer class="foot">{esc(cfg.get("footer", ""))}</footer><script src="/assets/site.js"></script></body></html>"""


def entry_links(e):
    if not e.get("url"): return '<span class="soon">скоро</span>'
    out = [f'<a href="{esc(e["url"])}">открыть</a>']
    for label, f in (e.get("downloads") or {}).items():
        dl = f"{e['slug']}.html" if f == "index.html" else f
        out.append(f'<a href="{esc(e["url"] + f)}" download="{esc(dl)}">{esc(label)}</a>')
    return " · ".join(out)


def entry_row(e, course=None):
    meta = " · ".join(x for x in [e.get("date", ""), e.get("event", ""), course or ""] if x)
    tags = " ".join(e.get("tags", []))
    title = f'<a href="{esc(e["url"])}">{esc(e["title"])}</a>' if e.get("url") else esc(e["title"])
    return f"""<li class="entry" data-search="{esc((e['title'] + ' ' + e.get('summary', '') + ' ' + tags + ' ' + (course or '')).lower())}">
<span class="badge t-{esc(e['type'])}">{esc(TYPE_LABEL.get(e['type'], e['type']))}</span>
<div><div class="e-title">{title}</div><div class="e-meta">{esc(meta)}</div>
<p class="e-sum">{esc(e.get('summary', ''))}</p><div class="e-links">{entry_links(e)}</div></div></li>"""


def build_entry(e, out, style, pdf):
    d, dest = e["dir"], out / e["course"] / e["slug"]
    t = e["type"]
    if e.get("status") == "planned" or t == "link": return
    if t == "deck":
        committed = (d / f"{e['slug']}.pdf").exists()  # a locally printed PDF wins over a CI print
        pack_deck(d, dest, style, pdf=pdf and not committed, home=f"/{e['course']}/", name=e["slug"], has_pdf=committed)
        for p in d.glob("*.pdf"): shutil.copy(p, dest)
        e.setdefault("downloads", {})["HTML"] = "index.html"
        if pdf or committed: e["downloads"]["PDF"] = f"{e['slug']}.pdf"
    elif t == "site":
        shutil.copytree(d / "site", dest, dirs_exist_ok=True)
        for p in d.glob("*.pdf"): shutil.copy(p, dest)
    elif t == "pdf":
        dest.mkdir(parents=True, exist_ok=True)
        f = e["file"]; shutil.copy(d / f, dest / f)
        e.setdefault("downloads", {})["PDF"] = f
    elif t == "notes":
        dest.mkdir(parents=True, exist_ok=True)
        for p in d.iterdir():
            if p.name not in ("entry.json", "index.md"):
                (shutil.copytree if p.is_dir() else shutil.copy)(p, dest / p.name)


def render_entry_page(cfg, c, e, out, style):
    """Pages for types that have no own index.html: pdf viewer, notes."""
    t, dest = e["type"], out / e["course"] / e["slug"]
    if e.get("status") == "planned": return
    crumbs = [(c["title"], f"/{c['slug']}/")]
    head = f'<h1>{esc(e["title"])}</h1><p class="lead">{esc(e.get("summary", ""))}</p><p class="e-links">{entry_links(e)}</p>'
    if t == "pdf":
        body = head + f'<object class="pdf" data="{esc(e["file"])}" type="application/pdf"><a href="{esc(e["file"])}">PDF</a></object>'
    elif t == "notes":
        md = read(e["dir"] / "index.md")
        try:
            import markdown
            inner = markdown.markdown(md, extensions=["tables", "fenced_code", "toc"])
        except ImportError:
            inner = f"<pre>{esc(md)}</pre>"
        body = f'<article class="prose">{inner}</article>'
    else:
        return
    (dest / "index.html").write_text(page(cfg, e["title"], body, style, crumbs), encoding="utf-8")


def build_site(out, style=None, pdf=False):
    cfg = site_cfg(); style = style or cfg.get("style", "paper")
    out = Path(out)
    if out.exists(): shutil.rmtree(out)
    (out / "assets").mkdir(parents=True)
    for f in ("site.css", "site.js"): shutil.copy(ROOT / "assets" / f, out / "assets" / f)
    shutil.copy(KIT / "theme.css", out / "assets" / "theme.css")
    courses = load_content()
    for c in courses:
        for e in c["entries"]:
            build_entry(e, out, style, pdf)
            render_entry_page(cfg, c, e, out, style)
    sections = []
    for c in courses:
        rows = "".join(entry_row(e) for e in c["entries"]) or '<li class="empty">Пока пусто.</li>'
        sections.append(f'<section class="course" id="{esc(c["slug"])}"><h2><a href="/{esc(c["slug"])}/">{esc(c["title"])}</a></h2>'
                        f'<p class="c-sub">{esc(c.get("subtitle", ""))}</p><ul class="entries">{rows}</ul></section>')
        (out / c["slug"]).mkdir(exist_ok=True)
        cbody = f'<h1>{esc(c["title"])}</h1><p class="lead">{esc(c.get("description", c.get("subtitle", "")))}</p><ul class="entries">{rows}</ul>'
        (out / c["slug"] / "index.html").write_text(page(cfg, c["title"], cbody, style), encoding="utf-8")
    toc = "".join(f'<a href="#{esc(c["slug"])}">{esc(c["title"])}</a>' for c in courses)
    body = (f'<h1>{esc(cfg["title"])}</h1><p class="lead">{esc(cfg.get("intro", ""))}</p>'
            f'<div class="tools"><input id="q" type="search" placeholder="Поиск по материалам" autocomplete="off"><nav class="toc">{toc}</nav></div>'
            + "".join(sections))
    (out / "index.html").write_text(page(cfg, cfg["title"], body, style), encoding="utf-8")
    (out / "404.html").write_text(page(cfg, "Не найдено", '<h1>Не найдено</h1><p><a href="/">В каталог</a></p>', style), encoding="utf-8")
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
