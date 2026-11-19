// Frame for a resource that is not our deck (a prebuilt site, a document): the shared header above, the resource below.
// The resource keeps the keyboard (focus returns after a header click; keys pressed on the header are handed over),
// ⛶ / F put the resource itself in fullscreen, and #n is passed in and copied back so a reload keeps the slide.
(() => {
  const f = document.querySelector('.fr-view'), base = f.dataset.src, local = !/^https?:/.test(base) && !/\.pdf(#|$)/i.test(base);   // a PDF keeps its own #view
  f.src = base + (local ? location.hash : '');
  const inner = () => { try { return f.contentWindow.document && f.contentWindow; } catch (e) { return null; } };
  const focus = () => { try { f.contentWindow.focus(); } catch (e) {} };
  const full = () => (document.fullscreenElement ? document.exitFullscreen() : f.requestFullscreen?.());
  f.addEventListener('load', () => {
    focus();
    const w = local && inner();
    if (!w) return;
    const copy = () => { const h = w.location.hash; if (h && h !== location.hash) history.replaceState(null, '', h); };
    for (const k of ['replaceState', 'pushState']) { const o = w.history[k].bind(w.history); w.history[k] = (...a) => { o(...a); copy(); }; }
    w.addEventListener('hashchange', copy); copy();
  });
  addEventListener('click', (e) => {
    if (e.target.closest('button[data-a="full"]')) full();
    if (!e.target.closest('a')) focus();
  });
  addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey || e.key === 'Tab' || (e.target.closest?.('a, button') && e.key === 'Enter')) return;
    e.preventDefault();
    if (['f', 'F', 'а', 'А'].includes(e.key)) return full();
    const w = inner();
    if (w) w.document.dispatchEvent(new w.KeyboardEvent('keydown', { key: e.key, code: e.code, shiftKey: e.shiftKey, bubbles: true, cancelable: true }));
    focus();
  });
})();
