// Catalogue: live search filter; ?style=paper|hse|coal previews a style.
(() => {
  const st = new URLSearchParams(location.search).get('style');
  if (st) document.documentElement.dataset.style = st;
  const q = document.getElementById('q');
  if (!q) return;
  q.addEventListener('input', () => {
    const terms = q.value.toLowerCase().split(/\s+/).filter(Boolean);
    document.querySelectorAll('.course').forEach((c) => {
      let any = false;
      c.querySelectorAll('.entry').forEach((e) => {
        const ok = terms.every((t) => e.dataset.search.includes(t));
        e.classList.toggle('hide', !ok); any ||= ok;
      });
      c.classList.toggle('hide', terms.length > 0 && !any);
    });
  });
})();
