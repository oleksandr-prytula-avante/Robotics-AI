"""Static site integrity checks. Run: python3 tests/site_test.py"""
import json
import unittest
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = []
        self.links = []
        self.root = {}
        self.buttons = {}
        self.in_title = False
        self.title = ''
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.root = attrs
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag in ('script', 'img') and 'src' in attrs:
            self.links.append(attrs['src'])
        if tag == 'link' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag == 'button' and 'data-lang' in attrs:
            self.buttons[attrs['data-lang']] = attrs.get('aria-pressed')
        if tag == 'title':
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


PAGES = {p.resolve(): Page(p) for p in ROOT.rglob('*.html')}


class SiteTests(unittest.TestCase):
    def test_english_defaults_and_titles_on_every_page(self):
        self.assertTrue(PAGES)
        for path, page in PAGES.items():
            with self.subTest(page=str(path.relative_to(ROOT))):
                self.assertEqual(page.root.get('lang'), 'en')
                self.assertEqual(page.title, page.root['data-en-title'])
                self.assertEqual(page.buttons, {'ru': 'false', 'en': 'true'})
                self.assertEqual(len(page.ids), len(set(page.ids)), 'Duplicate HTML IDs')

    def test_local_files_and_anchors(self):
        for path, page in PAGES.items():
            for href in page.links:
                parts = urlsplit(href)
                if parts.scheme or parts.netloc:
                    continue
                with self.subTest(page=str(path.relative_to(ROOT)), href=href):
                    target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
                    if target.is_dir():
                        target = target / 'index.html'
                    self.assertTrue(target.is_file(), f'Missing file: {target}')
                    if parts.fragment and target in PAGES:
                        self.assertIn(unquote(parts.fragment), PAGES[target].ids)

    def test_procurement_budget_and_owned_assets(self):
        data = json.loads((ROOT / 'procurement.json').read_text())
        items = {item['id']: item for item in data['items']}
        self.assertEqual(len(items), len(data['items']))
        self.assertTrue({'MacBook Pro', 'Creality Print'}.issubset({x['name'] for x in data['owned']}))
        self.assertTrue(any(x['kind'] == 'printer' for x in data['owned']))
        self.assertTrue(all(x['purchase_quantity'] == 0 and x['ownership_confirmed'] for x in data['owned']))
        subtotal = Decimal('0')
        unpriced = 0
        for row in data['first_basket']:
            item = items[row['id']]
            self.assertGreater(row['quantity'], 0)
            if item['price'] is None:
                unpriced += 1
            else:
                self.assertEqual(item['currency'], 'UAH')
                subtotal += Decimal(str(item['price'])) * row['quantity']
        self.assertEqual(subtotal, Decimal(str(data['first_basket_subtotal_uah'])))
        self.assertEqual(unpriced, data['first_basket_unpriced_rows'])
        self.assertEqual(data['baseline_hours_unchanged'], 2960)
        page = PAGES[ROOT / 'procurement.html']
        for item in items.values():
            self.assertIn('item-' + item['id'], page.ids)
            for field in ['title', 'quantity_text', 'compatibility', 'timing'] + (['notes'] if any((item['notes'] or {}).values()) else []):
                self.assertTrue(item[field]['ru'].strip())
                self.assertTrue(item[field]['en'].strip())
        report = json.loads((ROOT / 'procurement-verification.json').read_text())
        self.assertEqual(report['product_rows'], len(items))
        self.assertEqual(report['first_basket_subtotal_uah'], float(subtotal))
        self.assertEqual(report['first_basket_unpriced_rows'], unpriced)

    def test_json_and_calendar_totals(self):
        for path in ROOT.glob('*.json'):
            with self.subTest(path=path.name):
                json.loads(path.read_text())
        schedule = json.loads((ROOT / 'schedule.json').read_text())
        self.assertEqual(schedule['base_hours'] + schedule['contingency_hours'], 2960)
        self.assertEqual(schedule['allocated_hours'], 2960)
        self.assertEqual(schedule['calendar_capacity_hours'], 3045)
        self.assertEqual(schedule['unallocated_hours'], 85)


if __name__ == '__main__':
    unittest.main()
