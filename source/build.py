"""Собирает статический сайт из source/stories.json и source/config.json.

Запуск из корня репозитория:  python3 source/build.py
"""
import json
import os
import random
import re
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source')

cfg = json.load(open(os.path.join(SRC, 'config.json'), encoding='utf-8'))
stories = json.load(open(os.path.join(SRC, 'stories.json'), encoding='utf-8'))
for s, meta in zip(stories, cfg['stories']):
    s.update(meta)

# ---------- типографика ----------
NBSP = '\u00a0'
# Короткие слова, которые не должны висеть в конце строки: всё длиной до двух букв
# (кроме частиц — они прилипают назад) плюс трёхбуквенные предлоги и союзы.
HANGING = re.compile(r'(?<![\w-])(?!(?:же|ли|ль|бы)(?![\w-]))(\w{1,2}|без|для|над|под|при|про|обо|изо|ото|меж|что|как|или)\s+(?=\S)',
                     re.IGNORECASE)
# Частицы прилипают к предыдущему слову.
PARTICLES = re.compile(r'\s+(же|ли|ль|бы|б)(?![\w-])', re.IGNORECASE)


def typo(text):
    """Неразрывные пробелы: после коротких слов, перед частицами и тире, между числом и словом."""
    text = re.sub(r'\s+—', NBSP + '—', text)
    text = re.sub(r'(\d)\s+(?=[^\W\d])', r'\1' + NBSP, text)
    text = PARTICLES.sub(lambda m: NBSP + m.group(1), text)
    prev = None
    while prev != text:  # повторяем, чтобы склеить цепочки вроде «и в»
        prev = text
        text = HANGING.sub(lambda m: m.group(1) + NBSP, text)
    return text


for s in stories:
    s['paras'] = [typo(p) for p in s['paras']]
    for key in ('title', 'synopsis', 'quote'):
        s[key] = typo(s[key])
for key in ('about', 'tagline'):
    cfg[key] = typo(cfg[key])

SITE = cfg['site_url'].rstrip('/')
AUTHOR = cfg['author']
AUTHOR_GEN = cfg['author_genitive']
YEAR = cfg['year']
FONTS = 'https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap'


def minutes(words):
    return max(1, round(words / 180))


def plural(n, one, few, many):
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 10 <= n % 100 < 20:
        return few
    return many


def thousands(n):
    return format(n, ',').replace(',', '\u00a0')


def clip(text, limit=158):
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(' ', 1)[0].rstrip(' ,.;:—-')
    return cut + '…'


def ld(data):
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            + '</script>')


PERSON = {'@type': 'Person', '@id': SITE + '/#author', 'name': AUTHOR, 'url': SITE + '/',
          'image': SITE + '/assets/photo.jpg'}
WEBSITE = {'@type': 'WebSite', '@id': SITE + '/#website', 'name': f'{AUTHOR} — рассказы',
           'url': SITE + '/', 'inLanguage': 'ru', 'author': {'@id': SITE + '/#author'}}


def head(title, description, path, prefix, og_type, schema, extra=''):
    url = SITE + path
    verify = ''
    if cfg.get('google_site_verification'):
        verify += f'\n<meta name="google-site-verification" content="{escape(cfg["google_site_verification"])}">'
    if cfg.get('yandex_verification'):
        verify += f'\n<meta name="yandex-verification" content="{escape(cfg["yandex_verification"])}">'
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<meta name="author" content="{escape(AUTHOR)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">{verify}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{escape(AUTHOR)} — рассказы">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f0f0ef" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#121212" media="(prefers-color-scheme: dark)">
<script>try {{ const s = JSON.parse(localStorage.getItem('settings') || '{{}}'), r = document.documentElement; if (s.theme && s.theme !== 'auto') r.dataset.theme = s.theme; if (s.layout) r.dataset.layout = s.layout; const v = {{ accent: '--accent', scale: '--scale', lh: '--big-lh', listSize: '--list-size', listLh: '--list-lh', listAlign: '--list-align', readLh: '--read-lh' }}; for (const k in v) if (s[k] != null) r.style.setProperty(v[k], s[k]); }} catch (e) {{}}</script>
<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">{extra}
<link rel="preload" href="{prefix}assets/fonts/lebowski-regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{prefix}assets/style.css">
<script src="{prefix}assets/settings.js" defer></script>
{ld(schema)}
</head>'''


def foot(prefix):
    return f'''<footer class="foot">
  <a href="{prefix}">© {YEAR} {AUTHOR}</a>
  <span>Все права защищены</span>
</footer>'''


def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(html)


# ---------- home ----------
home_schema = {'@context': 'https://schema.org', '@graph': [
    WEBSITE, PERSON,
    {'@type': 'ItemList', 'name': 'Рассказы', 'itemListElement': [
        {'@type': 'ListItem', 'position': s['n'], 'url': f"{SITE}/stories/{s['slug']}/", 'name': s['title']}
        for s in stories]},
]}
home_desc = (f'{AUTHOR} — короткая проза. Шесть рассказов: '
             + ', '.join(f'«{s["title"]}»' for s in stories) + '. Читать онлайн.')

PHOTOS = ' '.join(f'assets/photos/{i}.jpg' for i in range(1, 6))
CITY = escape(cfg['city']).replace('-', '\u2011')  # неразрывный дефис
write('index.html', head(f'{AUTHOR} — рассказы, короткая проза', clip(home_desc, 200), '/', '', 'website', home_schema)
      + f'''
<body id="top" class="home">

<main>
  <h1 class="visually-hidden">{AUTHOR} — рассказы</h1>
  <section class="hero">
    <p class="caps">{escape(cfg['tagline'])}</p>
    <figure class="portrait"><img class="swap" src="assets/photos/1.jpg" data-photos="{PHOTOS}" alt="{AUTHOR}, портрет" width="900" height="1200"></figure>
    <a href="stories/" class="scroll">Рассказы 01–06 →</a>
  </section>

  <section class="hero-b" aria-label="Об авторе">
    <p class="about">{escape(cfg['about'])}</p>
    <div class="hero-b-grid">
      <img class="swap" src="assets/photos/1.jpg" data-photos="{PHOTOS}" alt="{AUTHOR}, портрет" width="900" height="1200">
      <p class="big">
        <span>{AUTHOR}</span>
        <a class="edge" href="stories/">Рассказы 01–06</a>
        <span class="edge">{CITY}</span>
        <time class="clock" data-tz="{cfg['timezone']}" aria-label="Время в Петербурге">--:--:--</time>
      </p>
    </div>
  </section>
  <script>
    // Случайное фото при каждой загрузке, не повторяя прошлое.
    (() => {{
      const imgs = document.querySelectorAll('img.swap');
      const n = imgs[0].dataset.photos.split(' ').length;
      let last = -1;
      try {{ last = parseInt(localStorage.getItem('photo'), 10); }} catch (e) {{}}
      let i = Math.floor(Math.random() * (last >= 0 && last < n ? n - 1 : n));
      if (last >= 0 && last < n && i >= last) i++;
      imgs.forEach(img => {{ img.src = img.dataset.photos.split(' ')[i]; img.dataset.index = i; }});
      try {{ localStorage.setItem('photo', i); }} catch (e) {{}}
    }})();
  </script>

</main>

{foot('')}

<script src="assets/home-b.js" defer></script>
</body>
</html>
''')


# ---------- stories list: one flowing paragraph of titles ----------
BLUR_DEPTH, BLUR_AMOUNT = 0.22, 0.075  # как на главной по умолчанию


def title_html(n, title, comma):
    """Название по буквам: у последних букв задано размытие --b, оно включается при наведении.
    Слова не разрываются, номер склеен с первым словом, а запятая — с последним,
    чтобы она не уезжала на новую строку; размывается вместе с буквами."""
    chars = list(title + (',' if comma else ''))
    last = max(1, len(chars) - 1)
    words, word = [], ''
    for i, ch in enumerate(chars):
        if ch == ' ':
            words.append(word)
            word = ''
            continue
        k = max(0.0, (i / last - (1 - BLUR_DEPTH)) / BLUR_DEPTH)
        blur = k ** 1.6 * BLUR_AMOUNT
        word += f'<span class="ch" style="--b:{blur:.3f}em">{escape(ch)}</span>' if blur > 0 else escape(ch)
    words.append(word)
    words = [f'<span class="w">{w}</span>' for w in words]
    words[0] = f'<span class="toc-lead"><span class="toc-num">{n:02d}.</span>\u00a0{words[0]}</span>'
    return ' '.join(words)


toc = '\n'.join(f"""    <a href="{s['slug']}/" title="{escape(s['synopsis'])}" aria-label="{s['n']:02d}. {escape(s['title'])}">"""
                  f"""{title_html(s['n'], s['title'], s is not stories[-1])}</a>"""
                  for s in stories)

list_schema = {'@context': 'https://schema.org', '@graph': [
    {'@type': 'CollectionPage', 'name': 'Рассказы', 'url': SITE + '/stories/', 'inLanguage': 'ru',
     'isPartOf': {'@id': SITE + '/#website'}, 'author': {'@id': SITE + '/#author'},
     'mainEntity': {'@type': 'ItemList', 'itemListElement': [
         {'@type': 'ListItem', 'position': s['n'], 'url': f"{SITE}/stories/{s['slug']}/", 'name': s['title']}
         for s in stories]}},
    PERSON,
    {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': AUTHOR, 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Рассказы', 'item': SITE + '/stories/'}]},
]}
list_desc = (f'Рассказы {AUTHOR_GEN}: '
             + ', '.join(f'«{s["title"]}»' for s in stories) + '.')

write('stories/index.html', head(f'Рассказы — {AUTHOR}', clip(list_desc, 200), '/stories/', '../', 'website', list_schema)
      + f"""
<body id="top" class="list-page">

<main class="toc">
  <h1 class="visually-hidden">Рассказы</h1>
  <p class="toc-list">
{toc}
  </p>
  <a class="round-btn" href="../" aria-label="На главную">
    <svg viewBox="0 0 64 64" aria-hidden="true">
      <circle cx="32" cy="32" r="32" fill="currentColor"/>
      <path d="M32 21.5 42 30v11.5H22V30z" fill="var(--paper)"/>
    </svg>
  </a>
</main>

{foot('../')}
</body>
</html>
""")

# ---------- stories ----------
SEPARATORS = ['✱', '†', '§', '⁂', '‡', '❋', '※', '✳']

for i, s in enumerate(stories):
    nx = stories[(i + 1) % len(stories)]
    path = f"/stories/{s['slug']}/"
    title = f"{s['title']} — рассказ {AUTHOR_GEN} | читать онлайн"
    schema = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'ShortStory', '@id': SITE + path + '#story', 'name': s['title'], 'headline': s['title'],
         'url': SITE + path, 'description': s['synopsis'], 'genre': s['genre'], 'inLanguage': 'ru',
         'wordCount': s['words'], 'timeRequired': f"PT{minutes(s['words'])}M",
         'datePublished': YEAR, 'dateModified': cfg['updated'],
         'image': SITE + '/assets/og.jpg', 'isAccessibleForFree': True,
         'author': PERSON, 'isPartOf': {'@id': SITE + '/#website'}},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': AUTHOR, 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Рассказы', 'item': SITE + '/stories/'},
            {'@type': 'ListItem', 'position': 3, 'name': s['title'], 'item': SITE + path}]},
    ]}
    # Первый абзац — крупный лид; после абзаца с цитатой из config.json — выносная цитата.
    quoted = next(i for i, p in enumerate(s['paras']) if s['quote'] in p)
    # «***» в тексте — разбивка: по центру, каждый раз другой символ (выбор стабилен между сборками).
    rnd, glyph = random.Random(s['slug']), None
    blocks = []
    for i, p in enumerate(s['paras']):
        if p.strip() == '***':
            glyph = rnd.choice([g for g in SEPARATORS if g != glyph])
            blocks.append(f'      <div class="sep" role="separator"><span aria-hidden="true">{glyph}</span></div>')
            continue
        blocks.append(f'      <p class="lead">{escape(p)}</p>' if i == 0 else f'      <p>{escape(p)}</p>')
        if i == quoted:
            blocks.append(f'      <blockquote class="pull" aria-hidden="true">«{escape(s["quote"].rstrip("."))}»</blockquote>')
    body = '\n'.join(blocks)
    write(f"stories/{s['slug']}/index.html", head(title, clip(s['synopsis']), path, '../../', 'article', schema)
          + f'''
<body id="top" class="read-page">
<div class="progress" id="progress"></div>

<main>
  <article class="reader">
    <aside class="meta">
      <div class="num">{s['n']:02d}</div>
      <dl>
        <dt>Жанр</dt><dd>{s['genre']}</dd>
        <dt>Объём</dt><dd>{thousands(s['words'])} {plural(s['words'], 'слово', 'слова', 'слов')}</dd>
        <dt>Чтение</dt><dd>{minutes(s['words'])} мин</dd>
      </dl>
    </aside>
    <div class="text">
      <h1>{escape(s['title'])}</h1>
      <p class="byline">{AUTHOR}, {YEAR}</p>
{body}
      <p class="end">Конец</p>
    </div>
  </article>
  <a class="round-btn round-btn-left" href="../" aria-label="Все рассказы">
    <svg viewBox="0 0 64 64" aria-hidden="true">
      <circle cx="32" cy="32" r="32" fill="currentColor"/>
      <path d="M19 32 31 20v8h14v8H31v8z" fill="var(--paper)"/>
    </svg>
  </a>
  <nav class="next" aria-label="Следующий рассказ"><a href="../{nx['slug']}/"><span class="label">Следующий рассказ</span><span class="title">{escape(nx['title'])}</span></a></nav>
</main>

{foot('../../')}

<script>
  const bar = document.getElementById('progress');
  const onScroll = () => {{
    const max = document.documentElement.scrollHeight - innerHeight;
    bar.style.width = (max > 0 ? Math.min(1, scrollY / max) * 100 : 0) + '%';
  }};
  addEventListener('scroll', onScroll, {{ passive: true }});
  onScroll();
</script>
</body>
</html>
''')

# ---------- 404 ----------
write('404.html', f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Страница не найдена — {AUTHOR}</title>
<meta name="robots" content="noindex">
<link rel="icon" href="{SITE}/favicon.svg" type="image/svg+xml">
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{SITE}/assets/style.css">
<meta name="theme-color" content="#f0f0ef" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#121212" media="(prefers-color-scheme: dark)">
<script>try {{ const s = JSON.parse(localStorage.getItem('settings') || '{{}}'), r = document.documentElement; if (s.theme && s.theme !== 'auto') r.dataset.theme = s.theme; if (s.layout) r.dataset.layout = s.layout; const v = {{ accent: '--accent', scale: '--scale', lh: '--big-lh', listSize: '--list-size', listLh: '--list-lh', listAlign: '--list-align', readLh: '--read-lh' }}; for (const k in v) if (s[k] != null) r.style.setProperty(v[k], s[k]); }} catch (e) {{}}</script>
<script src="{SITE}/assets/settings.js" defer></script>
</head>
<body>
<main class="notfound">
  <p class="mute">404</p>
  <h1>Ни в коем случае не касайся этой страницы</h1>
  <a href="{SITE}/stories/">Вернуться к рассказам</a>
</main>
</body>
</html>
''')

# ---------- sitemap & robots ----------
urls = [('/', '1.0'), ('/stories/', '0.9')] + [(f"/stories/{s['slug']}/", '0.8') for s in stories]
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n'
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + ''.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{cfg["updated"]}</lastmod><priority>{p}</priority></url>\n'
                for u, p in urls)
      + '</urlset>\n')
write('robots.txt', f'User-agent: *\nAllow: /\nDisallow: /source/\n\nSitemap: {SITE}/sitemap.xml\n')

print(f'Готово: {len(stories)} рассказов, адрес сайта {SITE}')
