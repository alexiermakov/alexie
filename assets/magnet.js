// Магнитные круглые кнопки («домой», «назад»): когда курсор попадает в квадрат вокруг
// кнопки, она плавно тянется к нему и следует за ним; за пределами — мягко возвращается.
(() => {
  const btns = [...document.querySelectorAll('.round-btn')];
  if (!btns.length || matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const ZONE = 2.6;   // полуразмер зоны в размерах кнопки (квадрат ~5 кнопок в ширину)
  const PULL = 0.45;  // насколько сильно кнопка тянется к курсору
  const EASE = 0.14;  // плавность: чем меньше, тем мягче догоняет

  const state = btns.map(el => ({ el, x: 0, y: 0, tx: 0, ty: 0 }));
  let raf = 0;

  const loop = () => {
    let moving = false;
    for (const s of state) {
      s.x += (s.tx - s.x) * EASE;
      s.y += (s.ty - s.y) * EASE;
      if (Math.abs(s.tx - s.x) > 0.1 || Math.abs(s.ty - s.y) > 0.1) moving = true;
      s.el.style.transform = `translate3d(${s.x.toFixed(2)}px, ${s.y.toFixed(2)}px, 0)`;
    }
    raf = moving ? requestAnimationFrame(loop) : 0;
  };
  const kick = () => { if (!raf) raf = requestAnimationFrame(loop); };

  document.addEventListener('pointermove', e => {
    if (e.pointerType !== 'mouse') return;
    for (const s of state) {
      const r = s.el.getBoundingClientRect();
      // центр кнопки без текущего смещения
      const cx = r.left + r.width / 2 - s.x, cy = r.top + r.height / 2 - s.y;
      const dx = e.clientX - cx, dy = e.clientY - cy, half = r.width * ZONE;
      const inside = Math.abs(dx) < half && Math.abs(dy) < half;
      s.tx = inside ? dx * PULL : 0;
      s.ty = inside ? dy * PULL : 0;
    }
    kick();
  });
  // курсор ушёл из окна — кнопки возвращаются на место
  document.documentElement.addEventListener('mouseleave', () => { state.forEach(s => { s.tx = s.ty = 0; }); kick(); });
})();
