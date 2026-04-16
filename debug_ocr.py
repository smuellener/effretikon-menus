#!/usr/bin/env python3
"""
Debug-Script für Thalegg (Restaurant Riet) OCR.
Testet die Spalten-Trennung und den kompletten Menu-Parser.
"""

import sys
import re
import io
import os
import cloudscraper
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
from datetime import datetime

# Windows: Pfad zu tesseract.exe setzen
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = str(os.path.expanduser('~/tessdata'))

GERMAN_DAYS = {0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag', 4: 'Freitag'}
price_re = re.compile(r'\bFr\.?\s*([\d]{2,3}\.\d{2})', re.IGNORECASE)

# --- Bild von der Website holen ---
print("=== 1. Lade Website ===")
scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)
r = scraper.get('https://www.restaurant-riet.ch/', timeout=20)
print(f"HTTP {r.status_code}")
soup = BeautifulSoup(r.content, 'lxml')

# --- Bild-URL suchen ---
print("\n=== 2. Suche Menü-Bild ===")
menu_img_url = None
for img in soup.find_all('img'):
    srcset = img.get('srcset', '')
    src = img.get('src', '')
    for part in (srcset + ',' + src).split(','):
        part = part.strip()
        if 'transf/none' in part and 'jimcdn' in part:
            url = part.split(' ')[0]
            if '/image/' in url and '/version/' in url:
                menu_img_url = url
                break
    if menu_img_url:
        break

if not menu_img_url:
    print("KEIN transf/none Bild gefunden! Alle img-Tags:")
    for img in soup.find_all('img'):
        print(f"  src={img.get('src','')[:80]}")
    sys.exit(1)

print(f"Bild-URL: {menu_img_url}")

# --- Bild herunterladen ---
print("\n=== 3. Lade Bild ===")
img_resp = scraper.get(menu_img_url, timeout=15)
print(f"HTTP {img_resp.status_code}, Größe: {len(img_resp.content)/1024:.1f} KB")
img_bytes = img_resp.content

pil_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
print(f"Bildgröße: {pil_img.size}")
pil_img.save('debug_thalegg_menu.jpg')
print("→ Gespeichert als debug_thalegg_menu.jpg")

# --- Hochskalieren ---
w, h = pil_img.size
if w < 1000:
    pil_img = pil_img.resize((w * 2, h * 2), Image.LANCZOS)
    w, h = pil_img.size
    print(f"Hochskaliert auf: {pil_img.size}")

# --- Volltext OCR (für Wochen Angebot) ---
print("\n=== 4. Volltext OCR ===")
full_text = pytesseract.image_to_string(pil_img, lang='deu', config='--psm 6')
all_lines = [l.strip() for l in full_text.split('\n') if l.strip()]
print(f"{len(all_lines)} Zeilen gesamt:")
for i, l in enumerate(all_lines):
    print(f"  {i:2d}: {l}")

# --- Spalten-Trennung via Bounding-Boxes ---
print("\n=== 5. Spalten-Trennung (split_x = 52% Breite) ===")
split_x = int(w * 0.52)
print(f"split_x = {split_x}px  (Bildbreite: {w}px)")

data = pytesseract.image_to_data(pil_img, lang='deu', config='--psm 6',
                                  output_type=pytesseract.Output.DICT)

left_d = {}
right_d = {}

for i in range(len(data['text'])):
    text = data['text'][i].strip()
    if not text or int(data['conf'][i]) < 15:
        continue
    key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
    x = data['left'][i]
    y = data['top'][i]
    bucket = left_d if x < split_x else right_d
    entry = bucket.setdefault(key, {'words': [], 'y': y})
    entry['words'].append((x, text))

def reconstruct(line_dict):
    result = []
    for key in sorted(line_dict.keys()):
        entry = line_dict[key]
        words = sorted(entry['words'], key=lambda t: t[0])
        line = ' '.join(w for _, w in words).strip()
        if line:
            result.append({'text': line, 'y': entry['y']})
    return result

left_col = reconstruct(left_d)
right_col = reconstruct(right_d)

print(f"\n  LINKE SPALTE ({len(left_col)} Zeilen):")
for item in left_col:
    print(f"    y={item['y']:4d}  {item['text']}")

print(f"\n  RECHTE SPALTE ({len(right_col)} Zeilen):")
for item in right_col:
    print(f"    y={item['y']:4d}  {item['text']}")

# --- Parsing simulieren (gleiche Logik wie _parse_menu) ---
print("\n=== 6. Parser-Simulation ===")
today = datetime.now()
today_name = GERMAN_DAYS.get(today.weekday(), '')
day_names = list(GERMAN_DAYS.values())
print(f"Heute: {today_name} ({today.strftime('%d.%m.%Y')}), weekday={today.weekday()}")

def fuzzy_day_match(line):
    ll = line.lower()
    for day in day_names:
        if ll[:5] == day[:5].lower() or (
            len(ll) >= 4 and sum(a != b for a, b in zip(ll[:6], day.lower()[:6])) <= 1
        ):
            return day
    return None

# Linke Spalte → Tagessektionen
sections = {}
current_day = None
for item in left_col:
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

print(f"\n  Fleisch-Menüs (linke Spalte):")
for day, lines in sections.items():
    marker = " ◄ HEUTE" if day == today_name else ""
    print(f"    [{day}]{marker}: {lines}")

# Rechte Spalte → Vegi + Fitnesteller + Pasta
vegi_raw = []
fitness_options = []
fitness_price = 'CHF 24.50'
wurst_item = None
pasta_items = []
state = 'header'
pasta_price = 'CHF 19.50'

for item in right_col:
    line = item['text']
    ll = line.lower()
    if re.search(r'wochen\s*angebot', ll, re.IGNORECASE):
        break
    if re.search(r'vegi\s+fr', ll, re.IGNORECASE):
        state = 'vegi'
        continue
    if re.search(r'fitnesteller', ll, re.IGNORECASE):
        state = 'fitness'
        pm = price_re.search(line)
        if pm: fitness_price = f'CHF {pm.group(1)}'
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
            text = price_re.sub('', line).strip().rstrip(',.')
            wurst_item = {'title': 'Wurst-Käse Salat garniert', 'description': text,
                          'price': f'CHF {pm.group(1)}' if pm else 'CHF 19.50'}
        elif ll.startswith('mit ') and len(line) > 6:
            fitness_options.append(line.strip())
    elif state == 'pasta':
        pm = price_re.search(line)
        text = price_re.sub('', line).strip().rstrip(',.')
        if text and len(text) > 4:
            pasta_items.append({'title': 'Pasta', 'description': text,
                                'price': f'CHF {pm.group(1)}' if pm else pasta_price})

pasta_funghi_idx = next(
    (i for i, l in enumerate(vegi_raw) if re.search(r'funghi|tagliatelle', l, re.IGNORECASE) and i > 0),
    len(vegi_raw)
)
vegi1 = ' '.join(l for l in vegi_raw[:pasta_funghi_idx] if len(l) > 3)
vegi2 = ' '.join(l for l in vegi_raw[pasta_funghi_idx:] if len(l) > 3)

weekday = today.weekday()
today_fitness = None
if fitness_options and weekday < len(fitness_options):
    today_fitness = {'title': 'Fitnesteller', 'description': fitness_options[weekday],
                     'price': fitness_price}

print(f"\n  Vegi-Menü 1: {vegi1}")
print(f"  Vegi-Menü 2: {vegi2}")
print(f"  Fitnesteller-Optionen: {fitness_options}")
print(f"  Fitnesteller heute (idx={weekday}): {today_fitness}")
print(f"  Wurst-Käse: {wurst_item}")
print(f"  Pasta: {pasta_items}")

# Wochen Angebot
wochen_items = []
in_wochen = False
for line in all_lines:
    if re.search(r'wochen\s*angebot', line, re.IGNORECASE):
        in_wochen = True
        continue
    if not in_wochen:
        continue
    pm = price_re.search(line)
    if pm:
        text = price_re.sub('', line).strip().rstrip(',.;')
        if len(text) > 4 and not re.match(r'^[\W\d\s]+$', text):
            wochen_items.append({'description': text, 'price': f'CHF {pm.group(1)}'})

print(f"\n  Wochen-Angebot ({len(wochen_items)} Gerichte):")
for w_item in wochen_items:
    print(f"    {w_item['description']}  →  {w_item['price']}")

print(f"\n=== 7. Zusammenfassung für heute ({today_name}) ===")
meat = sections.get(today_name, [])
print(f"  Fleisch: {' '.join(meat)}")
print(f"  Vegi 1:  {vegi1}")
print(f"  Vegi 2:  {vegi2}")
print(f"  Fitness: {today_fitness}")
print(f"  Wurst:   {wurst_item}")
print(f"  Pasta:   {[p['description'] for p in pasta_items]}")
print(f"  Wochen:  {len(wochen_items)} Angebote")
