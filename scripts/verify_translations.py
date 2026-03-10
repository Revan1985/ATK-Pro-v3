import re

# Pattern inglesi specifici delle sezioni modificate che non dovrebbero
# apparire nelle guide non-EN/non-IT
ENGLISH_PATTERNS = [
    'After choosing the mode',
    'select the required folders',
    'Folder dialog opens',
    'format dialog opens automatically',
    'formats are saved',
    'Select at least one format',
    'Click Confirm',
    'A dialog box opens',
    'Choose the FOLDER MODE',
    'Single folder for all',
    'One folder per record',
    'Mode and folders are saved',
    'different number of Documents',
    'Load input file',
    'Alternatively:',
    'At the end a summary',
]

# Elementi chiave che DEVONO essere presenti in ogni guida (strutturali)
REQUIRED_STRUCTURAL = [
    '✅',   # nota formati salvati e/o cartelle salvate
    '⬤',   # pulsanti radio modalità cartelle
    '⚠️',  # avviso mismatch
    '📝',   # consigli/tips
    '☐ PNG',
    '☐ JPG',
    '☐ TIFF',
    'output/doc',
    'output/reg',
]

# Pattern per verificare che il blocco SETTINGS abbia la riga persistence
SETTINGS_PERSISTENCE_HINT = 'memorizzat|memori|saved|gespeichert|guardad|sauvegard|memor|sохран|保存|opgeslagen|παρα|zapisyw|gemm|gjem|kaydedil|lưu|저장'

LANGS_ALL = ['it','en','es','de','fr','pt','nl','ar','he','ru','ja','sv','zh','ro','el','pl','da','no','tr','vi']

issues = {}
ok_langs = []

for lang in LANGS_ALL:
    path = f'assets/{lang}/testuali/guida.html'
    with open(path, 'r', encoding='utf-8') as f:
        t = f.read()

    found_issues = []

    # 1. Controlla fallback inglesi (solo per non-EN)
    if lang not in ('en',):
        for pat in ENGLISH_PATTERNS:
            if pat.lower() in t.lower():
                idx = t.lower().find(pat.lower())
                line = t[:idx].count('\n') + 1
                ctx = t[max(0, idx-30):idx+len(pat)+50].replace('\n', '↵').strip()
                found_issues.append(f'  ENGLISH FALLBACK [{line}]: "{pat}"')
                found_issues.append(f'    → {ctx}')

    # 2. Controlla elementi strutturali obbligatori
    for el in REQUIRED_STRUCTURAL:
        if el not in t:
            found_issues.append(f'  MANCANTE: "{el}"')

    # 3. Controlla che il blocco pre SETTINGS abbia sia la riga persistence formati
    #    che le 3 modalità cartelle (•)
    pre_blocks = re.findall(r'<pre class="file-structure">(.*?)</pre>', t, re.DOTALL)
    settings_pre = None
    for pb in pre_blocks:
        if 'PNG' in pb or 'JPG' in pb or 'TIFF' in pb:
            settings_pre = pb
            break
    if settings_pre is None:
        found_issues.append('  SETTINGS pre block non trovato')
    else:
        if '•' not in settings_pre:
            found_issues.append('  SETTINGS: mancano • (modalità cartelle nei bullet)')
        bullet_count = settings_pre.count('•')
        if bullet_count < 3:
            found_issues.append(f'  SETTINGS: solo {bullet_count} bullet • (attesi >=3)')

    if found_issues:
        issues[lang] = found_issues
    else:
        ok_langs.append(lang)

print(f'OK ({len(ok_langs)}): {", ".join(ok_langs)}')
print()
if issues:
    print(f'=== PROBLEMI IN {len(issues)} LINGUA/E ===')
    for lang, msgs in issues.items():
        print(f'\n{lang.upper()}:')
        for m in msgs:
            print(m)
else:
    print('Tutte le guide sono coerenti. Nessun fallback inglese né elemento mancante.')
