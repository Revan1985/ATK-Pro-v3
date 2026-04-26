import json
import time

try:
    from deep_translator import GoogleTranslator
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "deep-translator"])
    from deep_translator import GoogleTranslator

glossary_path = r'c:\ATK-Pro_v2.0\docs_generali\glossario_multilingua_ATK-Pro.json'
with open(glossary_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

lang_names = {
    'EN': 'english', 'ES': 'spanish', 'DE': 'german', 'FR': 'french', 'PT': 'portuguese',
    'NL': 'dutch', 'AR': 'arabic', 'HE': 'hebrew', 'RU': 'russian', 'JA': 'japanese',
    'SV': 'swedish', 'ZH': 'chinese (simplified)', 'RO': 'romanian', 'EL': 'greek', 'PL': 'polish',
    'DA': 'danish', 'NO': 'norwegian', 'TR': 'turkish', 'VI': 'vietnamese'
}

translators = {k: GoogleTranslator(source='it', target=v) for k, v in lang_names.items()}

count_entries_touched = 0
total_cells_translated = 0

for section_name, section_list in data.items():
    if not isinstance(section_list, list):
        continue
    
    for entry in section_list:
        base_msg = entry.get('IT')
        if not base_msg:
            base_msg = entry.get('messaggio', '')
            
        if not base_msg.strip():
            continue
            
        entry_needs_save = False
        
        for lang_code, translator in translators.items():
            current_val = entry.get(lang_code, "")
            
            # Se manca, è vuoto, oppure è identico all'italiano (non tradotto)
            if not current_val or current_val == base_msg:
                # Esegui la traduzione
                print(f"[{lang_code}] Translating: {base_msg[:30]}...")
                try:
                    translated = translator.translate(base_msg)
                    if translated:
                        entry[lang_code] = translated
                        total_cells_translated += 1
                        entry_needs_save = True
                except Exception as e:
                    print(f"Error for {lang_code}: {e}")
                    entry[lang_code] = base_msg # Fallback 
                    
        if entry_needs_save:
            count_entries_touched += 1
            # Evitiamo il rate limit se abbiamo appena tradotto
            time.sleep(0.3)

with open(glossary_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Done! Updated {count_entries_touched} entries, {total_cells_translated} cells translated.")
