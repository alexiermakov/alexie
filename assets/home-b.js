// Главная: смена фото при движении мыши, часы по Петербургу (вид 2)
// и размытый правый конец крупных строк.
(() => {
  const esc = s => s.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  const settings = () => {
    try { return JSON.parse(localStorage.getItem('settings') || '{}'); } catch (e) { return {}; }
  };

  // ---------- фото ----------
  // Каждые STEP пикселей пути курсора показываем следующее фото; по клику и тапу — тоже.
  // Стартовое фото случайное, его выбирает встроенный скрипт сразу после разметки.
  const STEP = 70;
  document.querySelectorAll('img.swap').forEach(img => {
    const photos = img.dataset.photos.split(' ');
    let index = +img.dataset.index || 0, path = 0, last = null, loaded = false;
    const next = () => { index = (index + 1) % photos.length; img.src = photos[index]; };
    img.addEventListener('pointerenter', () => {
      if (!loaded) { photos.forEach(src => { new Image().src = src; }); loaded = true; }
      last = null;
    });
    img.addEventListener('pointermove', e => {
      if (e.pointerType !== 'mouse') return;
      if (last) path += Math.hypot(e.clientX - last.x, e.clientY - last.y);
      last = { x: e.clientX, y: e.clientY };
      if (path >= STEP) { path = 0; next(); }
    });
    img.addEventListener('click', next);
  });

  // ---------- размытие ----------
  // depth — какая доля фразы справа размыта, amount — максимальное размытие в em.
  const DEPTH = 0.22, AMOUNT = 0.075;
  const lines = [...document.querySelectorAll('.big .edge')];
  lines.forEach(el => { el.dataset.text = el.textContent.trim(); });

  const blurEdges = (el, depth, amount) => {
    const text = el.dataset.text;
    const chars = [...text];
    const last = Math.max(1, chars.length - 1);
    const html = chars.map((ch, i) => {
      const k = depth > 0 ? Math.max(0, (i / last - (1 - depth)) / depth) : 0;
      const blur = (Math.pow(k, 1.6) * amount).toFixed(3);
      return `<span class="ch" style="filter:blur(${blur}em)">${esc(ch)}</span>`;
    }).join('');
    el.innerHTML = `<span class="edge-sr">${esc(text)}</span><span aria-hidden="true">${html}</span>`;
  };
  const renderBlur = () => {
    const s = settings();
    const depth = s.blurDepth != null ? +s.blurDepth : DEPTH;
    const amount = s.blurAmount != null ? +s.blurAmount : AMOUNT;
    lines.forEach(el => blurEdges(el, depth, amount));
  };
  renderBlur();
  addEventListener('settingschange', renderBlur);

  // ---------- часы ----------
  const clock = document.querySelector('.big .clock');
  if (!clock) return;
  const fmt = new Intl.DateTimeFormat('ru-RU', { timeZone: clock.dataset.tz, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const tick = () => {
    const now = new Date();
    clock.textContent = fmt.format(now);
    clock.dateTime = now.toISOString();
    setTimeout(tick, 1000 - now.getMilliseconds());
  };
  tick();

  // На узком экране фото стоит под часами и равно им по ширине.
  const hero = clock.closest('.hero-b');
  const fitPhoto = () => {
    const range = document.createRange();
    range.selectNodeContents(clock);
    hero.style.setProperty('--clock-w', range.getBoundingClientRect().width + 'px');
  };
  document.fonts.ready.then(fitPhoto);
  addEventListener('resize', fitPhoto);
})();
