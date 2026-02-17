#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html_to_json_glossario.py — ATK-Pro v2.0
Ricostruisce glossario_multilingua_ATK-Pro.json da HTML
Input: scripts/glossario_multilingua_ATK-Pro.html
Output: docs_generali/glossario_multilingua_ATK-Pro.json
EMERGENZA: File JSON perso durante operazioni Git
"""

import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

def html_to_json_glossario():
    """Ricostruisce JSON da HTML del glossario"""
    
    print("🔄 RICOSTRUZIONE GLOSSARIO JSON DA HTML")
    print("=" * 50)
    print()
    
    # Percorsi (relativi alla root del progetto)
    script_dir = Path(__file__).parent.parent
    html_path = script_dir / "scripts" / "glossario_multilingua_ATK-Pro.html"
    json_path = script_dir / "docs_generali" / "glossario_multilingua_ATK-Pro.json"
    
    if not html_path.exists():
        print(f"❌ File HTML non trovato: {html_path}")
        return False
    
    print(f"📖 Lettura HTML: {html_path}")
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Mapping sezioni (dai titoli HTML alle chiavi JSON)
    section_mapping = {
        "Banner di Sostegno": "banner_sostegno",
        "Funzioni ATK-Pro": "funzioni_atkpro",
        "Etichette GUI": "etichette_gui",
        "Etichette Menu": "etichette_menu",
        "Menu Servizi": "menu_servizi",
        "Etichette Output": "etichette_output",
        "Messaggi Dialogo": "messaggi_dialogo"
    }
    
    # Lingue in ordine (20 lingue)
    lingue = [
        "IT", "EN", "ES", "DE", "FR", "PT", "NL", "AR", "HE", "RU",
        "JA", "SV", "ZH", "RO", "EL", "PL", "DA", "NO", "TR", "VI"
    ]
    
    glossario = {}
    
    # Trova tutte le sezioni
    sections = soup.find_all('div', class_='section')
    
    for section in sections:
        # Trova il titolo della sezione
        title_elem = section.find('h2', class_='section-title')
        if not title_elem:
            continue
        
        # Estrae titolo pulito (senza emoji)
        title_text = title_elem.get_text(strip=True)
        # Rimuovi emoji e simboli iniziali
        title_clean = re.sub(r'^[^\w\s]+\s*', '', title_text).strip()
        
        # Trova chiave sezione
        section_key = None
        for key_search, json_key in section_mapping.items():
            if key_search in title_clean:
                section_key = json_key
                break
        
        if not section_key:
            print(f"⚠️  Sezione non riconosciuta: {title_clean}")
            continue
        
        print(f"📋 Elaborazione sezione: {title_clean} → {section_key}")
        
        # Trova tabella in questa sezione
        table = section.find('table', class_='glossario-table')
        if not table:
            print(f"   ⚠️  Tabella non trovata in sezione {title_clean}")
            continue
        
        # Estrae righe del tbody
        tbody = table.find('tbody')
        if not tbody:
            print(f"   ⚠️  tbody non trovato in sezione {title_clean}")
            continue
        
        rows = tbody.find_all('tr')
        section_data = []
        
        for row in rows:
            cells = row.find_all('td')
            
            if len(cells) < 21:  # Deve avere almeno 21 colonne (messaggio + 20 lingue)
                print(f"   ⚠️  Riga con {len(cells)} colonne (attese 21), saltata")
                continue
            
            # Prima colonna = messaggio/chiave (dentro <strong>)
            first_cell = cells[0]
            strong_elem = first_cell.find('strong')
            if strong_elem:
                messaggio = strong_elem.get_text(strip=True)
            else:
                messaggio = first_cell.get_text(strip=True)
            
            # Costruisce entry per questa riga
            entry = {"messaggio": messaggio}
            
            # Estrae traduzioni per ogni lingua
            for i, lingua in enumerate(lingue):
                # cells[i+1] perché la prima cella è il messaggio
                if i + 1 < len(cells):
                    traduzione = cells[i + 1].get_text(strip=True)
                    entry[lingua] = traduzione
                else:
                    entry[lingua] = ""
            
            section_data.append(entry)
            print(f"   ✓ {messaggio}: {len(section_data)} entries")
        
        glossario[section_key] = section_data
        print(f"   ✅ Sezione {section_key}: {len(section_data)} entries")
        print()
    
    # Salva JSON
    print(f"💾 Salvataggio JSON: {json_path}")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(glossario, f, ensure_ascii=False, indent=2)
    
    print()
    print("✅ GLOSSARIO JSON RICOSTRUITO CON SUCCESSO!")
    print()
    print(f"📊 Statistiche:")
    print(f"   • Sezioni: {len(glossario)}")
    for section_key, entries in glossario.items():
        print(f"   • {section_key}: {len(entries)} entries")
    
    total_entries = sum(len(entries) for entries in glossario.values())
    print(f"   • Totale entries: {total_entries}")
    print(f"   • Lingue per entry: 20")
    print(f"   • Traduzioni totali: {total_entries * 20}")
    print()
    
    return True

if __name__ == "__main__":
    success = html_to_json_glossario()
    exit(0 if success else 1)
