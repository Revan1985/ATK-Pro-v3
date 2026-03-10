import re

# Each language maps:
# 'old_formats_folder' = the exact text from formats line through folder last line (before Export)
# 'new_formats_folder' = the new expanded text (same up to Export)

REPLACEMENTS = {
    'es': {
        'old': '├─ Seleccionar formatos de imagen\n│  └─ Elige entre PNG, JPG, TIFF (al menos 1 obligatorio)\n├─ Seleccionar carpeta de salida\n│  └─ Elige la carpeta donde guardar las imágenes procesadas\n├─ Exportar configuración',
        'new': '├─ Seleccionar formatos de imagen\n│  └─ Elige entre PNG, JPG, TIFF (al menos 1 obligatorio)\n│     Tu elección se guarda y se preselecciona automáticamente en la próxima sesión\n├─ Seleccionar carpetas de salida\n│  └─ Abre primero la selección del modo de carpeta y luego los diálogos de selección:\n│     • Carpeta única para todos      → una sola carpeta para documentos y registros\n│     • Carpetas separadas doc/reg    → una carpeta para todos los doc, otra para los reg\n│     • Carpeta por cada registro     → una carpeta distinta para cada registro\n│     El modo y las carpetas se guardan y restauran automáticamente en la próxima sesión\n├─ Exportar configuración',
    },
    'de': {
        'old': '├─ Bildformate auswählen\n│  └─ Wählen Sie zwischen PNG, JPG, TIFF (mindestens 1 erforderlich)\n├─ Ausgabeordner auswählen\n│  └─ Wählen Sie den Ordner, in dem die bearbeiteten Bilder gespeichert werden sollen\n├─ Konfiguration exportieren',
        'new': '├─ Bildformate auswählen\n│  └─ Wählen Sie zwischen PNG, JPG, TIFF (mindestens 1 erforderlich)\n│     Ihre Auswahl wird gespeichert und in der nächsten Sitzung automatisch vorausgewählt\n├─ Ausgabeordner auswählen\n│  └─ Öffnet zuerst die Ordnermoduswahl, dann die Ordnerauswahl-Dialoge:\n│     • Einzelner Ordner für alle     → ein Ordner für Dokumente und Register\n│     • Separate Ordner doc/reg       → ein Ordner für alle Dok., einer für alle Register\n│     • Ordner pro Datensatz          → ein eigener Ordner für jeden Datensatz\n│     Modus und Ordner werden gespeichert und in der nächsten Sitzung wiederhergestellt\n├─ Konfiguration exportieren',
    },
    'fr': {
        'old': "├─ Sélectionner les formats d'image\n│  └─ Choisissez entre PNG, JPG, TIFF (au moins 1 obligatoire)\n├─ Sélectionner le dossier de sortie\n│  └─ Choisissez le dossier où enregistrer les images traitées\n├─ Exporter la configuration",
        'new': "├─ Sélectionner les formats d'image\n│  └─ Choisissez entre PNG, JPG, TIFF (au moins 1 obligatoire)\n│     Votre choix est sauvegardé et présélectionné automatiquement à la prochaine session\n├─ Sélectionner les dossiers de sortie\n│  └─ Ouvre d'abord le choix du mode dossier, puis les fenêtres de sélection :\n│     • Dossier unique pour tous      → un seul dossier pour documents et registres\n│     • Dossiers séparés doc/reg      → un dossier pour tous les doc, un pour les reg\n│     • Dossier par enregistrement    → un dossier distinct pour chaque enregistrement\n│     Le mode et les dossiers sont sauvegardés et restaurés à la prochaine session\n├─ Exporter la configuration",
    },
    'pt': {
        'old': '├─ Selecionar formatos de imagem\n│  └─ Escolha entre PNG, JPG, TIFF (pelo menos 1 obrigatório)\n├─ Selecionar pasta de saída\n│  └─ Escolha a pasta onde salvar as imagens processadas\n├─ Exportar configuração',
        'new': '├─ Selecionar formatos de imagem\n│  └─ Escolha entre PNG, JPG, TIFF (pelo menos 1 obrigatório)\n│     Sua escolha é salva e pré-selecionada automaticamente na próxima sessão\n├─ Selecionar pastas de saída\n│  └─ Abre primeiro a seleção do modo de pasta e depois os diálogos de seleção:\n│     • Pasta única para todos        → uma pasta para documentos e registros\n│     • Pastas separadas doc/reg      → uma pasta para todos os doc, outra para os reg\n│     • Pasta por registro            → uma pasta distinta para cada registro\n│     O modo e as pastas são salvos e restaurados automaticamente na próxima sessão\n├─ Exportar configuração',
    },
    'nl': {
        'old': '├─ Selecteer afbeeldingsindelingen\n│  └─ Kies uit PNG, JPG, TIFF (minimaal 1 verplicht)\n├─ Selecteer uitvoermap\n│  └─ Kies de map waar de verwerkte afbeeldingen moeten worden opgeslagen\n├─ Exporteer configuratie',
        'new': '├─ Selecteer afbeeldingsindelingen\n│  └─ Kies uit PNG, JPG, TIFF (minimaal 1 verplicht)\n│     Uw keuze wordt opgeslagen en automatisch voorgeselecteerd bij de volgende sessie\n├─ Selecteer uitvoermappen\n│  └─ Opent eerst de mapselectie, dan de mappenkiezer-dialogen:\n│     • Eén map voor alles            → één map voor documenten en registers\n│     • Aparte mappen doc/reg         → één map voor alle doc, één voor alle reg\n│     • Map per record                → een aparte map voor elk record\n│     Modus en mappen worden opgeslagen en hersteld bij de volgende sessie\n├─ Exporteer configuratie',
    },
    'ar': {
        'old': '├─ اختر تنسيقات الصور\n│  └─ اختر بين PNG، JPG، TIFF (واحد على الأقل مطلوب)\n├─ اختر مجلد الإخراج\n│  └─ اختر المجلد الذي تريد حفظ الصور المعالجة فيه\n├─ تصدير التكوين',
        'new': '├─ اختر تنسيقات الصور\n│  └─ اختر بين PNG، JPG، TIFF (واحد على الأقل مطلوب)\n│     يتم حفظ اختيارك وتحديده مسبقاً تلقائياً في الجلسة التالية\n├─ اختر مجلدات الإخراج\n│  └─ يفتح أولاً اختيار وضع المجلد ثم نوافذ الاختيار:\n│     • مجلد واحد للجميع             → مجلد واحد للوثائق والسجلات\n│     • مجلدات منفصلة doc/reg        → مجلد لكل الوثائق، آخر للسجلات\n│     • مجلد لكل سجل                 → مجلد مخصص لكل سجل\n│     يتم حفظ الوضع والمجلدات واستعادتها تلقائياً في الجلسة التالية\n├─ تصدير التكوين',
    },
    'he': {
        'old': '├─ בחר פורמטים של תמונה\n│  └─ בחר בין PNG, JPG, TIFF (לפחות אחד חובה)\n├─ בחר תיקיית פלט\n│  └─ בחר את התיקייה לשמירת התמונות המעובדות\n├─ ייצוא תצורה',
        'new': '├─ בחר פורמטים של תמונה\n│  └─ בחר בין PNG, JPG, TIFF (לפחות אחד חובה)\n│     הבחירה נשמרת ומסומנת מראש אוטומטית בסשן הבא\n├─ בחר תיקיות פלט\n│  └─ פותח תחילה את בחירת מצב התיקייה, ואז חלונות הבחירה:\n│     • תיקייה אחת לכולם             → תיקייה אחת למסמכים ולרשומות\n│     • תיקיות נפרדות doc/reg        → תיקייה לכל המסמכים, אחרת לכל הרשומות\n│     • תיקייה לכל רשומה             → תיקייה נפרדת לכל רשומה\n│     המצב והתיקיות נשמרים ומשוחזרים אוטומטית בסשן הבא\n├─ ייצוא תצורה',
    },
    'ru': {
        'old': '├─ Выбрать форматы изображений\n│  └─ Выберите между PNG, JPG, TIFF (минимум 1 обязательно)\n├─ Выберите выходную папку\n│  └─ Выберите папку для сохранения обработанных изображений\n├─ Экспортировать конфигурацию',
        'new': '├─ Выбрать форматы изображений\n│  └─ Выберите между PNG, JPG, TIFF (минимум 1 обязательно)\n│     Выбор сохраняется и автоматически предвыбирается в следующей сессии\n├─ Выбрать папки вывода\n│  └─ Сначала открывает выбор режима, затем диалоги выбора папок:\n│     • Единая папка для всех         → одна папка для документов и реестров\n│     • Отдельные папки doc/reg       → одна для всех доку., другая для всех реест.\n│     • Папка для каждой записи       → отдельная папка для каждой записи\n│     Режим и папки сохраняются и восстанавливаются в следующей сессии\n├─ Экспортировать конфигурацию',
    },
    'ja': {
        'old': '├─ 画像形式を選択\n│  └─ PNG、JPG、TIFFから選択（少なくとも1つ必須）\n├─ 出力フォルダを選択\n│  └─ 処理された画像を保存するフォルダを選択してください\n├─ 設定のエクスポート',
        'new': '├─ 画像形式を選択\n│  └─ PNG、JPG、TIFFから選択（少なくとも1つ必須）\n│     選択は保存され次回セッションで自動的に事前選択されます\n├─ 出力フォルダーを選択\n│  └─ 最初にフォルダーモードを選択し、次に選択ダイアログを開きます：\n│     • すべてに単一フォルダー         → ドキュメントとレジスター用の1つのフォルダー\n│     • doc/reg別フォルダー           → すべてのdoc用、すべてのreg用に各1つ\n│     • レコードごとのフォルダー       → 各レコードに個別フォルダー\n│     モードとフォルダーは保存され次回セッションで自動的に復元されます\n├─ 設定のエクスポート',
    },
    'sv': {
        'old': '├─ Välj bildformat\n│  └─ Välj mellan PNG, JPG, TIFF (minst 1 obligatoriskt)\n├─ Välj utdatamapp\n│  └─ Välj mappen där bearbetade bilder ska sparas\n├─ Exportera konfiguration',
        'new': '├─ Välj bildformat\n│  └─ Välj mellan PNG, JPG, TIFF (minst 1 obligatoriskt)\n│     Ditt val sparas och förmarkeras automatiskt i nästa session\n├─ Välj utdatamappar\n│  └─ Öppnar först val av mappläge, sedan mappval-dialoger:\n│     • Enstaka mapp för alla         → en mapp för dokument och register\n│     • Separata mappar doc/reg       → en mapp för alla dok, en för alla reg\n│     • Mapp per post                 → en separat mapp för varje post\n│     Läget och mapparna sparas och återställs i nästa session\n├─ Exportera konfiguration',
    },
    'zh': {
        'old': '├─ 选择图片格式\n│  └─ 选择 PNG、JPG、TIFF（至少选择一种）\n├─ 选择输出文件夹\n│  └─ 选择保存处理后图像的文件夹\n├─ 导出配置',
        'new': '├─ 选择图片格式\n│  └─ 选择 PNG、JPG、TIFF（至少选择一种）\n│     您的选择已保存，下次启动时自动预选\n├─ 选择输出文件夹\n│  └─ 先打开文件夹模式选择，然后是文件夹选择对话框：\n│     • 所有记录的单一文件夹           → 文档和登记册共用一个文件夹\n│     • 分开的 doc/reg 文件夹         → 所有文档一个，所有登记册一个\n│     • 每条记录一个文件夹             → 每条记录各有独立文件夹\n│     模式和文件夹已保存，下次启动时自动恢复\n├─ 导出配置',
    },
    'ro': {
        'old': '├─ Selectați formate de imagine\n│  └─ Alegeți între PNG, JPG, TIFF (cel puțin 1 obligatoriu)\n├─ Selectați directorul de ieșire\n│  └─ Alegeți directorul unde să salvați imaginile procesate\n├─ Exportă configurație',
        'new': '├─ Selectați formate de imagine\n│  └─ Alegeți între PNG, JPG, TIFF (cel puțin 1 obligatoriu)\n│     Alegerea dvs. este salvată și preselectată automat la sesiunea următoare\n├─ Selectați folderele de ieșire\n│  └─ Deschide mai întâi selectorul de mod folder, apoi dialogurile de selecție:\n│     • Folder unic pentru toți       → un singur folder pentru documente și registre\n│     • Foldere separate doc/reg      → un folder pentru toate doc, altul pentru reg\n│     • Folder per înregistrare       → un folder distinct pentru fiecare înregistrare\n│     Modul și folderele sunt salvate și restaurate la sesiunea următoare\n├─ Exportă configurație',
    },
    'el': {
        'old': '├─ Επιλογή μορφών εικόνας\n│  └─ Επιλέξτε μεταξύ PNG, JPG, TIFF (τουλάχιστον 1 υποχρεωτικό)\n├─ Επιλογή φακέλου εξόδου\n│  └─ Επιλέξτε τον φάκελο όπου θα αποθηκευτούν οι επεξεργασμένες εικόνες\n├─ Εξαγωγή διαμόρφωσης',
        'new': '├─ Επιλογή μορφών εικόνας\n│  └─ Επιλέξτε μεταξύ PNG, JPG, TIFF (τουλάχιστον 1 υποχρεωτικό)\n│     Η επιλογή σας αποθηκεύεται και προεπιλέγεται αυτόματα στην επόμενη σύνοδο\n├─ Επιλογή φακέλων εξόδου\n│  └─ Ανοίγει πρώτα την επιλογή λειτουργίας φακέλου, μετά τα παράθυρα επιλογής:\n│     • Ενιαίος φάκελος για όλους     → ένας φάκελος για έγγραφα και μητρώα\n│     • Ξεχωριστοί φάκελοι doc/reg   → ένας για όλα τα doc, ένας για τα reg\n│     • Φάκελος ανά εγγραφή           → ξεχωριστός φάκελος για κάθε εγγραφή\n│     Η λειτουργία και οι φάκελοι αποθηκεύονται και επαναφέρονται αυτόματα\n├─ Εξαγωγή διαμόρφωσης',
    },
    'pl': {
        'old': '├─ Wybierz formaty obrazu\n│  └─ Wybierz spośród PNG, JPG, TIFF (wymagany co najmniej 1)\n├─ Wybierz folder wyjściowy\n│  └─ Wybierz folder, w którym chcesz zapisać przetworzone obrazy\n├─ Eksportuj konfigurację',
        'new': '├─ Wybierz formaty obrazu\n│  └─ Wybierz spośród PNG, JPG, TIFF (wymagany co najmniej 1)\n│     Twój wybór jest zapisywany i automatycznie wstępnie wybierany w następnej sesji\n├─ Wybierz foldery wyjściowe\n│  └─ Najpierw otwiera wybór trybu folderów, potem dialogi wyboru:\n│     • Jeden folder dla wszystkich   → jeden folder dla dokumentów i rejestrów\n│     • Oddzielne foldery doc/reg     → jeden dla wszystkich dok., drugi dla reg.\n│     • Folder na każdy rekord        → osobny folder dla każdego rekordu\n│     Tryb i foldery są zapisywane i przywracane w następnej sesji\n├─ Eksportuj konfigurację',
    },
    'da': {
        'old': '├─ Vælg billedformater\n│  └─ Vælg mellem PNG, JPG, TIFF (mindst 1 obligatorisk)\n├─ Vælg outputmappe\n│  └─ Vælg mappen, hvor de behandlede billeder skal gemmes\n├─ Eksporter konfiguration',
        'new': '├─ Vælg billedformater\n│  └─ Vælg mellem PNG, JPG, TIFF (mindst 1 obligatorisk)\n│     Dit valg gemmes og forudvælges automatisk i næste session\n├─ Vælg outputmapper\n│  └─ Åbner først mappevalg, derefter mappevælger-dialoger:\n│     • Enkelt mappe til alle         → én mappe for dokumenter og registre\n│     • Separate mapper doc/reg       → én til alle dok., én til alle reg.\n│     • Mappe per post                → en separat mappe for hver post\n│     Tilstand og mapper gemmes og gendannes automatisk i næste session\n├─ Eksporter konfiguration',
    },
    'no': {
        'old': '├─ Velg bildeformater\n│  └─ Velg mellom PNG, JPG, TIFF (minst 1 obligatorisk)\n├─ Velg utdatamappe\n│  └─ Velg mappen der du vil lagre de behandlede bildene\n├─ Eksporter konfigurasjon',
        'new': '├─ Velg bildeformater\n│  └─ Velg mellom PNG, JPG, TIFF (minst 1 obligatorisk)\n│     Valget lagres og forhåndsvelges automatisk i neste økt\n├─ Velg utdatamapper\n│  └─ Åpner først mappemodus-valg, deretter mappevelger-dialoger:\n│     • Enkelt mappe for alle         → én mappe for dokumenter og registre\n│     • Separate mapper doc/reg       → én for alle dok., én for alle reg.\n│     • Mappe per oppføring           → en separat mappe for hver oppføring\n│     Modus og mapper lagres og gjenopprettes automatisk i neste økt\n├─ Eksporter konfigurasjon',
    },
    'tr': {
        'old': '├─ Görüntü biçimleri seçin\n│  └─ PNG, JPG, TIFF arasından seçim yapın (en az 1 zorunlu)\n├─ Çıktı klasörünü seçin\n│  └─ İşlenmiş resimleri kaydetmek istediğiniz klasörü seçin\n├─ Yapılandırmayı dışa aktar',
        'new': '├─ Görüntü biçimleri seçin\n│  └─ PNG, JPG, TIFF arasından seçim yapın (en az 1 zorunlu)\n│     Seçiminiz kaydedilir ve sonraki oturumda otomatik olarak önceden seçilir\n├─ Çıktı klasörlerini seçin\n│  └─ Önce klasör modu seçimi, ardından klasör seçici diyaloglar açılır:\n│     • Tümü için tek klasör           → belge ve siciller için tek klasör\n│     • Ayrı klasörler doc/reg         → tüm belgeler için bir, tüm sic. için bir\n│     • Her kayıt için klasör          → her kayıt için ayrı bir klasör\n│     Mod ve klasörler kaydedilir ve sonraki oturumda otomatik geri yüklenir\n├─ Yapılandırmayı dışa aktar',
    },
    'vi': {
        'old': '├─ Chọn định dạng ảnh\n│  └─ Chọn giữa PNG, JPG, TIFF (ít nhất 1 bắt buộc)\n├─ Chọn thư mục đầu ra\n│  └─ Chọn thư mục để lưu ảnh đã xử lý\n├─ Xuất cấu hình',
        'new': '├─ Chọn định dạng ảnh\n│  └─ Chọn giữa PNG, JPG, TIFF (ít nhất 1 bắt buộc)\n│     Lựa chọn được lưu và tự động chọn trước trong phiên tiếp theo\n├─ Chọn thư mục đầu ra\n│  └─ Mở hộp thoại chọn chế độ thư mục trước, sau đó chọn thư mục:\n│     • Thư mục duy nhất cho tất cả   → một thư mục cho tài liệu và sổ đăng ký\n│     • Thư mục riêng doc/reg         → một cho tất cả tài liệu, một cho sổ đăng ký\n│     • Thư mục cho mỗi bản ghi       → thư mục riêng cho từng bản ghi\n│     Chế độ và thư mục được lưu và tự động khôi phục trong phiên tiếp theo\n├─ Xuất cấu hình',
    },
}

total_ok = 0
total_fail = 0

for lang, repl in REPLACEMENTS.items():
    path = f'c:/ATK-Pro_v2.0/assets/{lang}/testuali/guida.html'

    with open(path, 'rb') as f:
        raw = f.read()
    is_crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')

    old_str = repl['old']
    new_str = repl['new']

    if old_str in text:
        new_text = text.replace(old_str, new_str, 1)
        if is_crlf:
            out_bytes = new_text.replace('\n', '\r\n').encode('utf-8')
        else:
            out_bytes = new_text.encode('utf-8')
        with open(path, 'wb') as f:
            f.write(out_bytes)
        print(f'{lang}: OK')
        total_ok += 1
    else:
        print(f'{lang}: NOT FOUND - checking...')
        # Try to find partial match
        lines = old_str.split('\n')
        for i, line in enumerate(lines):
            if line not in text:
                print(f'  Line {i} not found: {repr(line)}')
        total_fail += 1

print(f'\nDone: {total_ok} OK, {total_fail} FAIL')
