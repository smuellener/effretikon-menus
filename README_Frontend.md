# 🌐 Effretikon Menü-Scraper - Web-Frontend

Ein modernes, responsives Web-Frontend für den Effretikon Restaurant Menü-Scraper.

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0%2B-lightgrey)

## 🚀 Quick Start

### 1. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 2. Web-App starten

```bash
python app.py
```

### 3. Im Browser öffnen

Öffne deinen Browser und navigiere zu:

```
http://localhost:5000
```

## 📸 Screenshots

Das Frontend zeigt:
- 🎨 Moderne, farbenfrohe Benutzeroberfläche
- 📱 Vollständig responsive (Mobile, Tablet, Desktop)
- 🔄 Echtzeit-Aktualisierung der Menüs
- 📄 Export-Funktion zu Markdown
- ⚡ Schnelle und intuitive Bedienung

## 🏗️ Architektur

```
rest-test/
├── app.py                    # Flask Backend-Server
├── menu_scraper.py          # Scraping-Logik
├── templates/
│   └── index.html           # HTML-Template
├── static/
│   ├── css/
│   │   └── style.css        # Styles & Responsive Design
│   └── js/
│       └── app.js           # Frontend-Logik
└── requirements.txt         # Python-Dependencies
```

## 🔧 Features

### Backend (Flask)
- ✅ RESTful API-Endpunkte
- ✅ CORS-Support
- ✅ Health-Check-Endpoint
- ✅ Fehlerbehandlung
- ✅ JSON-Responses

### Frontend
- ✅ Moderne UI mit Gradient-Design
- ✅ Responsive Grid-Layout
- ✅ Restaurant-Cards mit Hover-Effekten
- ✅ Status-Badges (verfügbar/nicht verfügbar)
- ✅ Loading-Spinner
- ✅ Fehlerbehandlung mit User-Feedback
- ✅ Automatisches Laden beim Start

## 📡 API-Endpunkte

### GET `/`
Hauptseite der Anwendung

### GET `/api/menus`
Lädt alle aktuellen Menüs von den Restaurants

**Response:**
```json
{
  "success": true,
  "timestamp": "2026-04-16T09:15:00",
  "menus": [...],
  "count": 4
}
```

### GET `/api/restaurants`
Liste aller konfigurierten Restaurants

**Response:**
```json
{
  "success": true,
  "restaurants": [
    {
      "name": "Restaurant Oase",
      "url": "https://...",
      "address": "..."
    }
  ]
}
```

### GET `/api/export`
Exportiert Menüs als Markdown-Datei

**Response:**
```json
{
  "success": true,
  "filename": "tagesmenus_export.md",
  "message": "Erfolgreich exportiert"
}
```

### GET `/health`
Health-Check für Monitoring

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-16T09:15:00"
}
```

## 🎨 Design-System

### Farben
- **Primary:** Orange (#FF6B35)
- **Secondary:** Gold (#F7931E)
- **Success:** Grün (#4CAF50)
- **Error:** Rot (#f44336)
- **Info:** Blau (#2196F3)

### Typografie
- **Font:** Poppins (Google Fonts)
- **Weights:** 300, 400, 600, 700

### Layout
- **Container:** Max-width 1400px
- **Cards:** Grid mit Auto-Fill (min 400px)
- **Border-Radius:** 12px
- **Shadows:** Layered (4px, 10px, 25px)

## 📱 Responsive Breakpoints

- **Desktop:** > 768px (Grid mit mehreren Spalten)
- **Tablet:** 768px (Single Column)
- **Mobile:** < 480px (Optimierte Buttons & Spacing)

## 🛠️ Entwicklung

### Debug-Modus
Der Flask-Server läuft standardmäßig im Debug-Modus:
- Auto-Reload bei Code-Änderungen
- Detaillierte Fehler-Traces
- Debugger-PIN in der Konsole

### Frontend-Entwicklung
1. Ändere HTML in `templates/index.html`
2. Ändere CSS in `static/css/style.css`
3. Ändere JavaScript in `static/js/app.js`
4. Reload Browser (Cmd+R / Ctrl+R)

### Backend-Entwicklung
1. Ändere Python-Code in `app.py` oder `menu_scraper.py`
2. Server reloaded automatisch (Debug-Modus)
3. API-Änderungen testen mit `/api/*`

## 🚀 Deployment

### Produktions-Server

Für Production NICHT den Development-Server verwenden! Verwende stattdessen:

#### Option 1: Gunicorn (Linux/Mac)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Option 2: Waitress (Windows)
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

#### Option 3: Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Umgebungsvariablen

```bash
# Produktions-Modus
export FLASK_ENV=production

# Port ändern
export FLASK_PORT=8080

# Host ändern
export FLASK_HOST=127.0.0.1
```

## 🔒 Sicherheit

⚠️ **Wichtige Hinweise für Production:**

1. **Debug-Modus deaktivieren:**
   ```python
   app.run(debug=False)
   ```

2. **Secret Key setzen:**
   ```python
   app.config['SECRET_KEY'] = 'your-secret-key-here'
   ```

3. **CORS einschränken:**
   ```python
   CORS(app, origins=['https://yourdomain.com'])
   ```

4. **HTTPS verwenden** (Reverse Proxy: nginx, Caddy)

5. **Rate Limiting** implementieren

## 🧪 Testing

### Manuelles Testen
```bash
# Health Check
curl http://localhost:5000/health

# Menüs laden
curl http://localhost:5000/api/menus

# Restaurants abrufen
curl http://localhost:5000/api/restaurants
```

### Browser-Testing
1. Öffne Browser-DevTools (F12)
2. Network-Tab öffnen
3. Auf "Aktualisieren" klicken
4. API-Calls überprüfen

## 📊 Performance

### Optimierungen
- Lazy Loading von Menü-Daten
- Parallele API-Requests
- Minimale DOM-Manipulationen
- CSS-Transitions statt JavaScript-Animationen

### Caching (Optional)
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/menus')
@cache.cached(timeout=300)  # 5 Minuten Cache
def get_menus():
    ...
```

## 🐛 Troubleshooting

### Server startet nicht
```bash
# Port bereits belegt?
netstat -ano | findstr :5000

# Dependencies fehlen?
pip install -r requirements.txt --upgrade
```

### Menüs laden nicht
- Internet-Verbindung prüfen
- Restaurant-Websites erreichbar?
- Browser-Console checken (F12)
- Server-Logs prüfen

### Frontend-Fehler
- Browser-Cache leeren (Ctrl+Shift+R)
- JavaScript-Errors in Console prüfen
- API-Endpoints testen (curl/Postman)

## 📝 Erweiterungen

### Neue Features hinzufügen

1. **Favoriten-System:**
   - LocalStorage für gespeicherte Favoriten
   - Stern-Icon zum Markieren

2. **Filter & Suche:**
   - Nach Küchen-Art filtern
   - Nach Preis filtern
   - Freitext-Suche

3. **Benachrichtigungen:**
   - Push-Notifications
   - E-Mail-Alerts bei neuen Menüs

4. **Bewertungen:**
   - User-Ratings
   - Kommentare

## 🤝 Contributing

Verbesserungen willkommen! Pull Requests gerne an:
1. Fork das Projekt
2. Feature-Branch erstellen
3. Commit mit aussagekräftiger Message
4. Push zum Branch
5. Pull Request öffnen

## 📄 Lizenz

Dieses Projekt ist für persönlichen Gebrauch. Die Menü-Daten gehören den jeweiligen Restaurants.

## 🙏 Credits

- **Flask:** Web-Framework
- **Beautiful Soup:** Web-Scraping
- **Rich:** Terminal-Formatting
- **Google Fonts:** Poppins Font
- **Icons:** Unicode Emoji

---

**Version:** 1.0.0  
**Erstellt:** 16. April 2026  
**Autor:** Menu Scraper Team  
**Status:** Production Ready ✅
