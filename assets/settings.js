// Панель настроек с вкладками по страницам: у главной, списка рассказов и
// страницы чтения свои настройки, тема и акцент — общие для всего сайта.
// Всё хранится в localStorage под ключом settings; ранний скрипт в <head>
// применяет сохранённое до отрисовки страницы.
(() => {
  const root = document.documentElement;
  const page = document.body.classList.contains('home') ? 'home'
    : document.body.classList.contains('list-page') ? 'list'
    : document.querySelector('.reader') ? 'read' : null;

  const ACCENTS = [
    ['#e100c3', 'Маджента'], ['#2f3bff', 'Синий'], ['#ff3b1f', 'Красный'],
    ['#0a9f5a', 'Зелёный'], ['#8c8c8c', 'Серый'],
  ];

  // Настройки, которые сразу пишутся в CSS-переменные.
  const CSS_VARS = { accent: '--accent', scale: '--scale', lh: '--big-lh',
    listSize: '--list-size', listLh: '--list-lh', listAlign: '--list-align', readLh: '--read-lh' };

  let settings = {};
  try { settings = JSON.parse(localStorage.getItem('settings') || '{}'); } catch (e) {}
  const save = () => { try { localStorage.setItem('settings', JSON.stringify(settings)); } catch (e) {} };

  const group = (label, key, def, options, swatch) => `
    <div class="set-row" data-default="${def}">
      <span class="set-label">${label}</span>
      <span class="set-options">${options.map(([value, text]) => swatch
        ? `<button type="button" class="swatch" data-key="${key}" data-value="${value}" title="${text}" aria-label="${text}" style="--c:${value}"></button>`
        : `<button type="button" data-key="${key}" data-value="${value}">${text}</button>`).join('')}</span>
    </div>`;
  const range = (label, key, def, min, max, step) => `
    <label class="set-row">
      <span class="set-label">${label} <output></output></span>
      <input type="range" data-key="${key}" data-default="${def}" min="${min}" max="${max}" step="${step}">
    </label>`;

  const TABS = [
    ['home', 'Главная',
      group('Вид', 'layout', 'b', [['a', 'Вид 1'], ['b', 'Вид 2']]) +
      range('Межстрочное крупного текста', 'lh', '0.79', '0.6', '1.2', '0.01') +
      range('Глубина размытия', 'blurDepth', '0.22', '0', '0.6', '0.01') +
      range('Сила размытия', 'blurAmount', '0.075', '0', '0.3', '0.005')],
    ['list', 'Рассказы',
      range('Размер названий', 'listSize', '1', '0.5', '1.5', '0.01') +
      range('Межстрочное', 'listLh', '0.9', '0.7', '1.3', '0.01') +
      group('Выравнивание', 'listAlign', 'center', [['left', 'Слева'], ['center', 'По центру'], ['right', 'Справа']])],
    ['read', 'Чтение',
      group('Размер текста', 'scale', '1', [['0.9', 'S'], ['1', 'M'], ['1.12', 'L'], ['1.25', 'XL']]) +
      range('Межстрочное', 'readLh', '1.65', '1.2', '2.2', '0.05')],
  ];
  let tab = page || 'home';

  const toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'settings-toggle';
  toggle.setAttribute('aria-label', 'Настройки');
  toggle.title = 'Настройки';
  toggle.innerHTML = '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4.9" stroke-linecap="butt" stroke-linejoin="miter" aria-hidden="true">'
    + '<circle cx="32" cy="32" r="28.5"/><path d="M17 25h30M17 39h30M38 18v14M26 32v14"/></svg>';
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-controls', 'settings-panel');

  const panel = document.createElement('div');
  panel.className = 'settings-panel';
  panel.id = 'settings-panel';
  panel.hidden = true;
  panel.innerHTML =
    `<div class="set-tabs" role="tablist">${TABS.map(([id, name]) =>
      `<button type="button" role="tab" data-tab="${id}">${name}</button>`).join('')}</div>` +
    TABS.map(([id, , html]) => `<div class="set-page" data-page="${id}">${html}</div>`).join('') +
    '<div class="set-common">' +
      group('Тема', 'theme', 'auto', [['auto', 'Авто'], ['light', 'Светлая'], ['dark', 'Тёмная']]) +
      group('Акцент', 'accent', ACCENTS[0][0], ACCENTS, true) +
    '</div>' +
    '<button type="button" class="set-reset">Сбросить</button>';

  const apply = () => {
    if (settings.theme && settings.theme !== 'auto') root.dataset.theme = settings.theme;
    else delete root.dataset.theme;
    if (settings.layout) root.dataset.layout = settings.layout; else delete root.dataset.layout;
    for (const [key, prop] of Object.entries(CSS_VARS)) {
      if (settings[key] != null) root.style.setProperty(prop, settings[key]); else root.style.removeProperty(prop);
    }
    panel.querySelectorAll('[data-tab]').forEach(b => b.setAttribute('aria-selected', String(b.dataset.tab === tab)));
    panel.querySelectorAll('.set-page').forEach(p => { p.hidden = p.dataset.page !== tab; });
    panel.querySelectorAll('input[data-key]').forEach(input => {
      input.value = settings[input.dataset.key] ?? input.dataset.default;
      input.closest('.set-row').querySelector('output').textContent = input.value;
    });
    panel.querySelectorAll('button[data-key]').forEach(b => {
      const value = settings[b.dataset.key] || b.closest('[data-default]').dataset.default;
      b.setAttribute('aria-pressed', String(b.dataset.value === value));
    });
    window.dispatchEvent(new Event('settingschange'));
  };

  document.body.append(toggle, panel);

  const close = () => { panel.hidden = true; toggle.setAttribute('aria-expanded', 'false'); };
  toggle.addEventListener('click', () => {
    panel.hidden = !panel.hidden;
    toggle.setAttribute('aria-expanded', String(!panel.hidden));
  });
  document.addEventListener('click', e => {
    if (!panel.hidden && !panel.contains(e.target) && !toggle.contains(e.target)) close();
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !panel.hidden) { close(); toggle.focus(); }
  });
  panel.addEventListener('input', e => {
    const input = e.target.closest('input[data-key]');
    if (!input) return;
    if (input.value === input.dataset.default) delete settings[input.dataset.key];
    else settings[input.dataset.key] = input.value;
    save();
    apply();
  });
  panel.addEventListener('click', e => {
    const b = e.target.closest('button');
    if (!b) return;
    if (b.dataset.tab) { tab = b.dataset.tab; apply(); return; }
    if (b.classList.contains('set-reset')) {
      // Сбрасываем только открытую вкладку и общие настройки.
      panel.querySelectorAll(`.set-page[data-page="${tab}"] [data-key], .set-common [data-key]`)
        .forEach(el => { delete settings[el.dataset.key]; });
    } else {
      const def = b.closest('[data-default]').dataset.default;
      if (b.dataset.value === def) delete settings[b.dataset.key];
      else settings[b.dataset.key] = b.dataset.value;
    }
    save();
    apply();
  });
  apply();
})();
