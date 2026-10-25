"""Собирает статический сайт из source/stories.json и source/config.json.

Запуск из корня репозитория:  python3 source/build.py
"""
import json
import os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source')

cfg = json.load(open(os.path.join(SRC, 'config.json'), encoding='utf-8'))
stories = json.load(open(os.path.join(SRC, 'stories.json'), encoding='utf-8'))
for s, meta in zip(stories, cfg['stories']):
    s.update(meta)

SITE = cfg['site_url'].rstrip('/')
AUTHOR = cfg['author']
AUTHOR_GEN = cfg['author_genitive']
YEAR = cfg['year']
FONTS = 'https://fonts.googleapis.com/css2?family=Geist:wght@400;500&display=swap'


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


def head(title, description, path, prefix, og_type, schema):
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
<script>try {{ const t = localStorage.getItem('theme'); if (t) document.documentElement.dataset.theme = t; }} catch (e) {{}}</script>
<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="preload" href="{prefix}assets/fonts/lebowski-regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{prefix}assets/style.css">
<script src="{prefix}assets/theme.js" defer></script>
{ld(schema)}
</head>'''


def bar(prefix, is_home):
    name = (f'<h1><a href="{prefix}" class="name">{AUTHOR}</a></h1>' if is_home
            else f'<a href="{prefix}" class="name">{AUTHOR}</a>')
    return f'''<header class="bar">
  {name}
  <a href="{prefix}#index">Рассказы</a>
  <span class="mute">Короткая проза</span>
  <button class="theme-toggle" type="button">Тёмная тема</button>
</header>'''


FOOT = f'''<footer class="foot">
  <span>© {YEAR} {AUTHOR}</span>
  <span>Все права защищены</span>
  <span></span>
  <a href="#top">Наверх ↑</a>
</footer>'''


def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(html)


# ---------- home ----------
rows = '\n'.join(f'''    <li class="row">
      <button class="row-main" type="button" aria-expanded="false">
        <span class="tag">{s['genre']}</span>
        <span class="num">{s['n']:02d}.</span>
        <span class="title">{escape(s['title'])}</span>
        <span class="time">{minutes(s['words'])} мин</span>
      </button>
      <div class="row-more">
        <p>{escape(s['synopsis'])}</p>
        <a class="read" href="stories/{s['slug']}/">Читать рассказ «{escape(s['title'])}» →</a>
      </div>
    </li>''' for s in stories)

home_schema = {'@context': 'https://schema.org', '@graph': [
    WEBSITE, PERSON,
    {'@type': 'ItemList', 'name': 'Рассказы', 'itemListElement': [
        {'@type': 'ListItem', 'position': s['n'], 'url': f"{SITE}/stories/{s['slug']}/", 'name': s['title']}
        for s in stories]},
]}
home_desc = (f'{AUTHOR} — короткая проза. Шесть рассказов: '
             + ', '.join(f'«{s["title"]}»' for s in stories) + '. Читать онлайн.')

write('index.html', head(f'{AUTHOR} — рассказы, короткая проза', clip(home_desc, 200), '/', '', 'website', home_schema)
      + f'''
<body id="top">
{bar('', True)}

<main>
  <section class="hero">
    <p class="caps">{escape(cfg['tagline'])}</p>
    <figure class="portrait"><img src="assets/photo.jpg" alt="{AUTHOR}, портрет" width="900" height="1200"></figure>
    <a href="#index" class="scroll mute">Шесть рассказов ↓</a>
  </section>

  <section class="index" id="index" aria-labelledby="index-title">
    <h2 class="visually-hidden" id="index-title">Рассказы</h2>
    <div class="index-head" aria-hidden="true">
      <span>Жанр</span><span>№</span><span>Название</span><span style="justify-self:end">Время чтения</span>
    </div>
    <ol class="list" id="list">
{rows}
    </ol>
  </section>
</main>

{FOOT}

<noscript><style>.row-more {{ max-height: none; }}</style></noscript>
<script>
  const list = document.getElementById('list');
  list.addEventListener('click', e => {{
    const btn = e.target.closest('.row-main');
    if (!btn) return;
    const row = btn.parentElement;
    const open = !row.classList.contains('open');
    list.querySelectorAll('.row.open').forEach(r => {{ r.classList.remove('open'); r.firstElementChild.setAttribute('aria-expanded', 'false'); }});
    if (open) {{ row.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); }}
  }});
</script>
</body>
</html>
''')

# ---------- stories ----------
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
            {'@type': 'ListItem', 'position': 2, 'name': s['title'], 'item': SITE + path}]},
    ]}
    body = '\n'.join(f'      <p>{escape(p)}</p>' for p in s['paras'])
    write(f"stories/{s['slug']}/index.html", head(title, clip(s['synopsis']), path, '../../', 'article', schema)
          + f'''
<body id="top">
<div class="progress" id="progress"></div>
{bar('../../', False)}

<main>
  <article class="reader">
    <aside class="meta">
      <div class="num">{s['n']:02d}.</div>
      <dl>
        <dt>Жанр</dt><dd>{s['genre']}</dd>
        <dt>Объём</dt><dd>{thousands(s['words'])} {plural(s['words'], 'слово', 'слова', 'слов')}</dd>
        <dt>Чтение</dt><dd>{minutes(s['words'])} мин</dd>
      </dl>
      <a href="../../#index" class="back">← Все рассказы</a>
    </aside>
    <div class="text">
      <h1>{escape(s['title'])}</h1>
      <p class="byline">{AUTHOR}, {YEAR}</p>
{body}
      <p class="end">Конец</p>
    </div>
  </article>
  <nav class="next" aria-label="Следующий рассказ"><a href="../{nx['slug']}/"><span class="label">Следующий рассказ</span><span class="title">{escape(nx['title'])}</span></a></nav>
</main>

{FOOT}

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
<script>try {{ const t = localStorage.getItem('theme'); if (t) document.documentElement.dataset.theme = t; }} catch (e) {{}}</script>
<script src="{SITE}/assets/theme.js" defer></script>
</head>
<body>
<header class="bar">
  <a href="{SITE}/" class="name">{AUTHOR}</a>
  <a href="{SITE}/#index">Рассказы</a>
  <span class="mute">Короткая проза</span>
  <button class="theme-toggle" type="button">Тёмная тема</button>
</header>
<main class="notfound">
  <p class="mute">404</p>
  <h1>Ни в коем случае не касайся этой страницы</h1>
  <a href="{SITE}/">Вернуться к рассказам</a>
</main>
</body>
</html>
''')

# ---------- sitemap & robots ----------
urls = [('/', '1.0')] + [(f"/stories/{s['slug']}/", '0.8') for s in stories]
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n'
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + ''.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{cfg["updated"]}</lastmod><priority>{p}</priority></url>\n'
                for u, p in urls)
      + '</urlset>\n')
write('robots.txt', f'User-agent: *\nAllow: /\nDisallow: /source/\n\nSitemap: {SITE}/sitemap.xml\n')

print(f'Готово: {len(stories)} рассказов, адрес сайта {SITE}')
