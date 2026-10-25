# Лёша Е. — рассказы

Сайт писателя: главная страница и шесть рассказов. Статический HTML, без фреймворков, готов для GitHub Pages.

## Структура

```
index.html                 главная: портрет и оглавление
stories/<slug>/index.html  отдельная страница каждого рассказа
404.html                   страница «не найдено»
assets/                    стили, фото, картинка для соцсетей, иконка
favicon.svg
sitemap.xml, robots.txt    для поисковиков
source/                    исходники: тексты, настройки, сборщик
```

## Публикация на GitHub Pages

1. Создайте репозиторий на GitHub и загрузите в него содержимое этой папки.
2. Settings → Pages → Source: **Deploy from a branch**, ветка `main`, папка `/ (root)`.
3. Впишите адрес сайта в `source/config.json` (`site_url`) и пересоберите — см. ниже.
   Адрес вида `https://ИМЯ.github.io/РЕПОЗИТОРИЙ` или `https://ИМЯ.github.io`,
   если репозиторий называется `ИМЯ.github.io`.

## Как изменить тексты или настройки

Тексты лежат в `source/stories.json`, адрес сайта, подпись, жанры и ссылки — в `source/config.json`.
После правок пересоберите страницы:

```bash
python3 source/build.py
```

## Поисковики

- Google Search Console и Яндекс Вебмастер: добавьте сайт, подтвердите права
  (коды можно вписать в `google_site_verification` и `yandex_verification` в `config.json`
  и пересобрать), затем отправьте `sitemap.xml`.
