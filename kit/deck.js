// Deck engine: keys/clicker/swipe navigation, .step reveals, #n hash, fit-to-window,
// speaker view (S) synced by postMessage (works from file:// too), fullscreen (F), downloads.
(() => {
  const body = document.body;
  body.classList.add('deck-body');
  const slides = [...document.querySelectorAll('section.slide')];
  const meta = (n) => document.querySelector(`meta[name="deck:${n}"]`)?.content;
  const speaker = new URLSearchParams(location.search).has('speaker');
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
    } else if (d.type === 'deck' && e.source === peer) { go(d.i, d.step, false); }
    else if (d.type === 'deck-hello') { peer = e.source; send(); }
  });

  const steps = (i) => [...slides[i].querySelectorAll('.step')];
  function render() {
    slides.forEach((s, k) => s.classList.toggle('on', k === cur));
    steps(cur).forEach((el, k) => el.classList.toggle('shown', k < step));
    if (bar) bar.style.width = `${(100 * (cur + 1)) / slides.length}%`;
    if (location.hash !== `#${cur + 1}`) history.replaceState(null, '', `#${cur + 1}`);
    if (speaker) renderSpeaker();
  }
  function send() { try { peer && !peer.closed && peer.postMessage({ type: 'deck', i: cur, step }, '*'); } catch (e) {} }
  function go(i, s = 0, notify = true) {
    cur = Math.max(0, Math.min(slides.length - 1, i));
    step = Math.max(0, Math.min(steps(cur).length, s));
    render(); if (notify) send();
  }
  const next = () => (step < steps(cur).length ? go(cur, step + 1) : cur < slides.length - 1 && go(cur + 1, 0));
  const prev = () => (step > 0 ? go(cur, step - 1) : cur > 0 && go(cur - 1, steps(cur - 1).length));

  let bar = null, nextStage = null, notesEl = null, clockEl = null, t0 = null;
  if (!speaker) {
    body.appendChild(stage);
    bar = document.createElement('div'); bar.className = 'deck-bar'; body.appendChild(bar);
    const ui = document.createElement('nav'); ui.className = 'deck-ui';
    const home = meta('home'), pdf = meta('pdf');
    ui.innerHTML =
      (home ? `<a href="${home}" title="Каталог">⌂</a>` : '') +
      `<button data-a="prev" title="Назад (←)">‹</button><button data-a="next" title="Вперёд (→)">›</button>` +
      `<button data-a="speaker" title="Режим докладчика (S)">S</button><button data-a="full" title="Полный экран (F)">⛶</button>` +
      (pdf ? `<a href="${pdf}" download title="Скачать PDF">PDF</a>` : '') +
      `<a href="${location.pathname.split('/').pop() || 'index.html'}" download="${meta('file') || 'deck.html'}" title="Скачать офлайн-HTML">HTML</a>`;
    ui.addEventListener('click', (e) => {
      const a = e.target.closest('button')?.dataset.a;
      if (a === 'prev') prev(); else if (a === 'next') next();
      else if (a === 'speaker') openSpeaker(); else if (a === 'full') full();
    });
    body.appendChild(ui);
    const doFit = () => {
      const k = Math.min(innerWidth / 1280, innerHeight / 720);
      stage.style.transform = `translate(-50%,-50%) scale(${k})`;
    };
    addEventListener('resize', doFit); doFit();
    let idle; addEventListener('mousemove', () => { body.classList.add('ui-on'); clearTimeout(idle); idle = setTimeout(() => body.classList.remove('ui-on'), 1800); });
  } else {
    body.classList.add('speaker');
    const root = document.createElement('div'); root.className = 'spk';
    root.innerHTML = `<div class="spk-head"><b class="spk-n"></b><span class="spk-clock"></span><span>← → листать · таймер стартует с первого перехода</span></div>
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
    if (window.opener) { peer = window.opener; peer.postMessage({ type: 'deck-hello' }, '*'); }
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
  function full() { document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen?.(); }

  addEventListener('keydown', (e) => {
    if (e.target.closest?.('input, textarea, select')) return;
    const k = e.key;
    if (['ArrowRight', 'ArrowDown', ' ', 'PageDown', 'Enter'].includes(k)) { e.preventDefault(); next(); }
    else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(k)) { e.preventDefault(); prev(); }
    else if (k === 'Home') go(0); else if (k === 'End') go(slides.length - 1);
    else if (k === 'f' || k === 'F' || k === 'а' || k === 'А') full();
    else if ((k === 's' || k === 'S' || k === 'ы' || k === 'Ы') && !speaker) openSpeaker();
  });
  let tx = null;
  addEventListener('touchstart', (e) => { tx = e.touches[0].clientX; }, { passive: true });
  addEventListener('touchend', (e) => { if (tx === null) return; const dx = e.changedTouches[0].clientX - tx; if (Math.abs(dx) > 50) (dx < 0 ? next : prev)(); tx = null; });
  addEventListener('hashchange', () => { const n = parseInt(location.hash.slice(1), 10); if (n && n - 1 !== cur) go(n - 1); });

  go((parseInt(location.hash.slice(1), 10) || 1) - 1, 0, false);
})();
