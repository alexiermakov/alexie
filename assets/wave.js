// Обо мне: текст в покое, пока по нему не поводят курсором; тогда он колышется, как флаг на ветру,
// тянется к курсору и темнеет в глубине складок, а когда курсор замирает или уходит — успокаивается.
// Блок — полотнище, по которому бежит волна глубины z = A·sin(k·x + q·y − ω·t) (+ слабая вторая гармоника).
// Каждая буква — отдельный inline-block; из z для неё считаются перспективный масштаб (ближе — крупнее),
// сдвиг к центру/от центра (строки выгибаются), сжатие по ширине там, где полотно повёрнуто боком,
// и наклон по касательной к волне. Положение букв в строке задаёт обычная вёрстка, так что переносы
// и выравнивание по центру — как в макете. Для скринридеров остаётся исходный текст, анимированная копия скрыта.
(() => {
  const el = document.querySelector('.wave-text');
  if (!el) return;

  // ---- разбивка на слова и буквы ----
  // В тексте бывают переносы <br> и ссылки <a>: их сохраняем, буквы ссылки остаются внутри неё.
  // Скринридеру — скрытая копия обычного текста, а у ссылки — её собственное название (aria-label).
  const chars = [];
  const source = [...el.childNodes];
  el.textContent = '';
  const plain = document.createElement('span');
  plain.className = 'visually-hidden';
  plain.textContent = source.filter(n => n.nodeName !== 'A').map(n => n.textContent).join(' ').replace(/\s+/g, ' ').trim();
  el.append(plain);
  let gap = false, lineStart = true;   // нужен ли пробел перед следующим словом; начало строки — без пробела
  const words = (str, into) => {
    if (/^\s/.test(str) && !lineStart) gap = true;
    str.split(/\s+/).filter(Boolean).forEach(word => {
      if (gap && into !== el) {            // пробел внутри ссылки — тоже «буква», чтобы подчёркивание шло без разрыва
        const sp = document.createElement('span');
        sp.className = 'ch';
        sp.setAttribute('aria-hidden', 'true');
        sp.textContent = '\u00a0';
        into.append(sp);
        chars.push(sp);
      } else if (gap) into.append(' ');
      const w = document.createElement('span');
      w.className = 'wv';
      w.setAttribute('aria-hidden', 'true');
      for (const c of word) {
        const s = document.createElement('span');
        s.className = 'ch';
        s.textContent = c;
        w.append(s);
        chars.push(s);
      }
      into.append(w);
      gap = true; lineStart = false;
    });
    gap = /\s$/.test(str) || (gap && !str.trim());
  };
  source.forEach(n => {
    if (n.nodeType === 3) words(n.textContent, el);
    else if (n.nodeName === 'BR') { el.append(document.createElement('br')); gap = false; lineStart = true; }
    else if (n.nodeName === 'A') {
      const a = n.cloneNode(false);
      a.setAttribute('aria-label', n.textContent.trim());
      if (gap) { el.append(' '); gap = false; }
      words(n.textContent, a);
      el.append(a);
    }
  });

  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  // ---- параметры волны (в долях размера блока W) ----
  const AMP = 0.095;      // амплитуда глубины
  const PERSP = 1.0;      // расстояние до «камеры»: меньше — сильнее перспектива
  const WAVES = 1.05;     // сколько волн укладывается в ширину блока
  const TILT = 0.35;      // насколько волна идёт наискосок (вклад y)
  const PERIOD = 9;       // секунд на один период основной волны
  const H2 = 0.28;        // доля второй гармоники — чтобы движение не было механическим

  // ---- курсор: полотно вытягивается к нему ----
  const BULGE = 0.26;     // насколько ткань под курсором выпирает к зрителю
  const PULL = 0.12;      // насколько буквы рядом подтягиваются к курсору (больше — сжимает пятно под курсором)
  const RADIUS = 0.16;    // радиус влияния (в долях W)
  const FOLLOW = 0.09;    // плавность: доля пути до курсора за кадр
  const RISE = 0.07;      // как быстро полотно оживает, когда курсор движется по тексту
  const FALL = 0.022;     // как быстро успокаивается, когда курсор замер или ушёл (~2 с)
  const IDLE = 250;       // мс без движения — считаем, что курсор замер
  const MARGIN = 24;      // px вокруг текста, где движение курсора ещё считается «по тексту»

  // ---- тень: чем глубже точка полотна, тем темнее буква ----
  const DARK = 0.22;      // яркость в самой глубокой точке (1 — белый)

  let base = [], W = 1, cx = 0, cy = 0, hw = 0, hh = 0, amp = AMP;
  const measure = () => {
    chars.forEach(s => (s.style.transform = ''));
    const r = el.getBoundingClientRect();
    hw = r.width / 2 + MARGIN; hh = r.height / 2 + MARGIN;
    // масштаб волны — по большей стороне блока, чтобы на узком экране (блок выше, чем шире) не перегибало
    W = Math.max(r.width, r.height); cx = r.left + r.width / 2; cy = r.top + r.height / 2;
    amp = AMP * Math.min(1, Math.max(0.6, r.width / 1033));   // на узких экранах волна мягче
    base = chars.map(s => {
      const b = s.getBoundingClientRect();
      return [b.left + b.width / 2 - cx, b.top + b.height / 2 - cy];
    });
  };

  // курсор в координатах блока (доли W); сглаженная точка догоняет настоящую
  // «Энергия» on (0…1) растёт, пока курсор движется над текстом, и гаснет, когда он замер или ушёл;
  // ею умножаются волна, выпуклость, тяга и тень, и от неё же зависит скорость хода волны.
  let tx = 0, ty = 0, mx = 0, my = 0, on = 0, lastMove = -1e9, phase = 0, prev = 0, resting = true;
  addEventListener('pointermove', e => {
    const ox = e.clientX - cx, oy = e.clientY - cy;
    if (Math.abs(ox) > hw || Math.abs(oy) > hh) return;   // курсор не над текстом
    tx = ox / W; ty = oy / W;
    if (on < 0.01) { mx = tx; my = ty; }   // из покоя — сразу в точку, без пролёта через экран
    lastMove = performance.now();
    if (resting) { resting = false; requestAnimationFrame(frame); }
  }, { passive: true });
  document.documentElement.addEventListener('pointerleave', () => (lastMove = -1e9));
  addEventListener('blur', () => (lastMove = -1e9));

  const k = (2 * Math.PI * WAVES), w1 = (2 * Math.PI) / PERIOD;
  const zMax = AMP * (1 + H2);   // глубина складок волны — по ней нормируем тень (под курсором буквы просто белые)
  const r2 = 2 * RADIUS * RADIUS;

  // Точка полотна (x, y) сначала подтягивается к курсору: (u, v) = (x, y) + PULL·g·(m − p),
  // потом с глубиной z = волна + выпуклость под курсором проецируется в (u·s, v·s), s = P/(P − z).
  // Форму буквы задаёт производная этого отображения (матрица 2×2) — буквы и промежутки между ними
  // растягиваются согласованно, без дыр и наездов.
  function frame(now) {
    const dt = prev ? Math.min(0.1, (now - prev) / 1000) : 0; prev = now;
    const target = now - lastMove < IDLE ? 1 : 0;
    on += (target - on) * (target > on ? RISE : FALL);
    if (!target && on < 0.003) {           // успокоился — возвращаем ровный белый текст и спим до движения
      on = 0; prev = 0; resting = true;
      chars.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
      return;
    }
    phase += dt * on;                       // волна идёт, только пока полотно «живое»
    const t = phase;
    mx += (tx - mx) * FOLLOW; my += (ty - my) * FOLLOW;
    const wa = amp * on, bulge = BULGE * on, pull = PULL * on;
    for (let i = 0; i < chars.length; i++) {
      const x = base[i][0] / W, y = base[i][1] / W;
      // волна
      const p1 = k * x + TILT * k * y - w1 * t;
      const p2 = 1.9 * k * x - 0.6 * k * y - 1.55 * w1 * t + 1.3;
      const c1 = Math.cos(p1), c2 = Math.cos(p2);
      let z = wa * (Math.sin(p1) + H2 * Math.sin(p2));
      const zw = z;
      let zx = wa * k * (c1 + H2 * 1.9 * c2);
      let zy = wa * k * (TILT * c1 - H2 * 0.6 * c2);
      // курсор
      const ax = mx - x, ay = my - y;
      const g = Math.exp(-(ax * ax + ay * ay) / r2);
      const gx = g * ax / (RADIUS * RADIUS), gy = g * ay / (RADIUS * RADIUS);   // ∂g/∂x, ∂g/∂y
      z += bulge * g; zx += bulge * gx; zy += bulge * gy;
      const u = x + pull * g * ax, v = y + pull * g * ay;
      const ux = 1 + pull * (gx * ax - g), uy = pull * gy * ax;
      const vx = pull * gx * ay, vy = 1 + pull * (gy * ay - g);
      // проекция
      const d = PERSP - z, s = PERSP / d;
      const sx = (PERSP * zx) / (d * d), sy = (PERSP * zy) / (d * d);
      const a = ux * s + u * sx, b = vx * s + v * sx;   // ∂X/∂x, ∂Y/∂x
      // ∂X/∂y без перспективной части (u·sy): она даёт буквам «курсивный» скос, на флаге его не видно
      const c = uy * s, e = vy * s + v * sy;            // ∂X/∂y, ∂Y/∂y
      const dx = (u * s - x) * W, dy = (v * s - y) * W;
      const ch = chars[i].style;
      ch.transform = `matrix(${a.toFixed(3)},${b.toFixed(3)},${c.toFixed(3)},${e.toFixed(3)},${dx.toFixed(2)},${dy.toFixed(2)})`;
      // тень по глубине: z от −zMax (дальше всего) до +zMax (ближе всего); в покое — белый
      const depth01 = Math.min(1, Math.max(0, ((z - zw + zw / Math.max(on, 1e-3)) / zMax + 1) / 2));
      const shade = DARK + (1 - DARK) * Math.pow(depth01, 0.8);
      ch.opacity = (1 - on * (1 - shade)).toFixed(3);
    }
    requestAnimationFrame(frame);
  }

  const start = () => measure();
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(start);
  let rt;
  addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(measure, 150); });
  addEventListener('scroll', () => { const r = el.getBoundingClientRect(); cx = r.left + r.width / 2; cy = r.top + r.height / 2; }, { passive: true });
})();
