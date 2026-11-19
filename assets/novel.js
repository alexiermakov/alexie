// Роман: полоса прогресса чтения и меню глав.
// — Меню (и кнопка на телефоне) появляется, когда первый экран с названием ушёл вверх.
// — Подсвечивается глава, которую сейчас читают.
// — На телефоне круглая кнопка открывает и закрывает список; закрывается и по выбору главы,
//   по нажатию мимо и по Esc.
(() => {
  // полоса прогресса чтения сверху — как на страницах рассказов
  const bar = document.getElementById('progress');
  if (bar) {
    const onScroll = () => {
      const max = document.documentElement.scrollHeight - innerHeight;
      bar.style.width = (max > 0 ? Math.min(1, scrollY / max) * 100 : 0) + '%';
    };
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll);
    onScroll();
  }

  // просмотры страницы романа (abacus.jasoncameron.dev): на alexie.ru первый заход за сессию
  // прибавляет 1, повторные и локальные просмотры только читают число. Нет ответа — строка скрыта.
  const views = document.querySelector('.novel-views');
  if (views) {
    let counted = false;
    try { counted = sessionStorage.getItem('novel-viewed') === '1'; } catch (e) {}
    const live = location.hostname === 'alexie.ru' || location.hostname === 'www.alexie.ru';
    const op = live && !counted ? 'hit' : 'get';
    fetch(`https://abacus.jasoncameron.dev/${op}/alexie.ru/novel`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(d => {
        if (typeof d.value !== 'number') return;
        if (op === 'hit') { try { sessionStorage.setItem('novel-viewed', '1'); } catch (e) {} }
        views.querySelector('.novel-views-n').textContent = d.value.toLocaleString('ru-RU');
        views.setAttribute('aria-label', `Просмотров: ${d.value}`);
        views.hidden = false;
      })
      .catch(() => {});
  }

  const nav = document.getElementById('chapters');
  const btn = document.querySelector('.chapters-btn');
  const first = document.querySelector('.novel-first');
  if (!nav || !btn) return;
  const body = document.body;
  const links = [...nav.querySelectorAll('a')];
  const sections = links.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);

  // показать меню после первого экрана
  if (first) {
    new IntersectionObserver(([e]) => {
      body.classList.toggle('chapters-on', !e.isIntersecting);
      if (e.isIntersecting) setOpen(false);
    }).observe(first);
  } else body.classList.add('chapters-on');

  // текущая глава — последняя, чьё начало уже выше середины экрана
  const mark = () => {
    const mid = innerHeight * 0.4;
    let cur = 0;
    sections.forEach((s, i) => { if (s.getBoundingClientRect().top <= mid) cur = i; });
    links.forEach((a, i) => a.setAttribute('aria-current', i === cur ? 'true' : 'false'));
    // на кнопке содержания (телефон): до 1 главы — книжка, дальше — номер текущей главы
    const n = cur > 0 ? links[cur].querySelector('.nav-n') : null;
    if (n) { btn.dataset.num = n.textContent; btn.querySelector('.chapters-num').textContent = n.textContent; }
    else delete btn.dataset.num;
  };
  let ticking = false;
  addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { mark(); ticking = false; });
  }, { passive: true });
  addEventListener('resize', mark);
  mark();

  // телефон: открыть / закрыть список
  function setOpen(open) {
    nav.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  btn.addEventListener('click', e => { e.stopPropagation(); setOpen(!nav.classList.contains('open')); });
  links.forEach(a => a.addEventListener('click', () => setOpen(false)));
  document.addEventListener('click', e => { if (!nav.contains(e.target)) setOpen(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') setOpen(false); });
})();
