#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
json_to_html_glossario.py — ATK-Pro v2.0
Converte il glossario multilingue JSON in HTML tabellare con sezioni.
Input: docs_generali/glossario_multilingua_ATK-Pro.json
Output: scripts/glossario_multilingua_ATK-Pro.html
Mantiene la struttura originale per sezione con stile ATK-Pro.
"""

import json
import os
from datetime import datetime

def json_to_html_glossario():
    """Carica JSON glossario e genera HTML tabellare con sezioni."""
    
    # Percorsi (relativi alla root del progetto)
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(script_dir, "docs_generali", "glossario_multilingua_ATK-Pro.json")
    html_path = os.path.join(script_dir, "scripts", "glossario_multilingua_ATK-Pro.html")
    
    # Leggi JSON
    if not os.path.exists(json_path):
        print(f"❌ File non trovato: {json_path}")
        return False
    
    with open(json_path, "r", encoding="utf-8") as f:
        glossario = json.load(f)
    
    # Lingue supportate (ordine fisso, 20 lingue)
    lingue = [
        "IT", "EN", "ES", "DE", "FR", "PT", "NL", "AR", "HE", "RU",
        "JA", "SV", "ZH", "RO", "EL", "PL", "DA", "NO", "TR", "VI"
    ]
    
    # Mapping sezioni con label
    section_labels = {
        "banner_sostegno": "📢 Banner di Sostegno",
        "funzioni_atkpro": "✨ Funzioni ATK-Pro",
        "etichette_gui": "🖥️ Etichette GUI",
        "etichette_menu": "📋 Etichette Menu",
        "menu_servizi": "🔧 Menu Servizi",
        "etichette_output": "📤 Etichette Output",
        "messaggi_dialogo": "💬 Messaggi Dialogo",
        "visualizzatore": "🖼️ Visualizzatore Immagini e Metadati"
    }
    
    # CSS minimale - NON sovrascrive atk_style.css
    css_content = """        /* Stili specifici per il glossario */
        header p {
            text-align: center !important;
            margin: 5px 0;
        }
        
        .glossario-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .glossario-header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .table-wrapper {
            width: 100%;
            overflow-x: auto;
            margin: 15px 0;
            border: 2px solid #a67c52;
            border-radius: 4px;
        }
        
        .metadata {
            background: rgba(230, 210, 165, 0.7) !important;
            border: 2px solid #a67c52 !important;
            border-radius: 8px;
            padding: 15px 30px !important;
            margin: 15px 0 !important;
            color: #4a2c1a !important;
        }
        
        .metadata strong {
            color: #2a1a0a !important;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            border: 2px solid #a67c52 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            /* table-layout: fixed; */
        }
        
        table th, table td {
            border: 1px solid #a67c52 !important;
            padding: 10px 6px;
            text-align: center;
            vertical-align: middle;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            min-width: 120px;
            max-width: 320px;
            word-break: normal;
            overflow-wrap: anywhere;
            white-space: normal;
        }
        
        table th {
            background: rgba(230, 210, 165, 0.6) !important;
            font-weight: 700 !important;
            white-space: normal;
            word-break: break-word;
            color: #4a2c1a !important;
            border: 1px solid #a67c52 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            font-size: 0.95em !important;
            line-height: 1.4 !important;
        }
        
        table td {
            background: rgba(255, 255, 255, 0.3) !important;
        }
        
        .section-title {
            font-size: 1.3em;
            margin: 30px 0 15px 0;
            padding: 15px 20px;
            border: 2px solid #a67c52 !important;
            border-radius: 8px;
            background: rgba(230, 210, 165, 0.6) !important;
            font-weight: bold;
            color: #4a2c1a !important;
            display: inline-block;
            min-width: 100%;
            box-sizing: border-box;
        }
        
        .section {
            margin: 20px 0;
            padding: 0 30px;
        }
        
        /* Uniforma font size per AR e HE */
        th:nth-child(9), th:nth-child(10),
        td:nth-child(9), td:nth-child(10) {
            font-size: 0.80em !important;
            line-height: 1.3 !important;
        }
"""
    
    # Header HTML
    versione = glossario.get("metadata", {}).get("versione", "2.0")
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    responsabile = glossario.get("metadata", {}).get("responsabile", "Daniele Pigoli")
    data = glossario.get("metadata", {}).get("data", "Dicembre 2025")
    
    html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Glossario Multilingue ATK-Pro v2.0</title>
    <link rel="stylesheet" href="../assets/common/testuali/atk_style.css">
    <style>
{css_content}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌍 Glossario Multilingue ATK-Pro</h1>
            <p><strong>Versione {versione}</strong> – 20 lingue supportate</p>
            <p style="font-size: 0.95em; margin-top: 10px; color: #5a3e2b;">Antenati Toolkit Pro</p>
        </header>
        <div class="metadata">
            <strong>📅 Generato:</strong> {timestamp} | 
            <strong>👤 Responsabile:</strong> {responsabile} 
        </div>
"""
    
    # Per ogni sezione nel glossario
    for section_key in ["banner_sostegno", "funzioni_atkpro", "etichette_gui", "etichette_menu",
                       "menu_servizi", "etichette_output", "messaggi_dialogo", "visualizzatore"]:
        if section_key not in glossario:
            continue
        
        section_data = glossario[section_key]
        if not isinstance(section_data, list) or not section_data:
            continue
        
        section_label = section_labels.get(section_key, section_key)
        
        html_content += f"""        <div class="section">
            <h2 class="section-title">{section_label}</h2>
            <div class="table-wrapper">
                <table class="glossario-table">
                    <thead>
                        <tr>
                            <th>Messaggio</th>
"""
        
        # Intestazioni lingue fisse
        lang_emojis = {
            "IT": "🇮🇹", "EN": "🇬🇧", "ES": "🇪🇸", "DE": "🇩🇪", "FR": "🇫🇷", "PT": "🇵🇹", "NL": "🇳🇱", "AR": "🇦🇷", "HE": "🇮🇱", "RU": "🇷🇺",
            "JA": "🇯🇵", "SV": "🇸🇪", "ZH": "🇨🇳", "RO": "🇷🇴", "EL": "🇬🇷", "PL": "🇵🇱", "DA": "🇩🇰", "NO": "🇳🇴", "TR": "🇹🇷", "VI": "🇻🇳"
        }
        for lang in lingue:
            flag = lang_emojis.get(lang, lang)
            html_content += f"                            <th>{flag}<br>{lang}</th>\n"
        
        html_content += """                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Genera righe tabella per questa sezione
        for entry in section_data:
            messaggio = entry.get("messaggio", "")
            # Escape HTML
            messaggio = messaggio.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_content += f"                        <tr>\n                            <td><strong>{messaggio}</strong></td>\n"
            
            for lang in lingue:
                valore = entry.get(lang, "")
                # Escape HTML
                valore = str(valore).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                html_content += f"                            <td>{valore}</td>\n"
            
            html_content += "                        </tr>\n"
        
        html_content += """                    </tbody>
                </table>
            </div>
        </div>
"""
    
    html_content += """        <footer>
            <p><strong>📋 Documento ufficiale del progetto ATK‑Pro.</strong> Ogni voce è predisposta per integrazione in MUI/DLL o file .po/.mo. Il glossario va versionato e aggiornato a ogni nuova milestone linguistica.</p>
        </footer>
</body>
</html>
"""
    
    # Scrivi HTML
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Glossario HTML generato con 8 sezioni: {html_path}")
    return True

if __name__ == "__main__":
    success = json_to_html_glossario()
    exit(0 if success else 1)
