#!/usr/bin/env python3
"""
Effretikon Restaurant Menü Scraper
Sammelt und zeigt Tagesmenüs von Restaurants in Effretikon an.
"""

import requests
import re
import io
from bs4 import BeautifulSoup
from datetime import datetime, date
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import Dict, List, Optional
import sys

try:
    import pypdf
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    import cloudscraper as _cloudscraper
    CLOUDSCRAPER_SUPPORT = True
except ImportError:
    CLOUDSCRAPER_SUPPORT = False

try:
    import pytesseract as _pytesseract
    import os as _os
    import shutil as _shutil

    # Resolve tesseract binary: ENV > shutil.which > known paths
    _tess_candidates = [
        _os.environ.get('TESSERACT_CMD'),
        _shutil.which('tesseract'),
        r'C:\Program Files\Tesseract-OCR\tesseract.exe' if _os.name == 'nt' else None,
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
    ]
    _tess_cmd = next((p for p in _tess_candidates if p and _os.path.isfile(p)), None)
    if _tess_cmd:
        _pytesseract.pytesseract.tesseract_cmd = _tess_cmd
        print(f'[OCR] tesseract_cmd = {_tess_cmd}')
    else:
        print('[OCR] WARNING: tesseract binary not found in any known path')
    OCR_SUPPORT = True
except ImportError:
    OCR_SUPPORT = False


def _to_sentence_case(text: str) -> str:
    """Wandelt GROSSBUCHSTABEN-Text in normalen Satzbau um."""
    if not text:
        return text
    if text == text.upper():
        return text.capitalize()
    return text


class MenuScraper:
    """Basis-Klasse für Restaurant-Menü-Scraper"""
    
    def __init__(self, name: str, url: str, address: str):
        self.name = name
        self.url = url
        self.address = address
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'de-CH,de;q=0.9,en;q=0.8',
        })
    
    def get_menu(self) -> Dict[str, any]:
        """Sammelt Menü-Informationen vom Restaurant"""
        raise NotImplementedError("Subclass must implement get_menu()")
    
    def fetch_page(self, url: str = None) -> Optional[BeautifulSoup]:
        """Holt und parst eine Webseite"""
        try:
            response = self.session.get(url or self.url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"Fehler beim Laden von {self.name}: {e}")
            return None

    def fetch_pdf_bytes(self, url: str) -> Optional[bytes]:
        """Lädt eine PDF-Datei herunter"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Fehler beim Laden des PDFs von {self.name}: {e}")
            return None

    def _error_result(self, message: str) -> Dict:
        return {
            'restaurant': self.name,
            'address': self.address,
            'status': message,
            'menus': [],
            'website': self.url,
        }


class BellissimoScraper(MenuScraper):
    """Scraper für Ristorante Bellissimo da Edi - Tagesmenüs direkt von der Website"""

    # German month names → month number
    _MONTHS_DE = {
        'januar': 1, 'februar': 2, 'märz': 3, 'april': 4,
        'mai': 5, 'juni': 6, 'juli': 7, 'august': 8,
        'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12,
    }

    @classmethod
    def _parse_date_de(cls, text: str) -> Optional[date]:
        """Parst deutsches Datum aus Text. Erkennt z.B.:
        'Donnerstag, 16. April 2026', '16.04.2026', '16. April 2026'
        """
        import re as _re
        text = text.strip()

        # DD.MM.YYYY
        m = _re.search(r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b', text)
        if m:
            try:
                return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except ValueError:
                pass

        # DD. MonatName YYYY  (optional weekday prefix)
        m = _re.search(r'\b(\d{1,2})\.\s+([A-Za-zÄäÖöÜüß]+)\s+(\d{4})\b', text)
        if m:
            month_num = cls._MONTHS_DE.get(m.group(2).lower())
            if month_num:
                try:
                    return date(int(m.group(3)), month_num, int(m.group(1)))
                except ValueError:
                    pass

        return None

    def get_menu(self) -> Dict[str, any]:
        soup = self.fetch_page()
        if not soup:
            return self._error_result('Website nicht erreichbar')

        # Bellissimo uses Elementor - each menu is a 'type-tagesmenu' post element.
        # The first element is the date/intro, subsequent ones are individual menu items.
        menu_elements = soup.find_all(class_='type-tagesmenu')
        if not menu_elements:
            return self._error_result('Keine Menü-Elemente gefunden')

        # First element contains the date and intro text
        date_text = ''
        intro_text = ''
        first_texts = [t.strip() for t in menu_elements[0].get_text(separator='|').split('|')
                       if t.strip() and len(t.strip()) > 2]
        if first_texts:
            date_text = first_texts[0]
            intro_text = first_texts[1] if len(first_texts) > 1 else ''

        # Validate: if the menu date is from a past day, don't show it
        if date_text:
            menu_date = self._parse_date_de(date_text)
            if menu_date is not None and menu_date < datetime.now().date():
                return self._error_result(
                    f'Menü noch nicht aktualisiert (vom {date_text})'
                )

        # Remaining elements are individual menus: [title, italian_name, german_desc, price]
        menus = []
        for elem in menu_elements[1:]:
            parts = [t.strip() for t in elem.get_text(separator='|').split('|')
                     if t.strip() and len(t.strip()) > 2]
            if len(parts) >= 2:
                title = parts[0]
                italian_name = _to_sentence_case(parts[1]) if len(parts) > 1 else ''
                german_desc = parts[2] if len(parts) > 2 else ''
                price = parts[3] if len(parts) > 3 else ''
                menus.append({
                    'title': title,
                    'description': italian_name,
                    'details': german_desc,
                    'price': f'CHF {price}' if price else '',
                })

        return {
            'restaurant': self.name,
            'address': self.address,
            'status': f'Menüs vom {date_text}' if date_text else 'Aktuelle Menüs',
            'price': 'CHF 22.50–28.50',
            'menus': menus,
            'phone': '044 534 32 25',
            'website': self.url,
            'note': intro_text,
        }


class QNWorldScraper(MenuScraper):
    """Scraper für QN World Restaurant - Mittagsmenü von der Website"""

    def get_menu(self) -> Dict[str, any]:
        soup = self.fetch_page()
        if not soup:
            return self._error_result('Website nicht erreichbar')

        today_str = datetime.now().strftime('%d/%m/%Y')
        date_divs = soup.find_all('div', class_='menu-list-title')

        # Find today's date section
        today_section = None
        for div in date_divs:
            span = div.find('span')
            if span and span.get_text(strip=True) == today_str:
                today_section = div
                break

        if not today_section:
            # Show the most recent date as fallback
            if date_divs:
                today_section = date_divs[-1]
                date_shown = today_section.find('span')
                date_label = date_shown.get_text(strip=True) if date_shown else '?'
                status = f'Kein Menü für heute gefunden – zuletzt: {date_label}'
            else:
                return self._error_result('Keine Menüs gefunden')
        else:
            status = f'Menüs vom {today_str}'

        # Parse the table following the date header
        table = today_section.find_next('table', class_='table')
        if not table:
            return self._error_result('Keine Menü-Tabelle gefunden')

        menus = []
        current_menu = None
        current_items = []
        current_price = None

        for row in table.find_all('tr'):
            th = row.find('th')
            td_price = row.find('td', class_=lambda c: c and 'price-total' in c)
            td_item_price = row.find('td', class_=lambda c: c and 'price' in c and 'price-total' not in c)

            if th and not td_item_price and not td_price:
                # This is a menu category header (Menu 1, Menu 2, ...)
                th_text = th.get_text(strip=True)
                if re.search(r'[Mm]en[uü]', th_text):
                    # Save previous menu if any
                    if current_menu and current_items:
                        menus.append({
                            'title': current_menu,
                            'description': ' | '.join(current_items),
                            'price': f'CHF {current_price}' if current_price else '',
                        })
                    current_menu = th_text
                    current_items = []
                    current_price = None
                else:
                    current_items.append(th_text)
            elif th and td_item_price:
                # Item with price
                item_text = th.get_text(strip=True)
                price = td_item_price.get_text(strip=True)
                if price and price != '0.00':
                    current_items.append(f'{item_text} (CHF {price})')
                else:
                    current_items.append(item_text)
            elif td_price:
                # Total price row
                current_price = td_price.get_text(strip=True)

        # Save the last menu
        if current_menu and current_items:
            menus.append({
                'title': current_menu,
                'description': ' | '.join(current_items),
                'price': f'CHF {current_price}' if current_price else '',
            })

        return {
            'restaurant': self.name,
            'address': self.address,
            'status': status,
            'price': 'CHF 24–52',
            'menus': menus,
            'phone': '052 355 38 38',
            'website': self.url,
        }


class StrickhofScraper(MenuScraper):
    """Scraper für Strickhof Mensa Lindau - Wochenmenü via PDF"""

    PDF_URL = 'https://www.strickhof.ch/wp-content/uploads/2020/08/Aktuelles-Menue-Lindau.pdf'

    DAY_MAP = {0: 'MO', 1: 'DI', 2: 'MI', 3: 'DO', 4: 'FR'}

    def get_menu(self) -> Dict[str, any]:
        today = datetime.now()
        weekday = today.weekday()

        if weekday > 4:
            return self._error_result('Mensa am Wochenende geschlossen')

        if not PDF_SUPPORT:
            return self._error_result('PDF-Bibliothek nicht installiert (pip install pypdf)')

        pdf_bytes = self.fetch_pdf_bytes(self.PDF_URL)
        if not pdf_bytes:
            return self._error_result('PDF nicht abrufbar')

        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text = '\n'.join(page.extract_text() for page in reader.pages)
        except Exception as e:
            return self._error_result(f'PDF-Parsing-Fehler: {e}')

        return self._parse_pdf_for_day(text, weekday)

    def _parse_pdf_for_day(self, text: str, weekday: int) -> Dict:
        day_abbr = self.DAY_MAP[weekday]
        days_ordered = ['MO', 'DI', 'MI', 'DO', 'FR']
        day_index = days_ordered.index(day_abbr)

        # Split text into day sections using day abbreviations as delimiters
        pattern = r'\n(' + '|'.join(days_ordered) + r')\s*\n'
        parts = re.split(pattern, text)

        # parts alternates: [preamble, DAY, content, DAY, content, ...]
        day_sections = {}
        for i in range(1, len(parts) - 1, 2):
            day_key = parts[i].strip()
            day_content = parts[i + 1].strip() if i + 1 < len(parts) else ''
            day_sections[day_key] = day_content

        if day_abbr not in day_sections:
            return self._error_result('Kein Menü für heute im PDF gefunden')

        section = day_sections[day_abbr]
        lines = [l.strip() for l in section.split('\n') if l.strip()]

        # Extract week date range from preamble
        date_match = re.search(r'\d+\.\s+bis\s+\d+\.\s+\w+\s+\d{4}', text)
        week_dates = date_match.group(0) if date_match else ''

        # The PDF columns are: VORSPEISE | MITTAGESSEN | MITTAGESSEN VEGI | DESSERT | ...
        # We reconstruct meaningful menu items from the line sequence.
        # Structure: lines describe courses in order across columns.
        # We extract what's relevant for lunch visitors (Mittagessen + Vegi + Dessert).
        menus = []

        # Heuristic: group lines into logical courses (3-5 lines each)
        # Column headers from PDF: VORSPEISE MITTAGESSEN MITTAGESSEN VEGI DESSERT NACHTESSEN NACHTESSEN VEGI
        all_text = ' '.join(lines)

        # Try to find Mittagessen and Vegi sections by looking at relative positions
        # The text flows left-to-right, column by column in PDF extraction
        menus.append({
            'title': 'Mittagessen',
            'description': self._extract_lunch(lines, vegetarian=False),
            'price': 'CHF 24',
        })
        menus.append({
            'title': 'Mittagessen Vegetarisch',
            'description': self._extract_lunch(lines, vegetarian=True),
            'price': 'CHF 24',
        })

        return {
            'restaurant': self.name,
            'address': self.address,
            'status': f'Woche: {week_dates}' if week_dates else 'Aktuelles Wochenmenü',
            'price': 'CHF 24',
            'menus': menus,
            'phone': '058 105 98 00',
            'website': 'https://www.strickhof.ch/campus/gastronomie/gastronomie-lindau/',
            'note': 'Extern: CHF 23 Hauptgang, je +CHF 1 für Vorspeise/Dessert. Lernende CHF 9, Mitarbeitende CHF 11.',
        }

    def _extract_lunch(self, lines: List[str], vegetarian: bool) -> str:
        """Heuristic extraction of lunch lines from PDF text."""
        # The PDF text flows: Vorspeise lines, then Mittagessen lines, then Vegi lines, etc.
        # We detect vegi-specific words as indicators.
        vegi_keywords = ['tofu', 'vegi', 'planted', 'gemüse-', 'blumenkohl', 'quorn',
                         'randen', 'quinoa', 'grill-käse', 'bio']
        meat_keywords = ['fleisch', 'steak', 'poulet', 'schwein', 'rind', 'kalbf',
                         'schnitzel', 'hackfleisch', 'burger', 'geschnetzeltes']

        result_lines = []
        for line in lines:
            lower = line.lower()
            is_vegi = any(k in lower for k in vegi_keywords)
            is_meat = any(k in lower for k in meat_keywords)

            if vegetarian and (is_vegi or (not is_meat and len(result_lines) < 3)):
                result_lines.append(line)
            elif not vegetarian and (is_meat or (not is_vegi and len(result_lines) < 3)):
                result_lines.append(line)

        if not result_lines:
            result_lines = lines[:4]

        return ' | '.join(result_lines[:4])


class CasaLindaScraper(MenuScraper):
    """Scraper für Casa Linda – BÜEZERMENÜ aus dem Mittagsmenü-PDF"""

    def get_menu(self) -> Dict[str, any]:
        if not CLOUDSCRAPER_SUPPORT:
            return self._error_result('cloudscraper nicht installiert (pip install cloudscraper)')
        if not PDF_SUPPORT:
            return self._error_result('pypdf nicht installiert (pip install pypdf)')

        try:
            scraper = _cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
            )
            r = scraper.get(self.url, timeout=15)
            r.raise_for_status()
        except Exception as e:
            return self._error_result(f'Website nicht erreichbar: {e}')

        soup = BeautifulSoup(r.content, 'lxml')

        # Find the "Mittagsmenüs" link (Jimdo storage PDF, no .pdf extension)
        pdf_url = None
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True).lower()
            if 'mittag' in text and 'jimdo' in href.lower():
                pdf_url = href
                break
        # Fallback: any jimdo storage link with MITTAGSMEN in URL
        if not pdf_url:
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'jimdo' in href.lower() and 'mittag' in href.lower().replace('%c3%bc', 'ü'):
                    pdf_url = href
                    break

        if not pdf_url:
            return self._error_result('Kein Mittagsmenü-PDF-Link gefunden')

        try:
            pdf_resp = scraper.get(pdf_url, timeout=15)
            pdf_resp.raise_for_status()
            pdf_bytes = pdf_resp.content
        except Exception as e:
            return self._error_result(f'PDF nicht ladbar: {e}')

        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text = '\n'.join(page.extract_text() for page in reader.pages)
        except Exception as e:
            return self._error_result(f'PDF-Parsing-Fehler: {e}')

        return self._parse_buezermenus(text, pdf_url)

    def _parse_buezermenus(self, text: str, pdf_url: str) -> Dict:
        """Extrahiert das BÜEZERMENÜ (Mittagsmenü inkl. Suppe/Salat) aus dem PDF-Text."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        # Find PDF month/title for status
        title_match = re.search(r'MITTAGSMEN[ÜU]\s+(\w+)', text, re.IGNORECASE)
        month_label = title_match.group(1).capitalize() if title_match else ''

        # Locate the BÜEZERMENÜ section
        buezer_start = None
        for i, line in enumerate(lines):
            if re.search(r'B[ÜU]EZERMEN[ÜU]', line, re.IGNORECASE):
                buezer_start = i
                break

        if buezer_start is None:
            return self._error_result('BÜEZERMENÜ-Abschnitt im PDF nicht gefunden')

        # Collect lines until the next major section header (FLEISCH, PAN DE, etc.)
        section_end_re = re.compile(
            r'^(FLEISCH|PAN DE|VORSPEISEN|DESSERT|WARENHERK|PLATO)', re.IGNORECASE
        )
        buezer_lines = []
        for line in lines[buezer_start + 1:]:
            if section_end_re.match(line):
                break
            buezer_lines.append(line)

        # Parse menu items: NAME + optional subtitle + PRICE on same or next line
        # Pattern: line with price at end (e.g. "Cordon Bleu                  25.00")
        price_inline = re.compile(r'^(.+?)\s{2,}([\d]{2,3}\.\d{2})\s*$')
        # Or price on its own line
        price_only = re.compile(r'^([\d]{2,3}\.\d{2})\s*$')

        menus = []
        i = 0
        while i < len(buezer_lines):
            line = buezer_lines[i]

            # Skip "Suppe oder Salat inkl." marker lines
            if re.search(r'suppe|salat inkl', line, re.IGNORECASE):
                i += 1
                continue

            m = price_inline.match(line)
            if m:
                name = m.group(1).strip()
                price = m.group(2)
                # Peek at next line for description
                desc = ''
                if i + 1 < len(buezer_lines):
                    next_line = buezer_lines[i + 1]
                    if not price_inline.match(next_line) and not price_only.match(next_line):
                        desc = next_line
                        i += 1
                menus.append({
                    'title': name,
                    'description': desc,
                    'price': f'CHF {price}',
                })
                i += 1
                continue

            # No inline price — check if next line is just a price
            if i + 1 < len(buezer_lines) and price_only.match(buezer_lines[i + 1]):
                name = line
                price = buezer_lines[i + 1]
                desc = ''
                if i + 2 < len(buezer_lines):
                    nxt = buezer_lines[i + 2]
                    if not price_inline.match(nxt) and not price_only.match(nxt):
                        desc = nxt
                        i += 1
                menus.append({
                    'title': name,
                    'description': desc,
                    'price': f'CHF {price}',
                })
                i += 2
                continue

            i += 1

        status = f'Mittagsmenü {month_label}' if month_label else 'Aktuelles Mittagsmenü'
        return {
            'restaurant': self.name,
            'address': self.address,
            'status': status,
            'price': 'CHF 22.50–25.50',
            'menus': menus,
            'phone': '052 347 16 30',
            'website': self.url,
            'note': 'Inkl. Suppe oder Salat',
        }


class DaZiaMariaScraper(MenuScraper):
    """Scraper für Da Zia Maria – Tagesmenüs direkt aus der Website (Divi/WordPress)"""

    def get_menu(self) -> Dict[str, any]:
        soup = self.fetch_page()
        if not soup:
            return self._error_result('Website nicht erreichbar')

        # The menus live in the section immediately after id="tagesmenue"
        anchor = soup.find(id='tagesmenue')
        if not anchor:
            return self._error_result('Tagesmenü-Abschnitt nicht gefunden')

        menu_section = anchor.find_next_sibling()
        if not menu_section:
            return self._error_result('Menü-Abschnitt nach Anker nicht gefunden')

        # Date is in the first text module
        date_text = ''
        date_el = menu_section.find('p')
        if date_el:
            date_text = date_el.get_text(strip=True)

        # Each menu is inside an et_pb_column – one column per menu item
        menus = []
        for col in menu_section.find_all('div', class_='et_pb_column'):
            text_inner = col.find('div', class_='et_pb_text_inner')
            if not text_inner:
                continue

            h3 = text_inner.find('h3')
            if not h3:
                continue
            title = h3.get_text(strip=True)
            if not title or '★' in title:
                continue

            # Italian name (bold paragraph)
            italian = ''
            bold = text_inner.find('b')
            if bold:
                italian = bold.get_text(strip=True)

            # German translation (h6)
            german = ''
            h6 = text_inner.find('h6')
            if h6:
                german = h6.get_text(strip=True).strip('()')

            # Price
            price = ''
            for p in text_inner.find_all('p'):
                txt = p.get_text(strip=True)
                if txt.startswith('CHF'):
                    price = txt
                    break

            description = italian
            if german:
                description += f' – {german}'

            if title and description:
                menus.append({
                    'title': title,
                    'description': description,
                    'price': price,
                })

        status = f'Menüs vom {date_text}' if date_text else 'Aktuelle Tagesmenüs'
        return {
            'restaurant': self.name,
            'address': self.address,
            'status': status,
            'price': 'CHF 19.50–24.50',
            'menus': menus,
            'phone': '044 536 06 95',
            'website': self.url,
            'note': 'Täglich 4 Menüs inkl. Menüsalat',
        }


class TheValleyScraper(MenuScraper):
    """Scraper für Restaurant The Valley (Migros) – Wochenmenüplan als PDF"""

    BASE_URL = 'https://www.restaurant-thevalley.ch'
    # Column headers from the PDF, in order of appearance
    MENU_CATEGORIES = ['Mittags-Menu', 'Mittags-Hit', 'Klassiker am Grill',
                       'Chef empfiehlt', 'Power Bowl']

    def get_menu(self) -> Dict[str, any]:
        today = datetime.now()
        if today.weekday() > 4:
            return self._error_result('Restaurant am Wochenende geschlossen')

        if not PDF_SUPPORT:
            return self._error_result('PDF-Bibliothek nicht installiert (pip install pypdf)')

        # Find the current-week PDF link from the website
        pdf_url = self._find_pdf_url()
        if not pdf_url:
            return self._error_result('PDF-Link nicht gefunden')

        pdf_bytes = self.fetch_pdf_bytes(pdf_url)
        if not pdf_bytes:
            return self._error_result('PDF nicht abrufbar')

        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            # Page 0 = menus, Page 1 = weekly salad
            text = reader.pages[0].extract_text()
        except Exception as e:
            return self._error_result(f'PDF-Parsing-Fehler: {e}')

        return self._parse_today(text, today, pdf_url)

    def _find_pdf_url(self) -> Optional[str]:
        """Liest die aktuelle Woche-PDF-URL von der Website."""
        soup = self.fetch_page()
        if not soup:
            return None
        for a in soup.find_all('a', href=True):
            href = a['href']
            label = a.get_text(strip=True).lower()
            if '.pdf' in href.lower() and 'menueplan-1-de' in href.lower():
                return href if href.startswith('http') else self.BASE_URL + href
        # Fallback: first German PDF
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '.pdf' in href.lower() and '-de.pdf' in href.lower():
                return href if href.startswith('http') else self.BASE_URL + href
        return None

    def _parse_today(self, text: str, today: datetime, pdf_url: str) -> Dict:
        today_str = today.strftime('%d.%m.%Y')

        # Split text into per-day sections using "Weekday,\nDD.MM.YYYY" as delimiter
        parts = re.split(r'(\w+,\n\d{2}\.\d{2}\.\d{4})', text)

        today_content = None
        for i in range(1, len(parts) - 1, 2):
            if today_str in parts[i]:
                today_content = parts[i + 1] if i + 1 < len(parts) else ''
                break

        if today_content is None:
            return self._error_result(f'Kein Eintrag für {today_str} im PDF')

        menus = self._parse_menu_items(today_content)

        # Extract week date range from header
        date_match = re.search(r'\d{2}\.\d{2}\.\d{4}\s*-\s*\d{2}\.\d{2}\.\d{4}', text)
        week_dates = date_match.group(0) if date_match else ''

        return {
            'restaurant': self.name,
            'address': self.address,
            'status': f'Woche: {week_dates}' if week_dates else f'Menü vom {today_str}',
            'price': 'CHF 15.90–25.90',
            'menus': menus,
            'phone': '044 908 08 10',
            'website': self.url,
            'note': f'Vollständiger Menüplan: {pdf_url}',
        }

    def _parse_menu_items(self, content: str) -> List[Dict]:
        """Gruppiert aufeinanderfolgende Zeilen zu Menüeinträgen anhand der Preiszeile."""
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        price_pattern = re.compile(r'^\d+\.\d{2}\s*/\s*1\s*CU')

        menus = []
        current_lines = []

        for line in lines:
            if price_pattern.match(line):
                # Price line closes the current item
                price = line.split('/')[0].strip()
                if current_lines:
                    # First line = title, rest = description
                    title_candidate = current_lines[0]
                    desc_parts = current_lines[1:]
                    # Remove fish/origin info lines (e.g. "Fisch: Aquakultur...")
                    desc_parts = [p for p in desc_parts if not p.startswith('Fisch:')]
                    description = ' '.join(desc_parts)
                    # Detect vegetarian/vegan tag
                    tags = []
                    if 'Vegetarisch' in description:
                        tags.append('🌱 Vegetarisch')
                        description = description.replace('Vegetarisch', '').strip()
                    if 'Vegan' in description:
                        tags.append('🌿 Vegan')
                        description = description.replace('Vegan', '').strip()

                    cat_idx = len(menus)
                    category = (self.MENU_CATEGORIES[cat_idx]
                                if cat_idx < len(self.MENU_CATEGORIES) else f'Menü {cat_idx + 1}')

                    menus.append({
                        'title': f'{category}: {title_candidate}',
                        'description': description,
                        'price': f'CHF {price}',
                        'tags': tags,
                    })
                current_lines = []
            else:
                current_lines.append(line)

        return menus


class PuraVidaScraper(MenuScraper):
    """Scraper für Tagesrestaurant Pura Vida – OCR des Wochenmenü-Bildes auf der Jimdo-Website."""

    SITE_URL = 'https://www.restaurant-riet.ch/'
    GERMAN_DAYS = {0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch',
                   3: 'Donnerstag', 4: 'Freitag'}
    MONTHS_DE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

    def get_menu(self) -> Dict[str, any]:
        today = datetime.now()
        if today.weekday() > 4:
            return self._error_result('Restaurant am Wochenende geschlossen')

        if not CLOUDSCRAPER_SUPPORT:
            return self._error_result('cloudscraper nicht installiert (pip install cloudscraper)')
        if not OCR_SUPPORT:
            return self._error_result('pytesseract nicht installiert (pip install pytesseract)')

        # Fetch page bypassing Cloudflare
        try:
            scraper = _cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
            )
            r = scraper.get(self.SITE_URL, timeout=20)
            r.raise_for_status()
        except Exception as e:
            return self._error_result(f'Website nicht erreichbar: {e}')

        soup = BeautifulSoup(r.content, 'lxml')

        # Find all full-resolution images (srcset contains transf/none)
        menu_img_url = self._find_menu_image(soup)
        if not menu_img_url:
            return self._error_result('Menü-Bild auf der Website nicht gefunden')

        # Download the image
        try:
            img_resp = scraper.get(menu_img_url, timeout=15)
            img_resp.raise_for_status()
            img_bytes = img_resp.content
        except Exception as e:
            return self._error_result(f'Menü-Bild nicht ladbar: {e}')

        # OCR mit Spalten-Trennung
        self._ocr_error = None
        ocr = self._ocr_image(img_bytes)
        if not ocr:
            err = getattr(self, '_ocr_error', None) or 'unbekannter Fehler'
            return self._error_result(f'OCR fehlgeschlagen: {err}')

        return self._parse_menu(ocr, today)

    def _find_menu_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Sucht das Wochenplan-Bild anhand des srcset (transf/none) auf der Seite."""
        for img in soup.find_all('img'):
            srcset = img.get('srcset', '')
            src = img.get('src', '')
            for part in (srcset + ',' + src).split(','):
                part = part.strip()
                if 'transf/none' in part and 'jimcdn' in part:
                    url = part.split(' ')[0]
                    # Normalise: ensure ?-version param or path version present
                    if '/image/' in url and '/version/' in url:
                        return url
        return None

    def _ocr_image(self, img_bytes: bytes) -> Optional[Dict]:
        """OCR mit Spalten-Trennung via Bounding-Boxes.
        Gibt {'left': [...], 'right': [...], 'all': [...]} zurück.
        Jedes Element hat {'text': str, 'y': int}.
        """
        try:
            from PIL import Image
            import io as _io
            import os

            # Set TESSDATA_PREFIX for Windows (user tessdata folder)
            if os.name == 'nt':
                user_tessdata = os.path.expanduser('~/tessdata')
                if os.path.isdir(user_tessdata):
                    os.environ.setdefault('TESSDATA_PREFIX', user_tessdata)
            else:
                # Linux: try common apt-installed paths
                for candidate in [
                    '/usr/share/tesseract-ocr/4.00/tessdata',
                    '/usr/share/tesseract-ocr/5.00/tessdata',
                    '/usr/share/tessdata',
                ]:
                    if os.path.isdir(candidate):
                        os.environ.setdefault('TESSDATA_PREFIX', candidate)
                        break

            img = Image.open(_io.BytesIO(img_bytes)).convert('RGB')
            w, h = img.size
            if w < 1000:
                img = img.resize((w * 2, h * 2), Image.LANCZOS)
                w, h = img.size

            # Full merged text for Wochen Angebot section (below table)
            full_text = _pytesseract.image_to_string(img, lang='deu', config='--psm 6')
            all_lines = [l.strip() for l in full_text.split('\n') if l.strip()]

            # Word-level bounding boxes to separate left/right columns
            data = _pytesseract.image_to_data(
                img, lang='deu', config='--psm 6',
                output_type=_pytesseract.Output.DICT
            )

            # Table split: left column (days+meat) ends at ~52% of width
            split_x = int(w * 0.52)
            left_d: Dict = {}
            right_d: Dict = {}

            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if not text:
                    continue
                conf = data['conf'][i]
                try:
                    if int(conf) < 15:
                        continue
                except (ValueError, TypeError):
                    pass
                key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
                x = data['left'][i]
                y = data['top'][i]
                bucket = left_d if x < split_x else right_d
                entry = bucket.setdefault(key, {'words': [], 'y': y})
                entry['words'].append((x, text))

            def reconstruct(line_dict: Dict) -> List[Dict]:
                result = []
                for key in sorted(line_dict.keys()):
                    entry = line_dict[key]
                    words = sorted(entry['words'], key=lambda t: t[0])
                    line = ' '.join(w for _, w in words).strip()
                    if line:
                        result.append({'text': line, 'y': entry['y']})
                return result

            return {
                'left': reconstruct(left_d),
                'right': reconstruct(right_d),
                'all': all_lines,
            }
        except Exception as e:
            import traceback
            print(f'OCR Fehler bei Thalegg: {e}\n{traceback.format_exc()}')
            # Store error so get_menu can surface it
            self._ocr_error = str(e)
            return None

    def _parse_menu(self, ocr: Dict, today: datetime) -> Dict:
        """Parst die OCR-Spalten und extrahiert:
        - Tages-Fleischgericht (linke Spalte, tagabhängig)
        - 2 Vegi-Gerichte (rechte Spalte, ganze Woche)
        - Fitnesteller (rechte Spalte, tagabhängig nach Reihenfolge)
        - 2 Pasta-Gerichte (rechte Spalte, ganze Woche)
        - Wochen-Angebot Gerichte (unterhalb der Tabelle)
        """
        today_name = self.GERMAN_DAYS.get(today.weekday(), '')
        day_names = list(self.GERMAN_DAYS.values())
        price_re = re.compile(r'\bFr\.?\s*([\d]{2,3}\.\d{2})', re.IGNORECASE)

        # --- Header-Preise aus linker/rechter Spalte ---
        header_price = {'menu': 'CHF 22.50', 'vegi': 'CHF 20.50'}
        for item in (ocr['left'] + ocr['right'])[:12]:
            line = item['text']
            m = re.search(r'Men.?\s+Fr\.?\s*([\d.]+)', line, re.IGNORECASE)
            if m:
                header_price['menu'] = f'CHF {m.group(1)}'
            v = re.search(r'Vegi\s+Fr\.?\s*([\d.]+)', line, re.IGNORECASE)
            if v:
                header_price['vegi'] = f'CHF {v.group(1)}'

        def fuzzy_day_match(line: str) -> Optional[str]:
            ll = line.lower()
            for day in day_names:
                if ll[:5] == day[:5].lower() or (
                    len(ll) >= 4 and
                    sum(a != b for a, b in zip(ll[:6], day.lower()[:6])) <= 1
                ):
                    return day
            return None

        # --- LINKE SPALTE: Tages-Fleischgerichte ---
        sections: Dict[str, List[str]] = {}
        current_day = None

        for item in ocr['left']:
            line = item['text']
            if re.search(r'wochen\s*angebot', line, re.IGNORECASE):
                break
            matched = fuzzy_day_match(line)
            if matched:
                current_day = matched
                sections[current_day] = []
                trailing = re.sub(
                    r'^(?:' + '|'.join(day_names) + r')[^,]*,?\s*\d{1,2}\.\s*\w+\s*\d{4}\s*',
                    '', line, flags=re.IGNORECASE
                ).strip()
                if trailing and len(trailing) > 4:
                    sections[current_day].append(trailing)
            elif current_day:
                if re.match(r'^\d{1,2}[\.\- ]+\w+\s+\d{4}$', line):
                    continue
                if len(line) > 4 and not re.match(r'^[\W\d\s]+$', line):
                    sections[current_day].append(line)

        today_meat_lines = [
            l for l in sections.get(today_name, [])
            if len(l) > 4 and not re.match(r'^[\W\d\s]+$', l)
            and not re.match(r'^\+?[\d\s\-/]+$', l)
        ]

        # --- RECHTE SPALTE: Vegi + Fitnesteller + Pasta ---
        vegi_raw: List[str] = []
        fitness_options: List[str] = []
        fitness_price = 'CHF 24.50'
        wurst_item: Optional[Dict] = None
        pasta_items: List[Dict] = []

        state = 'header'

        for item in ocr['right']:
            line = item['text']
            ll = line.lower()

            if re.search(r'wochen\s*angebot', ll, re.IGNORECASE):
                break

            # Abschnittserkennung
            if re.search(r'vegi\s+fr', ll, re.IGNORECASE):
                state = 'vegi'
                v = re.search(r'Vegi\s+Fr\.?\s*([\d.]+)', line, re.IGNORECASE)
                if v:
                    header_price['vegi'] = f'CHF {v.group(1)}'
                continue

            if re.search(r'fitnesteller', ll, re.IGNORECASE):
                state = 'fitness'
                pm = price_re.search(line)
                if pm:
                    fitness_price = f'CHF {pm.group(1)}'
                continue

            if re.search(r'^pasta\s+fr|^pasta\s+\d', ll, re.IGNORECASE):
                state = 'pasta'
                pm = price_re.search(line)
                pasta_price = f'CHF {pm.group(1)}' if pm else 'CHF 19.50'
                continue

            if len(line) < 4:
                continue

            if state == 'vegi':
                vegi_raw.append(line)

            elif state == 'fitness':
                if re.search(r'wurst|käse salat|salat garniert', ll, re.IGNORECASE):
                    pm = price_re.search(line)
                    wurst_item = {
                        'title': 'Wurst-Käse Salat garniert',
                        'description': '',
                        'price': f'CHF {pm.group(1)}' if pm else 'CHF 19.50',
                    }
                elif ll.startswith('mit ') and len(line) > 6:
                    fitness_options.append(line.strip())

            elif state == 'pasta':
                pm = price_re.search(line)
                text = price_re.sub('', line).strip().rstrip(',.')
                if (text and len(text) > 4
                        and not re.search(r'www\.|http|\.ch\s*$|@|tel:|fax:|\/', text, re.IGNORECASE)):
                    pasta_items.append({
                        'title': 'Pasta',
                        'description': text,
                        'price': f'CHF {pm.group(1)}' if pm else pasta_price,
                    })

        # Vegi-Rohzeilen in 2 Gerichte splitten:
        # Vegi 2 beginnt typischerweise mit "Pasta Funghi" oder "Funghi"
        pasta_funghi_idx = next(
            (i for i, l in enumerate(vegi_raw)
             if re.search(r'funghi|tagliatelle', l, re.IGNORECASE) and i > 0),
            len(vegi_raw)
        )
        vegi1_lines = [l for l in vegi_raw[:pasta_funghi_idx] if len(l) > 3]
        vegi2_lines = [l for l in vegi_raw[pasta_funghi_idx:] if len(l) > 3]

        # Heutiges Fitnesteller-Gericht: index = Wochentag (Mo=0, Di=1, ..., Fr=4)
        weekday = today.weekday()
        today_fitness: Optional[Dict] = None
        if fitness_options and weekday < len(fitness_options):
            today_fitness = {
                'title': 'Fitnesteller (Gemischter Salat)',
                'description': fitness_options[weekday],
                'price': fitness_price,
            }

        # --- WOCHEN ANGEBOT aus Volltext ---
        wochen_items: List[Dict] = []
        in_wochen = False
        for line in ocr['all']:
            if re.search(r'wochen\s*angebot', line, re.IGNORECASE):
                in_wochen = True
                continue
            if not in_wochen:
                continue
            pm = price_re.search(line)
            if pm:
                text = price_re.sub('', line).strip().rstrip(',.;')
                if len(text) > 4 and not re.match(r'^[\W\d\s]+$', text):
                    wochen_items.append({
                        'title': 'Wochen-Angebot',
                        'description': text,
                        'price': f'CHF {pm.group(1)}',
                    })

        # --- Menüliste aufbauen ---
        menus: List[Dict] = []

        if today_meat_lines:
            menus.append({
                'title': 'Menü des Tages',
                'description': ' '.join(today_meat_lines),
                'price': header_price['menu'],
            })

        if vegi1_lines:
            menus.append({
                'title': 'Vegi-Menü 1',
                'description': ' '.join(vegi1_lines),
                'price': header_price['vegi'],
            })
        if vegi2_lines:
            menus.append({
                'title': 'Vegi-Menü 2',
                'description': ' '.join(vegi2_lines),
                'price': header_price['vegi'],
            })

        if today_fitness:
            menus.append(today_fitness)

        if wurst_item:
            menus.append(wurst_item)

        menus.extend(pasta_items)
        menus.extend(wochen_items)

        status = f'Tagesmenü {today.strftime("%d.%m.%Y")} (inkl. Suppe oder Salat)'
        if not [m for m in menus if m['title'] == 'Menü des Tages']:
            status = f'Kein Tagesmenü für {today_name} im Bild gefunden'

        return {
            'restaurant': self.name,
            'address': self.address,
            'status': status,
            'price': header_price['menu'],
            'menus': menus,
            'phone': '052 343 50 22',
            'website': self.SITE_URL,
            'note': 'Inkl. Suppe oder Menüsalat',
        }


class TomateScraper(MenuScraper):
    """Scraper für Restaurant Tomate – täglich aktualisiertes Menü-PDF"""

    PDF_URL = 'https://www.tomate-effretikon.ch/wp-content/uploads/menukarte.pdf'

    def get_menu(self) -> Dict[str, any]:
        today = datetime.now()
        if today.weekday() > 4:
            return self._error_result('Restaurant am Wochenende geschlossen')

        if not PDF_SUPPORT:
            return self._error_result('pypdf nicht installiert (pip install pypdf)')

        pdf_bytes = self.fetch_pdf_bytes(self.PDF_URL)
        if not pdf_bytes:
            return self._error_result('PDF nicht abrufbar')

        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text = '\n'.join(page.extract_text() for page in reader.pages)
        except Exception as e:
            return self._error_result(f'PDF-Parsing-Fehler: {e}')

        return self._parse_menus(text, today)

    def _parse_menus(self, text: str, today: datetime) -> Dict:
        # Verify the PDF is for today (date in first line)
        today_str = today.strftime('%d. %B %Y').lstrip('0')  # e.g. "16. April 2026"
        # Also handle "D O N N E R S T A G ,  D E N  16. April 2026" (spaced letters in PDF)
        date_match = re.search(
            r'(\d{1,2}\.)\s*(' + today.strftime('%B') + r')\s*(' + today.strftime('%Y') + r')',
            text, re.IGNORECASE
        )
        is_today = bool(date_match)

        # Extract all items with prices: text block followed by "CHF XX.XX"
        # Pattern: one or more descriptive lines, then a line with CHF price
        price_re = re.compile(r'CHF\s*([\d]{2,3}\.\d{2})')
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        menus = []
        buffer = []
        soup_line = ''

        # Find the included soup line (INKLUSIVE TAGESSUPPE: ...)
        for line in lines:
            if re.search(r'inklusive\s+tages', line, re.IGNORECASE):
                soup_line = re.sub(r'inklusive\s+tages(suppe)?:?\s*', '', line, flags=re.IGNORECASE).strip()
                break

        # Parse items: accumulate lines until price, then flush
        skip_re = re.compile(
            r'^(Restaurant|Bahnhof|Tel|Mail|Jedem|Menü 1|Menü 2|Vegetarisch|Tageshit|Wochenhit|INKLUSIVE|ODER)',
            re.IGNORECASE
        )
        # Also skip spaced-out day/date headers like "D O N N E R S T A G"
        spaced_re = re.compile(r'^([A-Z]\s){4,}')

        for line in lines:
            if skip_re.match(line) or spaced_re.match(line):
                continue
            m = price_re.search(line)
            if m:
                price = f'CHF {m.group(1)}'
                # Remove price from line if it's mixed
                name_part = price_re.sub('', line).strip().strip(';,.')
                if name_part:
                    buffer.append(name_part)
                if buffer:
                    title = buffer[0]
                    # Remove country hints like "(BR)", "(CH)"
                    title = re.sub(r'\s*\([A-Z]{2}\)\s*$', '', title).strip()
                    description = ', '.join(buffer[1:]) if len(buffer) > 1 else ''
                    # Clean up description
                    description = re.sub(r'\s*\([A-Z]{2}\)', '', description).strip()
                    menus.append({
                        'title': title,
                        'description': description,
                        'price': price,
                    })
                buffer = []
            else:
                buffer.append(line)

        status = f'Tagesmenü {today.strftime("%d.%m.%Y")}' if is_today else 'Aktuelles Menü (Datum nicht verifiziert)'
        note = f'Inkl. Salat oder Suppe: {soup_line}' if soup_line else 'Inkl. Salat oder Suppe'

        return {
            'restaurant': self.name,
            'address': self.address,
            'status': status,
            'price': 'CHF 22.50–27.50',
            'menus': menus,
            'phone': '052 343 30 12',
            'website': self.url,
            'note': note,
        }


class GenericScraper(MenuScraper):
    """Generischer Scraper für Restaurants ohne spezielle Implementierung"""

    def __init__(self, name: str, url: str, address: str, phone: str = '',
                 price: str = 'Siehe Website', note: str = ''):
        super().__init__(name, url, address)
        self.phone = phone
        self.price_info = price
        self.note = note

    def get_menu(self) -> Dict[str, any]:
        result = {
            'restaurant': self.name,
            'address': self.address,
            'price': self.price_info,
            'status': 'Keine Online-Menükarte verfügbar',
            'menus': [],
            'website': self.url,
            'info': 'Bitte Website oder telefonisch prüfen',
        }
        if self.phone:
            result['phone'] = self.phone
        if self.note:
            result['note'] = self.note
        return result


class MenuAggregator:
    """Hauptklasse zum Sammeln aller Restaurant-Menüs"""
    
    def __init__(self, use_console=True):
        self.use_console = use_console
        if use_console:
            self.console = Console()
        else:
            self.console = None
        self.restaurants = self._init_restaurants()
    
    def _init_restaurants(self) -> List[MenuScraper]:
        """Initialisiert alle Restaurant-Scraper"""
        return [
            BellissimoScraper(
                name="Ristorante Bellissimo da Edi",
                url="https://bellissimo-effretikon.ch/tagesmenue/",
                address="Bahnhofstrasse 21, 8307 Illnau-Effretikon"
            ),
            QNWorldScraper(
                name="QN World Restaurant",
                url="https://www.qn-world.ch/karten/mittagsmenu/",
                address="Riedstrasse 14, 8307 Effretikon"
            ),
            StrickhofScraper(
                name="Strickhof Mensa Lindau",
                url="https://www.strickhof.ch/campus/gastronomie/gastronomie-lindau/",
                address="Eschikon 21, 8315 Lindau"
            ),
            CasaLindaScraper(
                name="Casa Linda",
                url="https://www.casalinda.ch/",
                address="Lindenstrasse 38, 8307 Effretikon"
            ),
            TheValleyScraper(
                name="Restaurant The Valley",
                url="https://www.restaurant-thevalley.ch/",
                address="Gewerbestrasse 6, 8307 Effretikon"
            ),
            PuraVidaScraper(
                name="Restaurant Thalegg",
                url="https://www.restaurant-riet.ch/",
                address="Rietstrasse, 8307 Effretikon"
            ),
            GenericScraper(
                name="Tagesrestaurant Pura Vida",
                url="https://www.restaurant-riet.ch/",
                address="Märtplatz 19, 8307 Effretikon (APZ Bruggwiesen)",
                price='CHF 15–20',
                note="Täglich 3 Mittagsmenüs inkl. Suppe und Salat – Menü bitte vor Ort erfragen",
            ),
            DaZiaMariaScraper(
                name="Da Zia Maria",
                url="https://daziamaria.ch/",
                address="Vogelsangstrasse 14, 8307 Effretikon",
            ),
            TomateScraper(
                name="Restaurant Tomate",
                url="https://www.tomate-effretikon.ch/",
                address="Bahnhofstrasse 23, 8307 Illnau-Effretikon",
            ),
            GenericScraper(
                name="Casa Rustica",
                url="https://www.casarustica-effi.ch/index.html",
                address="Effretikon",
                phone="052 343 18 94",
                note="Event- und Bankettrestaurant – kein Mittagsmenü, Reservierung erforderlich",
            ),
        ]
    
    def collect_all_menus(self) -> List[Dict]:
        """Sammelt Menüs von allen Restaurants"""
        menus = []
        
        if self.console:
            with self.console.status("[bold green]Sammle Menüs von Restaurants...", spinner="dots"):
                for restaurant in self.restaurants:
                    self.console.print(f"[cyan]Lade {restaurant.name}...")
                    menu_data = restaurant.get_menu()
                    menus.append(menu_data)
        else:
            for restaurant in self.restaurants:
                menu_data = restaurant.get_menu()
                menus.append(menu_data)
        
        return menus
    
    def display_menus(self, menus: List[Dict]):
        """Zeigt alle gesammelten Menüs in schöner Formatierung"""
        self.console.print()
        self.console.print(Panel.fit(
            f"[bold yellow]🍽️  Mittagsmenüs Effretikon[/bold yellow]\n"
            f"[dim]{datetime.now().strftime('%A, %d. %B %Y - %H:%M Uhr')}[/dim]",
            box=box.DOUBLE
        ))
        self.console.print()
        
        for menu_data in menus:
            self._display_restaurant_menu(menu_data)
    
    def _display_restaurant_menu(self, menu_data: Dict):
        """Zeigt ein einzelnes Restaurant-Menü"""
        table = Table(
            title=f"[bold cyan]{menu_data['restaurant']}[/bold cyan]",
            show_header=False,
            box=box.ROUNDED,
            title_style="bold cyan"
        )
        
        table.add_column("Feld", style="bold yellow", width=15)
        table.add_column("Information", style="white")
        
        # Basis-Informationen
        table.add_row("📍 Adresse", menu_data['address'])
        
        if menu_data.get('phone'):
            table.add_row("📞 Telefon", menu_data['phone'])
        
        if menu_data.get('price'):
            table.add_row("💰 Preis", menu_data['price'])
        
        table.add_row("ℹ️  Status", menu_data.get('status', 'Unbekannt'))
        
        if menu_data.get('website'):
            table.add_row("🌐 Website", menu_data['website'])
        
        # Menüs anzeigen
        if menu_data.get('menus') and len(menu_data['menus']) > 0:
            table.add_row("", "")  # Leerzeile
            table.add_row("[bold]📋 Heutige Menüs", "")
            
            for idx, menu in enumerate(menu_data['menus'], 1):
                menu_title = menu.get('title', f'Menü {idx}')
                menu_desc = menu.get('description', 'Keine Details verfügbar')
                table.add_row(f"  {idx}.", f"[green]{menu_title}[/green]\n{menu_desc}")
        elif menu_data.get('info'):
            table.add_row("", "")
            table.add_row("[yellow]ℹ️  Hinweis", menu_data['info'])
        
        self.console.print(table)
        self.console.print()
    
    def export_to_markdown(self, menus: List[Dict], filename: str = "tagesmenus.md"):
        """Exportiert Menüs als Markdown-Datei"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Tagesmenüs Effretikon\n\n")
            f.write(f"**Stand:** {datetime.now().strftime('%d.%m.%Y, %H:%M Uhr')}\n\n")
            f.write("---\n\n")
            
            for menu_data in menus:
                f.write(f"## {menu_data['restaurant']}\n\n")
                f.write(f"**Adresse:** {menu_data['address']}\n\n")
                
                if menu_data.get('phone'):
                    f.write(f"**Telefon:** {menu_data['phone']}\n\n")
                
                if menu_data.get('price'):
                    f.write(f"**Preis:** {menu_data['price']}\n\n")
                
                f.write(f"**Status:** {menu_data.get('status', 'Unbekannt')}\n\n")
                
                if menu_data.get('website'):
                    f.write(f"**Website:** [{menu_data['website']}]({menu_data['website']})\n\n")
                
                if menu_data.get('menus') and len(menu_data['menus']) > 0:
                    f.write("### Heutige Menüs\n\n")
                    for idx, menu in enumerate(menu_data['menus'], 1):
                        f.write(f"{idx}. **{menu.get('title', 'Menü')}**\n")
                        f.write(f"   {menu.get('description', 'Keine Details')}\n\n")
                
                f.write("---\n\n")
        
        if self.console:
            self.console.print(f"[green]✓[/green] Menüs exportiert nach: [bold]{filename}[/bold]")


def main():
    """Hauptfunktion"""
    aggregator = MenuAggregator()
    
    # Sammle alle Menüs
    menus = aggregator.collect_all_menus()
    
    # Zeige Menüs an
    aggregator.display_menus(menus)
    
    # Exportiere zu Markdown
    try:
        aggregator.export_to_markdown(menus, "tagesmenus_heute.md")
    except Exception as e:
        print(f"Fehler beim Export: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
