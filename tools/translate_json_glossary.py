import json
import time

try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("Installing deep_translator...")
    import subprocess
    subprocess.check_call(["pip", "install", "deep-translator"])
    from deep_translator import GoogleTranslator

glossary_path = r'c:\ATK-Pro_v2.0\docs_generali\glossario_multilingua_ATK-Pro.json'
with open(glossary_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

lingue_map = {
    'EN': 'en', 'ES': 'es', 'DE': 'de', 'FR': 'fr', 'PT': 'pt',
    'NL': 'nl', 'AR': 'ar', 'HE': 'he', 'RU': 'ru', 'JA': 'ja',
    'SV': 'sv', 'ZH': 'zh-CN', 'RO': 'ro', 'EL': 'el', 'PL': 'pl',
    'DA': 'da', 'NO': 'no', 'TR': 'tr', 'VI': 'vi'
}

translators = {k: GoogleTranslator(source='it', target=v) for k, v in lingue_map.items()}

count = 0
total_translated = 0
for k, section_list in data.items():
    if isinstance(section_list, list):
        for entry in section_list:
            msg = entry.get('IT', entry.get('messaggio', ''))
            # check if untranslated: 'EN' matches the original italian 
            if entry.get('EN') == msg and msg.strip() != '' and len(msg) > 3:
                print(f"Translating: {msg}")
                for lang_code, translator in translators.items():
                    if entry.get(lang_code) == msg:
                        try:
                            translated = translator.translate(msg)
                            entry[lang_code] = translated
                            total_translated += 1
                        except:
                            entry[lang_code] = msg
                count += 1
                time.sleep(0.2)

with open(glossary_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
    
print(f"Done! Translated {count} sentences into 19 languages ({total_translated} API calls).")
