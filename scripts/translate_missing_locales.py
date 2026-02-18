#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera traduzioni complete per le 7 lingue mancanti usando Google Translate
"""

import os
import sys
from pathlib import Path
from babel.messages import pofile, mofile
from deep_translator import GoogleTranslator

# Mapping codici lingua
LANG_CODES = {
    'el': 'el',  # Greco
    'ja': 'ja',  # Giapponese
    'pl': 'pl',  # Polacco
    'ro': 'ro',  # Rumeno
    'sv': 'sv',  # Svedese
    'tr': 'tr',  # Turco
    'zh': 'zh-CN'  # Cinese semplificato
}

LANG_NAMES = {
    'el': 'Greek',
    'ja': 'Japanese',
    'pl': 'Polish',
    'ro': 'Romanian',
    'sv': 'Swedish',
    'tr': 'Turkish',
    'zh': 'Chinese (Simplified)'
}

def translate_po_file(source_lang_code, target_lang_code, target_lang_name):
    """
    Traduce file .po da lingua sorgente a lingua target
    """
    # Path
    project_root = Path(__file__).parent.parent
    source_po = project_root / f"locales/{source_lang_code}/LC_MESSAGES/messages.po"
    target_po = project_root / f"locales/{target_lang_code}/LC_MESSAGES/messages.po"
    target_mo = project_root / f"locales/{target_lang_code}/LC_MESSAGES/messages.mo"
    
    # Leggi catalogo sorgente
    with open(source_po, 'rb') as f:
        source_catalog = pofile.read_po(f)
    
    # Traduttore
    translator = GoogleTranslator(source='it', target=LANG_CODES[target_lang_code])
    
    print(f"\n🌍 Traduzione in {target_lang_name} ({target_lang_code})...")
    
    # Traduci ogni messaggio
    for message in source_catalog:
        if not message.id or not message.id.strip():
            continue  # Skip header
        
        try:
            # Traduci
            translated = translator.translate(message.id)
            message.string = translated
            print(f"  ✓ '{message.id}' → '{translated}'")
        except Exception as e:
            print(f"  ⚠️ Errore traduzione '{message.id}': {e}")
            message.string = message.id  # Fallback: usa originale
    
    # Aggiorna metadata
    source_catalog.project = 'Antenati ToolKit Pro'
    source_catalog.copyright_holder = 'ATK-Pro Team'
    source_catalog.msgid_bugs_address = 'antenati.toolkit.pro@gmail.com'
    source_catalog.language_team = f"{target_lang_name} <LL@li.org>"
    source_catalog.locale = target_lang_code
    
    # Salva .po
    with open(target_po, 'wb') as f:
        pofile.write_po(f, source_catalog, width=80)
    print(f"  💾 Salvato: {target_po}")
    
    # Compila .mo
    with open(target_mo, 'wb') as f:
        mofile.write_mo(f, source_catalog)
    
    mo_size = target_mo.stat().st_size / 1024
    print(f"  ✅ Compilato: {target_mo} ({mo_size:.1f} KB)")

def main():
    print("=" * 60)
    print("  ATK-Pro - Generazione Traduzioni Mancanti")
    print("=" * 60)
    
    # Lingua sorgente (italiano)
    source_lang = 'it'
    
    # Traduci tutte le 7 lingue
    for lang_code in ['el', 'ja', 'pl', 'ro', 'sv', 'tr', 'zh']:
        try:
            translate_po_file(source_lang, lang_code, LANG_NAMES[lang_code])
        except Exception as e:
            print(f"❌ Errore traduzione {lang_code}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print("✅ Traduzioni complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
