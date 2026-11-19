// Deck engine: keys/clicker/swipe navigation, .step reveals, #n hash, fit-to-window,
// the case's header above the slides, controls under them, slide list (O), speaker window (S) synced by postMessage (works from file:// too), fullscreen (F).
(() => {
  const body = document.body;
  body.classList.add('deck-body');
  const slides = [...document.querySelectorAll('section.slide')];
  const meta = (n) => document.querySelector(`meta[name="deck:${n}"]`)?.content;
  const params = new URLSearchParams(location.search), speaker = params.has('speaker'), bare = params.has('bare'), touch = matchMedia('(pointer: coarse)').matches;
  let cur = 0, step = 0, peer = null;

  const stage = document.createElement('div');
  stage.className = 'deck-stage';
  slides.forEach((s, i) => {
    const pg = document.createElement('div');
    pg.className = 'pg'; pg.textContent = `${i + 1} / ${slides.length}`;
    s.appendChild(pg); stage.appendChild(s);
  });

  // Widget iframes report their height (see the snippet the packer injects).
  addEventListener('message', (e) => {
    const d = e.data || {};
    if (d.type === 'widget-height') {
      for (const f of document.querySelectorAll('iframe.widget')) if (f.contentWindow === e.source) f.style.height = `${d.h}px`;
    } else if (d.type === 'widget-key') { key(d.key); }
    else if (d.type === 'deck') { if (!peer || peer.closed) peer = e.source; if (e.source === peer && (d.i !== cur || d.step !== step)) go(d.i, d.step, false); }
    else if (d.type === 'deck-hello') { peer = e.source; send(); }
  });

  const steps = (i) => [...slides[i].querySelectorAll('.step')];
  function render() {
    slides.forEach((s, k) => s.classList.toggle('on', k === cur));
    steps(cur).forEach((el, k) => el.classList.toggle('shown', k < step));
    if (bar) bar.style.width = `${(100 * (cur + 1)) / slides.length}%`;
    if (counter) { counter.textContent = `${cur + 1} / ${slides.length}`; toc.querySelectorAll('button').forEach((b, k) => b.classList.toggle('on', k === cur)); }
    if (location.hash !== `#${cur + 1}`) history.replaceState(null, '', `#${cur + 1}`);
    if (speaker) renderSpeaker();
  }
  function send() { try { peer && !peer.closed && peer.postMessage({ type: 'deck', i: cur, step }, '*'); } catch (e) {} }
  function go(i, s = 0, notify = true) {
    cur = Math.max(0, Math.min(slides.length - 1, i));
    step = Math.max(0, Math.min(steps(cur).length, s));
    body.classList.remove('toc-on');
    render(); if (notify) send();
  }
  const next = () => (step < steps(cur).length ? go(cur, step + 1) : cur < slides.length - 1 && go(cur + 1, 0));
  const prev = () => (step > 0 ? go(cur, step - 1) : cur > 0 && go(cur - 1, steps(cur - 1).length));

  let bar = null, view = null, nextStage = null, notesEl = null, clockEl = null, t0 = null, counter = null, toc = null;
  const titleOf = (s, i) => (s.querySelector('h1, h2')?.textContent || `Слайд ${i + 1}`).replace(/\s+/g, ' ').trim();
  const h = (tag, cls, text) => Object.assign(document.createElement(tag), cls ? { className: cls } : {}, text != null ? { textContent: text } : {});
  if (!speaker) {
    // The case's header (from <template id="deck-chrome">), then the viewer: the slides, and under them the controls.
    // Fullscreen (F, ?bare; on a desktop also an F11 window as big as the screen, never on a touch screen) drops the header and the controls; the header returns when the mouse is at the top.
    const tpl = document.getElementById('deck-chrome');
    const chrome = h('div', 'deck-chrome'); if (tpl) chrome.append(tpl.content);
    const btn = (a, text, title) => { const b = Object.assign(h('button', '', text), { title, type: 'button' }); b.dataset.a = a; return b; };
    const link = (href, text, dl) => { const x = h('a', '', text); x.href = href; if (dl) x.download = dl; return x; };
    const ctl = h('div', 'dt-bar');
    const nav = h('span', 'dt-nav'); counter = btn('toc', '', 'Список слайдов (O)'); counter.className = 'dt-n';
    nav.append(btn('prev', '‹', 'Назад (←)'), counter, btn('next', '›', 'Вперёд (→)'));
    const fsb = btn('full', '', 'Полный экран (F)');
    fsb.innerHTML = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M1 5V1h4M9 1h4v4M13 9v4H9M5 13H1V9"/></svg><span>Во весь экран</span>';
    ctl.append(nav, h('span', 'sp'), fsb, link(location.pathname.split('/').pop() || 'index.html', 'HTML', meta('file') || 'deck.html'));
    toc = h('ol', 'deck-toc');
    slides.forEach((s, i) => { const li = h('li'); li.append(btn('go', `${i + 1}. ${titleOf(s, i)}`, '')); li.firstChild.dataset.i = i; toc.append(li); });
    ctl.append(toc);
    bar = h('div', 'deck-bar');
    view = h('div', 'deck-view'); view.append(stage, bar);
    body.prepend(chrome); body.append(view, ctl);
    addEventListener('click', (e) => {
      if (e.target.closest('a[data-speaker]')) { e.preventDefault(); toggleToc(false); openSpeaker(); return; }   // the speaker window follows this one
      const b = e.target.closest('button[data-a]');
      if (!b) { if (!e.target.closest('.deck-toc')) body.classList.remove('toc-on'); return; }
      const a = b.dataset.a;
      if (a === 'prev') prev(); else if (a === 'next') next(); else if (a === 'toc') toggleToc();
      else if (a === 'go') go(+b.dataset.i);
      else if (a === 'full') { toggleToc(false); full(); }
      b.blur();
    });
    const doFit = () => {
      const fs = !!document.fullscreenElement || bare || (!touch && innerHeight >= screen.height - 1 && innerWidth >= screen.width - 1);  // ?bare: no header (card previews, embedding)
      body.classList.toggle('fs', fs);
      let w, hh, x = 0, y = 0;
      if (fs) {
        const k = Math.min(innerWidth / 1280, innerHeight / 720); w = 1280 * k; hh = 720 * k; x = (innerWidth - w) / 2; y = (innerHeight - hh) / 2;
        view.style.width = view.style.height = ''; ctl.style.width = '';
      } else {   // as wide as the header allows, and no taller than what is left of the window under it
        const wrap = chrome.firstElementChild, room = innerHeight - chrome.offsetHeight - ctl.offsetHeight - 16 - 20;
        const avail = wrap ? wrap.clientWidth - 2 * parseFloat(getComputedStyle(wrap).paddingLeft) : innerWidth - 32;
        w = Math.max(280, Math.min(avail, (room * 16) / 9));
        hh = (w * 9) / 16;
        view.style.width = `${w}px`; view.style.height = `${hh}px`; ctl.style.width = `${w}px`;
      }
      stage.style.transform = `translate(${x}px,${y}px) scale(${w / 1280})`;
    };
    addEventListener('resize', doFit); addEventListener('fullscreenchange', () => { body.classList.remove('top-on', 'toc-on'); doFit(); }); doFit();
    addEventListener('mousemove', (e) => body.classList.toggle('top-on', e.clientY < 56 || !!e.target.closest?.('.deck-chrome, .deck-toc')));
  } else {
    body.classList.add('speaker');
    const root = document.createElement('div'); root.className = 'spk';
    const home = document.getElementById('deck-chrome')?.content.querySelector('.cs-tab');   // the case's overview, so the speaker view is not a dead end
    root.innerHTML = `<div class="spk-head">${home ? `<a class="spk-back" href="${home.getAttribute('href')}">← ${home.textContent}</a>` : ''}<b class="spk-n"></b><span class="spk-clock"></span><span>← → листать · таймер стартует с первого перехода</span></div>
      <div class="spk-cur"></div><div class="spk-side"><div class="spk-next"></div><div class="spk-notes"></div></div>`;
    body.appendChild(root);
    root.querySelector('.spk-cur').appendChild(stage);
    nextStage = document.createElement('div'); nextStage.className = 'deck-stage';
    root.querySelector('.spk-next').appendChild(nextStage);
    notesEl = root.querySelector('.spk-notes'); clockEl = root.querySelector('.spk-clock');
    const doFit = () => {
      for (const [el, box] of [[stage, root.querySelector('.spk-cur')], [nextStage, root.querySelector('.spk-next')]]) {
        const r = box.getBoundingClientRect();
        const k = Math.min(r.width / 1280, r.height / 720);
        el.style.transform = `scale(${k})`; el.style.transformOrigin = '0 0';
      }
    };
    addEventListener('resize', doFit); setTimeout(doFit, 0);
    setInterval(() => {
      if (!t0) { clockEl.textContent = '00:00'; return; }
      const s = Math.floor((Date.now() - t0) / 1000);
      clockEl.textContent = `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
    }, 500);
    // Say hello now and every 1.5 s, so the main window re-attaches after a reload (it answers with its slide).
    const hello = () => { try { if (window.opener && !window.opener.closed) { peer = window.opener; peer.postMessage({ type: 'deck-hello' }, '*'); } } catch (e) {} };
    hello(); setInterval(hello, 1500);
  }

  function renderSpeaker() {
    if (cur > 0 || step > 0) t0 = t0 || Date.now();
    body.querySelector('.spk-n').textContent = `${cur + 1} / ${slides.length}`;
    const n = slides[cur].querySelector('.notes');
    notesEl.innerHTML = n ? n.innerHTML : '<i>Нет заметок</i>';
    nextStage.innerHTML = '';
    const nx = slides[cur + 1];
    if (nx) {
      const c = nx.cloneNode(true); c.classList.add('on');
      c.querySelectorAll('.step').forEach((el) => el.classList.add('shown'));
      c.querySelectorAll('iframe').forEach((f) => f.replaceWith(Object.assign(document.createElement('div'), { className: 'muted', textContent: '[виджет]' })));
      nextStage.appendChild(c);
    }
  }
  function openSpeaker() {
    const w = window.open(`${location.pathname}?speaker#${cur + 1}`, 'deck-speaker', 'width=1200,height=760');
    if (w) peer = w;
  }
  function toggleToc(on) {
    if (!toc) return;
    body.classList.toggle('toc-on', on);
    if (body.classList.contains('toc-on')) toc.querySelector('.on')?.scrollIntoView({ block: 'nearest' });
  }
  function full() { document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen?.(); }

  // Navigation keys; widgets forward theirs (PageUp/PageDown always, so a clicker keeps working after a click in a widget).
  function key(k) {
    if (k !== 'o' && k !== 'O' && k !== 'щ' && k !== 'Щ') body.classList.remove('top-on');  // a clicker press hides the hover header
    if (['ArrowRight', 'ArrowDown', ' ', 'PageDown', 'Enter'].includes(k)) next();
    else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(k)) prev();
    else if (k === 'Home') go(0); else if (k === 'End') go(slides.length - 1);
    else if (k === 'f' || k === 'F' || k === 'а' || k === 'А') full();
    else if ((k === 's' || k === 'S' || k === 'ы' || k === 'Ы') && !speaker) openSpeaker();
    else if (k === 'o' || k === 'O' || k === 'щ' || k === 'Щ') toggleToc();
    else if (k === 'Escape' && body.classList.contains('toc-on')) toggleToc(false);
    else return false;
    return true;
  }
  addEventListener('keydown', (e) => {
    if (e.target.closest?.('input, textarea, select') || (e.target.closest?.('a, button') && (e.key === 'Enter' || e.key === ' ')) || e.ctrlKey || e.metaKey || e.altKey) return;
    if (key(e.key)) e.preventDefault();
  });
  let tx = null;
  addEventListener('touchstart', (e) => { tx = e.touches[0].clientX; }, { passive: true });
  addEventListener('touchend', (e) => { if (tx === null) return; const dx = e.changedTouches[0].clientX - tx; if (Math.abs(dx) > 50) (dx < 0 ? next : prev)(); tx = null; });
  addEventListener('hashchange', () => { const n = parseInt(location.hash.slice(1), 10); if (n && n - 1 !== cur) go(n - 1); });

  go((parseInt(location.hash.slice(1), 10) || 1) - 1, 0, false);
})();
