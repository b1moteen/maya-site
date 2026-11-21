#!/usr/bin/env python3
"""Build a publishable static site without modifying the preview source."""
import argparse
import html
import ipaddress
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ROBOTS = '<meta name="robots" content="noindex, nofollow">'
PRICE = '<p id="ticket-price" hidden></p>'
CSP = re.compile(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(">)')


def origin_type(value):
    try:
        url = urlsplit(value)
        host = url.hostname
        port = url.port
        if (url.scheme != 'https' or not host or url.username is not None
                or url.password is not None or url.path or url.query or url.fragment
                or value.endswith((':', '?', '#'))):
            raise ValueError
        try:
            ipaddress.ip_address(host)
        except ValueError:
            ascii_host = host.encode('idna').decode('ascii')
            if len(ascii_host) > 253 or not all(
                re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?', label)
                for label in ascii_host.split('.')
            ):
                raise ValueError
        if port is not None and not 1 <= port <= 65535:
            raise ValueError
        return value
    except (ValueError, UnicodeError):
        raise argparse.ArgumentTypeError('нужен HTTPS origin без пути, учётных данных, запроса и фрагмента')


def positive_integer(value):
    if not re.fullmatch(r'[0-9]+', value) or int(value) <= 0:
        raise argparse.ArgumentTypeError('нужно положительное целое число')
    return int(value)


def add_metrika_csp(markup):
    match = CSP.search(markup)
    if not match or len(CSP.findall(markup)) != 1:
        raise ValueError('ожидался один CSP meta-тег')
    directives = [item.strip() for item in match.group(2).split(';') if item.strip()]
    additions = {'script-src': ['https://mc.yandex.ru', 'https://yastatic.net'],
                 'connect-src': ['https://mc.yandex.ru'],
                 'img-src': ['https://mc.yandex.ru']}
    for name, sources in additions.items():
        found = [i for i, d in enumerate(directives) if d.split()[0] == name]
        if len(found) > 1:
            raise ValueError('повторяющаяся директива CSP: ' + name)
        if found:
            tokens = directives[found[0]].split()
            for source in sources:
                if source not in tokens:
                    tokens.append(source)
            directives[found[0]] = ' '.join(tokens)
        else:
            directives.append(name + " 'self' " + ' '.join(sources))
    return markup[:match.start(2)] + '; '.join(directives) + markup[match.end(2):]


def main():
    parser = argparse.ArgumentParser(description='Подготовить папку статического сайта к публикации')
    parser.add_argument('origin', type=origin_type, help='HTTPS origin без пути, например https://example.com')
    parser.add_argument('output', type=Path, help='новая, ещё не существующая папка')
    parser.add_argument('--metrika-id', type=positive_integer)
    parser.add_argument('--from-price', type=positive_integer, help='подтверждённая минимальная цена в рублях')
    args = parser.parse_args()
    destination = args.output.resolve()
    if destination.exists():
        parser.error('папка назначения уже существует')
    try:
        origin = html.escape(args.origin, quote=True)
        routes = (
            ('index.html', '/', 'photo-08.jpg'),
            ('corporate/index.html', '/corporate/', 'photo-10.jpg'),
        )
        pages = {}
        for path, url_path, image in routes:
            markup = (ROOT / path).read_text(encoding='utf-8')
            if markup.count(ROBOTS) != 1:
                raise ValueError('ожидался один исходный noindex meta-тег: ' + path)
            if re.search(r'<(?:link\s+rel="canonical"|meta\s+(?:property="og:(?:url|image)|name="(?:twitter:card|metrika-id)))', markup, re.I):
                raise ValueError('SEO или Метрика уже добавлены в исходник; проверьте шаблон')
            if path == 'index.html':
                if markup.count(PRICE) != 1:
                    raise ValueError('не найдена единственная скрытая строка цены')
                if args.from_price:
                    amount = f'{args.from_price:,}'.replace(',', '\u00a0')
                    markup = markup.replace(PRICE, f'<p id="ticket-price">Билеты от {amount}\u00a0₽</p>')
            tags = [f'<link rel="canonical" href="{origin}{url_path}">',
                    f'<meta property="og:url" content="{origin}{url_path}">',
                    f'<meta property="og:image" content="{origin}/assets/{image}">',
                    '<meta property="og:image:width" content="900">',
                    '<meta property="og:image:height" content="599">',
                    '<meta property="og:image:alt" content="Спектакль «Майя Великолепная»">',
                    '<meta name="twitter:card" content="summary_large_image">']
            if args.metrika_id:
                markup = add_metrika_csp(markup)
                tags.append(f'<meta name="metrika-id" content="{args.metrika_id}">')
            pages[path] = markup.replace(ROBOTS, '\n'.join(tags))
        static_files = ('site.js', 'analytics.js', 'shared.css', 'corporate/corporate.css')
        required = (*static_files, *(f'assets/{image}' for _, _, image in routes))
        for path in required:
            if not (ROOT / path).is_file():
                raise ValueError('отсутствует файл: ' + str(ROOT / path))
        destination.mkdir(parents=True, exist_ok=False)
        try:
            (destination / 'corporate').mkdir()
            for path, markup in pages.items():
                (destination / path).write_text(markup, encoding='utf-8')
            for path in static_files:
                shutil.copy2(ROOT / path, destination / path)
            shutil.copytree(ROOT / 'assets', destination / 'assets')
            (destination / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {args.origin}/sitemap.xml\n', encoding='utf-8')
            locations = ''.join(
                '<url><loc>' + escape(args.origin + url_path) + '</loc></url>'
                for _, url_path, _ in routes
            )
            (destination / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + locations + '</urlset>\n', encoding='utf-8')
            for path in (*pages, *required, 'robots.txt', 'sitemap.xml'):
                if not (destination / path).is_file():
                    raise ValueError('отсутствует файл релиза: ' + path)
        except Exception:
            shutil.rmtree(destination)
            raise
    except (OSError, ValueError) as error:
        parser.exit(1, f'Ошибка сборки: {error}\n')
    print(f'Релиз готов: {destination}')


if __name__ == '__main__':
    main()
