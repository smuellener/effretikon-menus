#!/usr/bin/env python3
"""
Flask Web Application für Effretikon Restaurant Menü-Scraper
"""

from flask import Flask, render_template, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import json
from menu_scraper import MenuAggregator
import os

app = Flask(__name__)
CORS(app)

# Globale Instanz des Aggregators (ohne Console für Web-Betrieb)
aggregator = MenuAggregator(use_console=False)

@app.route('/')
def index():
    """Hauptseite"""
    return render_template('index.html')

@app.route('/api/menus', methods=['GET'])
def get_menus():
    """API-Endpunkt zum Abrufen der Menüs"""
    try:
        # Sammle Menüs
        menus = aggregator.collect_all_menus()
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'menus': menus,
            'count': len(menus)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    """API-Endpunkt zum Abrufen der Restaurant-Liste"""
    try:
        restaurants = []
        for scraper in aggregator.restaurants:
            restaurants.append({
                'name': scraper.name,
                'url': scraper.url,
                'address': scraper.address
            })
        
        return jsonify({
            'success': True,
            'restaurants': restaurants
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export', methods=['GET'])
def export_markdown():
    """Exportiert aktuelle Menüs als Markdown"""
    try:
        menus = aggregator.collect_all_menus()
        filename = 'tagesmenus_export.md'
        aggregator.export_to_markdown(menus, filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Erfolgreich exportiert'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🍽️  Effretikon Menü-Scraper Web-App")
    print("=" * 50)
    print(f"🌐 Server läuft auf: http://localhost:5000")
    print(f"📱 Öffne deinen Browser und besuche die URL")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
