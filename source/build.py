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
    чтобы она не уезжала на новую строку."""
    chars = list(title)
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
    words.append(word + (',' if comma else ''))
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
  <a class="toc-back" href="../" aria-label="На главную">
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="butt" stroke-linejoin="miter" aria-hidden="true">
      <circle cx="32" cy="32" r="29"/>
      <path d="M45 32H20M30 21 19 32l11 11"/>
    </svg>
  </a>
</main>

{foot('../')}
</body>
</html>
""")

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
            {'@type': 'ListItem', 'position': 2, 'name': 'Рассказы', 'item': SITE + '/stories/'},
            {'@type': 'ListItem', 'position': 3, 'name': s['title'], 'item': SITE + path}]},
    ]}
    body = '\n'.join(f'      <p>{escape(p)}</p>' for p in s['paras'])
    write(f"stories/{s['slug']}/index.html", head(title, clip(s['synopsis']), path, '../../', 'article', schema)
          + f'''
<body id="top">
<div class="progress" id="progress"></div>

<main>
  <article class="reader">
    <aside class="meta">
      <div class="num">{s['n']:02d}.</div>
      <dl>
        <dt>Жанр</dt><dd>{s['genre']}</dd>
        <dt>Объём</dt><dd>{thousands(s['words'])} {plural(s['words'], 'слово', 'слова', 'слов')}</dd>
        <dt>Чтение</dt><dd>{minutes(s['words'])} мин</dd>
      </dl>
      <a href="../" class="back">← Все рассказы</a>
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
