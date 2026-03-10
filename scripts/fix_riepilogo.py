import re

# Old h4 📌 titles to replace (2nd h4 📌 in each file)
OLD_H4 = {
    'es': '<h4>📌 IMPORTANTE:</h4>',
    'de': '<h4>📌 WICHTIG:</h4>',
    'fr': '<h4>📌 IMPORTANT :</h4>',
    'pt': '<h4>📌 IMPORTANTE:</h4>',
    'nl': '<h4>📌 BELANGRIJK:</h4>',
    'ar': '<h4>📌 هام:</h4>',
    'he': '<h4>📌 חשוב:</h4>',
    'ru': '<h4>📌 ВАЖНО:</h4>',
    'ja': '<h4>📌 重要：</h4>',
    'sv': '<h4>📌 VIKTIGT:</h4>',
    'zh': '<h4>📌 重要：</h4>',
    'ro': '<h4>📌 IMPORTANT:</h4>',
    'el': '<h4>📌 ΣΗΜΑΝΤΙΚΟ:</h4>',
    'pl': '<h4>📌 WAŻNE:</h4>',
    'da': '<h4>📌 VIGTIGT:</h4>',
    'no': '<h4>📌 VIKTIG:</h4>',
    'tr': '<h4>📌 ÖNEMLİ:</h4>',
    'vi': '<h4>📌 QUAN TRỌNG:</h4>',
}

# New RIEPILOGO translations per language
# Structure: (title, single_label, single_desc, sep_desc, per_label, per_desc)
RIEPILOGO = {
    'es': (
        'RESUMEN DE MODOS',
        'Carpeta única', 'Sencillo, todo en un lugar. Ideal para trabajos rápidos o pruebas',
        'Organizado por tipo. Predeterminado', 'y',
        'Por registro', 'Máxima flexibilidad. Puedes usar unidades diferentes, NAS, carpetas personalizadas'
    ),
    'de': (
        'MODUS-ÜBERSICHT',
        'Einzelner Ordner', 'Einfach, alles an einem Ort. Gut für schnelle Aufgaben oder Tests',
        'Nach Typ organisiert. Standard', 'und',
        'Pro Datensatz', 'Maximale Flexibilität. Ordner auf verschiedenen Laufwerken, NAS, benutzerdefiniert'
    ),
    'fr': (
        'RÉSUMÉ DES MODES',
        'Dossier unique', 'Simple, tout au même endroit. Idéal pour les travaux rapides ou les tests',
        'Organisé par type. Par défaut', 'et',
        'Par enregistrement', 'Flexibilité maximale. Dossiers sur différents disques, NAS, personnalisés'
    ),
    'pt': (
        'RESUMO DOS MODOS',
        'Pasta única', 'Simples, tudo no mesmo lugar. Ideal para trabalhos rápidos ou testes',
        'Organizado por tipo. Padrão', 'e',
        'Por registro', 'Máxima flexibilidade. Pastas em drives diferentes, NAS, personalizadas'
    ),
    'nl': (
        'MODUS-OVERZICHT',
        'Eén map voor alles', 'Eenvoudig, alles op één plek. Goed voor snelle taken of tests',
        'Georganiseerd per type. Standaard', 'en',
        'Per record', 'Maximale flexibiliteit. Mappen op verschillende schijven, NAS, aangepast'
    ),
    'ar': (
        'ملخص الأوضاع',
        'مجلد واحد للجميع', 'بسيط، كل شيء في مكان واحد. جيد للمهام السريعة أو الاختبارات',
        'منظم حسب النوع. الافتراضي', 'و',
        'مجلد لكل سجل', 'مرونة قصوى. يمكن استخدام محركات مختلفة أو NAS أو مجلدات مخصصة'
    ),
    'he': (
        'סיכום מצבים',
        'תיקייה אחת לכולם', 'פשוט, הכל במקום אחד. מתאים למשימות מהירות או בדיקות',
        'מאורגן לפי סוג. ברירת מחדל', 'ו-',
        'תיקייה לכל רשומה', 'גמישות מרבית. ניתן להשתמש בכוננים שונים, NAS, תיקיות מותאמות'
    ),
    'ru': (
        'СВОДКА РЕЖИМОВ',
        'Единая папка', 'Просто, всё в одном месте. Хорошо для быстрых задач или тестов',
        'Упорядочено по типу. По умолчанию', 'и',
        'Папка на запись', 'Максимальная гибкость. Разные диски, NAS, пользовательские папки'
    ),
    'ja': (
        'モード概要',
        '単一フォルダー', 'シンプル、すべて一か所。素早い作業やテストに最適',
        'タイプ別に整理。デフォルト', 'と',
        'レコードごとのフォルダー', '最大の柔軟性。異なるドライブ、NAS、カスタムフォルダーを使用可能'
    ),
    'sv': (
        'LÄGESÖVERSIKT',
        'Enstaka mapp för alla', 'Enkelt, allt på ett ställe. Bra för snabba jobb eller tester',
        'Organiserat per typ. Standard', 'och',
        'Mapp per post', 'Maximal flexibilitet. Mappar på olika enheter, NAS, anpassade mappar'
    ),
    'zh': (
        '模式摘要',
        '单一文件夹', '简单，所有内容在一处。适合快速任务或测试',
        '按类型组织。默认', '和',
        '每条记录一个文件夹', '最大灵活性。可使用不同驱动器、NAS、自定义文件夹'
    ),
    'ro': (
        'REZUMAT MODURI',
        'Folder unic pentru toți', 'Simplu, totul într-un loc. Bun pentru sarcini rapide sau teste',
        'Organizat pe tip. Implicit', 'și',
        'Folder per înregistrare', 'Flexibilitate maximă. Foldere pe unități diferite, NAS, personalizate'
    ),
    'el': (
        'ΣΥΝΟΨΗ ΛΕΙΤΟΥΡΓΙΩΝ',
        'Ενιαίος φάκελος για όλους', 'Απλό, όλα σε ένα μέρος. Ιδανικό για γρήγορες εργασίες ή δοκιμές',
        'Οργανωμένο ανά τύπο. Προεπιλογή', 'και',
        'Φάκελος ανά εγγραφή', 'Μέγιστη ευελιξία. Διαφορετικές μονάδες δίσκου, NAS, προσαρμοσμένοι φάκελοι'
    ),
    'pl': (
        'PODSUMOWANIE TRYBÓW',
        'Jeden folder dla wszystkich', 'Prosto, wszystko w jednym miejscu. Dobre do szybkich zadań lub testów',
        'Zorganizowane według typu. Domyślnie', 'i',
        'Folder na każdy rekord', 'Maksymalna elastyczność. Różne dyski, NAS, foldery niestandardowe'
    ),
    'da': (
        'TILSTANDSOVERSIGT',
        'Enkelt mappe til alle', 'Simpelt, alt ét sted. Godt til hurtige opgaver eller tests',
        'Organiseret efter type. Standard', 'og',
        'Mappe per post', 'Maksimal fleksibilitet. Mapper på forskellige drev, NAS, tilpassede mapper'
    ),
    'no': (
        'MODUSSAMMENDRAG',
        'Enkelt mappe for alle', 'Enkelt, alt på ett sted. Bra for raske jobber eller tester',
        'Organisert etter type. Standard', 'og',
        'Mappe per oppføring', 'Maksimal fleksibilitet. Mapper på forskjellige stasjoner, NAS, tilpassede mapper'
    ),
    'tr': (
        'MOD ÖZETİ',
        'Tümü için tek klasör', 'Basit, her şey bir yerde. Hızlı işler veya testler için iyi',
        'Türe göre düzenlenmiş. Varsayılan', 've',
        'Her kayıt için klasör', 'Maksimum esneklik. Farklı sürücüler, NAS, özel klasörler'
    ),
    'vi': (
        'TÓM TẮT CHẾ ĐỘ',
        'Thư mục duy nhất cho tất cả', 'Đơn giản, mọi thứ ở một nơi. Tốt cho công việc nhanh hoặc kiểm tra',
        'Được tổ chức theo loại. Mặc định', 'và',
        'Thư mục cho mỗi bản ghi', 'Tối đa linh hoạt. Ổ đĩa khác nhau, NAS, thư mục tùy chỉnh'
    ),
}

# DA english fallback fix
DA_OLD_H3 = '4. After choosing the mode, select the required folders (1, 2 or N valgdialogbokse)'
DA_NEW_H3 = '4. Vælg de nødvendige mapper efter valg af tilstand (1, 2 eller N valgdialogbokse)'

I = '            '

def build_riepilogo(lang):
    r = RIEPILOGO[lang]
    title, s_label, s_desc, sep_label, conj, p_label, p_desc = r
    lines = [
        f'<h4>📌 {title}:</h4>',
        '<ul>',
        f'    <li><strong>{s_label}:</strong> {s_desc}</li>',
        f'    <li><strong>Separate doc/reg:</strong> {sep_label}: <code>output/doc/</code> {conj} <code>output/reg/</code></li>',
        f'    <li><strong>{p_label}:</strong> {p_desc}</li>',
        '</ul>',
    ]
    return '\n'.join(I + l for l in lines)


total_ok = 0
total_fail = 0

for lang in OLD_H4.keys():
    path = f'assets/{lang}/testuali/guida.html'
    with open(path, 'rb') as f:
        raw = f.read()
    is_crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')

    changed = False

    # 1. Fix DA english fallback
    if lang == 'da' and DA_OLD_H3 in text:
        text = text.replace(
            f'<h3>{DA_OLD_H3}</h3>',
            f'<h3>{DA_NEW_H3}</h3>'
        )
        changed = True

    # 2. Find the 2nd 📌 h4 (the IMPORTANTE/WICHTIG) and replace it + its content
    old_h4 = OLD_H4[lang]
    if old_h4 not in text:
        print(f'{lang}: vecchio h4 📌 NON TROVATO: {old_h4}')
        total_fail += 1
        continue

    # Find position of old h4 (2nd occurrence in most cases, but there should be only one of this exact title)
    idx = text.find(old_h4)
    if idx < 0:
        print(f'{lang}: SKIP (non trovato)')
        total_fail += 1
        continue

    # Find end of old block (next h4)
    after = text[idx + len(old_h4):]
    next_h4 = re.search(r'<h4>', after)
    if next_h4:
        end_idx = idx + len(old_h4) + next_h4.start()
    else:
        end_idx = idx + len(old_h4) + 500  # fallback

    old_block = text[idx:end_idx]
    new_block = build_riepilogo(lang) + '\n'

    text = text[:idx] + new_block + text[end_idx:]
    changed = True

    if is_crlf:
        out = text.replace('\n', '\r\n').encode('utf-8')
    else:
        out = text.encode('utf-8')

    with open(path, 'wb') as f:
        f.write(out)

    print(f'{lang}: OK (da fixato={lang=="da"}, riepilogo={len(old_block)}→{len(new_block)} chars)')
    total_ok += 1

print(f'\nDone: {total_ok} OK, {total_fail} FAIL')
