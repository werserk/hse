// Konspekt page: widget heights, active section in the contents.
(() => {
  addEventListener('message', (e) => {
    if (e.data?.type !== 'widget-height') return;
    for (const f of document.querySelectorAll('iframe.widget')) if (f.contentWindow === e.source) f.style.height = `${e.data.h}px`;
  });
  const links = [...document.querySelectorAll('.nt-toc a')];
  const io = new IntersectionObserver((es) => es.forEach((x) => {
    if (x.isIntersecting) links.forEach((a) => a.classList.toggle('on', a.getAttribute('href') === `#${x.target.id}`));
  }), { rootMargin: '0px 0px -75% 0px' });
  document.querySelectorAll('.nt-body h2[id], .nt-body h3[id]').forEach((x) => io.observe(x));
})();
