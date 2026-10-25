// Переключатель темы: без сохранённого выбора сайт следует системной настройке.
(() => {
  const root = document.documentElement;
  const dark = matchMedia('(prefers-color-scheme: dark)');
  const current = () => root.dataset.theme || (dark.matches ? 'dark' : 'light');
  const buttons = document.querySelectorAll('.theme-toggle');
  const label = () => buttons.forEach(b => {
    b.textContent = current() === 'dark' ? 'Светлая тема' : 'Тёмная тема';
  });
  buttons.forEach(b => b.addEventListener('click', () => {
    const next = current() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (e) {}
    label();
  }));
  dark.addEventListener('change', label);
  label();
})();
