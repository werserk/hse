// Reading view (?read): the deck as an illustrated article, in the manner of a lecture blog.
// Contents on the left; each slide becomes a live figure (widgets work) followed by its speaker notes as text.
(() => {
  if (!new URLSearchParams(location.search).has('read')) return;
  const body = document.body;
  body.dataset.mode = 'read'; body.classList.add('read-body');
  const meta = (n) => document.querySelector(`meta[name="deck:${n}"]`)?.content;
  const el = (tag, cls, html) => Object.assign(document.createElement(tag), cls ? { className: cls } : {}, html ? { innerHTML: html } : {});
  const slides = [...document.querySelectorAll('section.slide')];
  const home = meta('home'), pdf = meta('pdf'), file = meta('file') || 'deck.html';

  const side = el('nav', 'read-side'), toc = el('ol', 'read-toc'), main = el('main', 'read-main');
  const figs = [];
  slides.forEach((s, i) => {
    const notes = s.querySelector('.notes'); notes?.remove();
    s.querySelectorAll('.step').forEach((x) => x.classList.add('shown'));
    const h = s.querySelector('h1, h2');
    const title = (h?.textContent || `Слайд ${i + 1}`).trim();
    const text = notes ? notes.innerHTML.replace(/\[([^\]<]{2,})\]/g, '<span class="read-cue">$1</span>') : '';
    let sec;
    if (i === 0 && s.classList.contains('title')) {  // the title slide becomes the article head
      sec = el('header', 'read-head'); sec.append(...[...s.children]); s.remove();
      side.dataset.title = title;
    } else {
      sec = el('section', 'read-sec'); sec.append(el('h2', '', h ? h.innerHTML : title));
      h?.classList.add('read-hidden');
      const fig = el('div', 'read-fig'); fig.append(s); sec.append(fig); figs.push([fig, s]);
      toc.append(el('li', '', `<a href="#${i + 1}"></a>`)); toc.lastChild.firstChild.textContent = title;
    }
    sec.id = String(i + 1);
    if (text) sec.append(el('div', 'read-text', text));
    main.append(sec);
  });

  side.innerHTML = (home ? `<a class="read-home" href="${home}">← Материалы</a>` : '') +
    `<div class="read-title"></div><div class="read-act"><a class="read-go" href="${location.pathname}#1">▶ Слайды</a>` +
    (pdf ? `<a href="${pdf}" download>PDF</a>` : '') + `<a href="${location.pathname}" download="${file}">HTML</a></div>`;
  side.querySelector('.read-title').textContent = side.dataset.title || document.title;
  side.append(toc);
  body.append(side, main);

  const fit = () => figs.forEach(([fig, s]) => {
    const k = fig.clientWidth / 1280;
    fig.style.height = `${720 * k}px`; s.style.transform = `scale(${k})`;
  });
  addEventListener('resize', fit); fit();

  addEventListener('message', (e) => {  // widget heights; the deck engine is off in this view
    if (e.data?.type !== 'widget-height') return;
    for (const f of document.querySelectorAll('iframe.widget')) if (f.contentWindow === e.source) f.style.height = `${e.data.h}px`;
  });
  const links = [...toc.querySelectorAll('a')];
  const io = new IntersectionObserver((es) => es.forEach((x) => {
    if (!x.isIntersecting) return;
    links.forEach((a) => a.classList.toggle('on', a.getAttribute('href') === `#${x.target.id}`));
  }), { rootMargin: '-20% 0px -70% 0px' });
  main.querySelectorAll('.read-sec').forEach((x) => io.observe(x));
  if (location.hash) document.getElementById(location.hash.slice(1))?.scrollIntoView();
})();
