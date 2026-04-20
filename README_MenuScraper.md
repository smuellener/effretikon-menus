# 🍽️ Effretikon Restaurant Menü-Scraper

Ein Python-Tool zum automatischen Sammeln und Anzeigen von Tagesmenüs der Restaurants in Effretikon, Schweiz.

## Features

- ✅ Automatisches Sammeln von Menüs aus Restaurant-Websites
- ✅ Schöne Darstellung im Terminal mit Farben und Tabellen
- ✅ Export als Markdown-Datei
- ✅ Erweiterbar für neue Restaurants
- ✅ Fehlertolerante Web-Scraping-Implementierung

## Installation

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)

### Schritt 1: Dependencies installieren

```bash
pip install -r requirements.txt
```

Oder einzeln:

```bash
pip install requests beautifulsoup4 lxml rich python-dateutil
```

## Verwendung

### Menüs sammeln und anzeigen

```bash
python menu_scraper.py
```

Das Tool wird:
1. Alle konfigurierten Restaurant-Websites besuchen
2. Nach aktuellen Tagesmenüs suchen
3. Die Ergebnisse schön formatiert im Terminal anzeigen
4. Eine Markdown-Datei `tagesmenus_heute.md` mit allen Infos erstellen

### Ausgabe-Beispiel

```
🍽️  Mittagsmenüs Effretikon
Mittwoch, 16. April 2026 - 09:10 Uhr

╭─────────────────────────────────────────────╮
│     Restaurant Oase Effretikon              │
├─────────────┬───────────────────────────────┤
│ 📍 Adresse  │ Bietenholzstrasse 1          │
│ 📞 Telefon  │ 052 354 54 54                │
│ 💰 Preis    │ Variabel                     │
│ ℹ️  Status  │ Täglich frische Menüs        │
╰─────────────┴───────────────────────────────╯
```

## Konfiguration

### Neue Restaurants hinzufügen

Um ein neues Restaurant hinzuzufügen, bearbeiten Sie die `menu_scraper.py` Datei:

```python
# In der _init_restaurants() Methode:
GenericScraper(
    name="Neues Restaurant",
    url="https://restaurant-website.ch/menu",
    address="Restaurantstrasse 1, 8307 Effretikon"
),
```

### Eigenen Scraper erstellen

Für bessere Ergebnisse können Sie einen spezifischen Scraper für ein Restaurant erstellen:

```python
class MeinRestaurantScraper(MenuScraper):
    def get_menu(self) -> Dict[str, any]:
        soup = self.fetch_page()
        if not soup:
            return self._error_response()
        
        # Hier Ihre spezifische Parsing-Logik
        menus = []
        menu_divs = soup.find_all('div', class_='daily-menu')
        
        for div in menu_divs:
            menus.append({
                'title': div.find('h3').text,
                'description': div.find('p').text
            })
        
        return {
            'restaurant': self.name,
            'address': self.address,
            'menus': menus,
            'status': 'Online verfügbar'
        }
```

## Struktur

```
rest-test/
├── menu_scraper.py          # Hauptskript
├── requirements.txt         # Python-Dependencies
├── README_MenuScraper.md   # Diese Datei
├── tagesmenus_heute.md     # Generierte Ausgabe (nach Ausführung)
└── Effretikon_Mittagsmenues.md  # Statische Restaurant-Info
```

## Klassen-Übersicht

### `MenuScraper` (Basis-Klasse)
- Abstrakte Basisklasse für alle Scraper
- Stellt gemeinsame Funktionalität bereit (HTTP-Requests, Error-Handling)

### `MenuAggregator`
- Hauptklasse zum Orchestrieren aller Scraper
- Sammelt, formatiert und exportiert Menüdaten

### Restaurant-Scraper
- `OaseEffretikonScraper` - Restaurant Oase
- `VillaBaroneScraper` - Villa Barone
- `GenericScraper` - Fallback für Restaurants ohne spezielle Implementierung

## Erweiterte Nutzung

### Nur bestimmte Restaurants abfragen

Bearbeiten Sie `_init_restaurants()` und kommentieren Sie ungewünschte Restaurants aus.

### Zeitgesteuertes Ausführen

**Windows (Task Scheduler):**
```powershell
# Führe täglich um 08:00 Uhr aus
schtasks /create /sc daily /tn "Menu Scraper" /tr "python C:\path\to\menu_scraper.py" /st 08:00
```

**Linux/Mac (Cron):**
```bash
# Füge zu crontab hinzu
0 8 * * * cd /path/to/rest-test && python menu_scraper.py
```

## Fehlerbehebung

### Problem: "Module not found"
**Lösung:** Installieren Sie die Dependencies erneut:
```bash
pip install -r requirements.txt --upgrade
```

### Problem: "Website nicht erreichbar"
**Lösung:** 
- Überprüfen Sie Ihre Internetverbindung
- Manche Websites blockieren automatische Requests
- Versuchen Sie es später erneut

### Problem: "Keine Menüs gefunden"
**Lösung:**
- Die Website-Struktur könnte sich geändert haben
- Besuchen Sie die Website manuell im Browser
- Passen Sie den Scraper-Code entsprechend an

## Hinweise

⚠️ **Web-Scraping Legalität:**
- Dieses Tool ist für persönlichen Gebrauch gedacht
- Respektieren Sie die robots.txt der Websites
- Überladen Sie Server nicht mit zu vielen Requests
- Prüfen Sie die Nutzungsbedingungen der Websites

⚠️ **Datenaktualität:**
- Die Daten sind nur so aktuell wie die Websites
- Nicht alle Restaurants aktualisieren ihre Online-Menüs täglich
- Bei wichtigen Anlässen telefonisch bestätigen

## Zukünftige Verbesserungen

- [ ] API-Integration für Restaurants mit APIs
- [ ] GUI-Version mit Tkinter oder PyQt
- [ ] E-Mail-Benachrichtigung mit täglichen Menüs
- [ ] Filterung nach Allergenen/Diätpräferenzen
- [ ] Preisvergleich und Bewertungen
- [ ] Mobile App (React Native)

## Support

Bei Fragen oder Problemen:
1. Überprüfen Sie die Fehlerausgabe im Terminal
2. Stellen Sie sicher, dass alle Dependencies installiert sind
3. Testen Sie die Restaurant-URLs manuell im Browser

## Lizenz

Dieses Tool ist für persönlichen Gebrauch. Die gesammelten Daten gehören den jeweiligen Restaurants.

---

**Erstellt:** 16. April 2026  
**Version:** 1.0.0  
**Python:** 3.8+
