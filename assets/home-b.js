// Главная: смена фото при движении мыши, часы по Петербургу (вид 2)
// и размытый правый конец крупных строк.
(() => {
  const esc = s => s.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

  // ---------- фото ----------
  // Каждые STEP пикселей пути курсора по фото или ниже его нижнего края показываем
  // следующее фото (над текстом — нет);
  // по клику и тапу на фото — тоже. Стартовое фото случайное, его выбирает встроенный
  // скрипт сразу после разметки. Оба вида главной показывают одно и то же фото.
  const STEP = 70;
  const imgs = [...document.querySelectorAll('img.swap')];
  if (imgs.length) {
    const photos = imgs[0].dataset.photos.split(' ');
    let index = +imgs[0].dataset.index || 0, path = 0, last = null, loaded = false;
    const next = () => {
      index = (index + 1) % photos.length;
      imgs.forEach(img => { img.src = photos[index]; });
    };
    // Курсор в «зоне фото»: на самом видимом фото или ниже его нижней границы.
    const inZone = e => {
      const img = imgs.find(i => i.offsetParent);
      if (!img) return false;
      const r = img.getBoundingClientRect();
      if (e.target.closest && e.target.closest('.big, .about')) return false;
      return e.target === img || e.clientY > r.bottom;
    };
    document.addEventListener('pointermove', e => {
      if (e.pointerType !== 'mouse') return;
      if (!inZone(e)) { last = null; return; }
      if (!loaded) { photos.forEach(src => { new Image().src = src; }); loaded = true; }
      if (last) path += Math.hypot(e.clientX - last.x, e.clientY - last.y);
      last = { x: e.clientX, y: e.clientY };
      if (path >= STEP) { path = 0; next(); }
    });
    document.addEventListener('pointerleave', () => { last = null; });
    imgs.forEach(img => img.addEventListener('click', next));
  }

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
      const blur = Math.pow(k, 1.6) * amount;
      const style = blur > 0 ? ` style="filter:blur(${blur.toFixed(3)}em)"` : '';
      return `<span class="ch"${style}>${esc(ch)}</span>`;
    }).join('');
    el.innerHTML = `<span class="edge-sr">${esc(text)}</span><span aria-hidden="true">${html}</span>`;
  };
  const renderBlur = () => lines.forEach(el => blurEdges(el, DEPTH, AMOUNT));

  // ---------- градиент ----------
  // Диагональный градиент #FF3D20 → #FFD3CC: от начала текста обо мне (сверху слева) к правому
  // нижнему углу часов. Каждой букве задаём свой цвет — точку градиента под её центром.
  // Так нет фона, «вырезанного» по тексту, и браузеру нечего обрезать у плотных строк.
  const C0 = [255, 61, 32], C1 = [255, 211, 204];
  const heroB = document.querySelector('.hero-b');
  const letters = el => {
    el.innerHTML = [...el.textContent].map(ch => `<span class="gc">${esc(ch)}</span>`).join('');
  };
  if (heroB) heroB.querySelectorAll('.about, .big > :not(.edge):not(.clock)').forEach(letters);

  let p0 = [0, 0], d = [1, 1], len2 = 2;
  const measure = () => {
    const about = heroB.querySelector('.about').getBoundingClientRect();
    const range = document.createRange();
    range.selectNodeContents(heroB.querySelector('.big .clock'));
    const end = range.getBoundingClientRect();
    p0 = [about.left, about.top];
    d = [end.right - about.left, end.bottom - about.top];
    len2 = d[0] * d[0] + d[1] * d[1] || 1;
  };
  const paint = spans => spans.forEach(el => {
    const r = el.getBoundingClientRect();
    const t = Math.min(1, Math.max(0, ((r.left + r.width / 2 - p0[0]) * d[0] + (r.top + r.height / 2 - p0[1]) * d[1]) / len2));
    el.style.color = `rgb(${C0.map((v, i) => Math.round(v + (C1[i] - v) * t)).join(',')})`;
  });
  const paintGradient = () => {
    if (!heroB || !heroB.offsetParent) return;
    measure();
    paint(heroB.querySelectorAll('.gc, .big .edge .ch'));
  };

  renderBlur();
  document.fonts.ready.then(paintGradient);
  addEventListener('resize', paintGradient);

  // ---------- часы ----------
  const clock = document.querySelector('.big .clock');
  if (!clock) return;
  const fmt = new Intl.DateTimeFormat('ru-RU', { timeZone: clock.dataset.tz, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const tick = () => {
    const now = new Date();
    clock.textContent = fmt.format(now);
    clock.dateTime = now.toISOString();
    if (heroB && heroB.offsetParent) { letters(clock); paint(clock.querySelectorAll('.gc')); }
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
