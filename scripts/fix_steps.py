import re

# Translation strings per language
TRANS = {
    'es': {
        'new_h3_1': '1. Carga un archivo input (Archivo input → Abrir input): la ventana de formatos se abre automáticamente',
        'alternatively': 'En alternativa: ',
        'formats_saved_p': '✅ <strong>Los formatos seleccionados se guardan</strong> y se preseleccionan automáticamente la próxima vez que abras el programa.',
        'step2_new_h4': 'PASO 2: SELECCIONAR CARPETAS DE SALIDA',
        'step2_h3_1': '1. La ventana de carpetas se abre automáticamente después de elegir los formatos (cuando cargas un archivo input)',
        'step2_h3_2': '2. En alternativa: Haz clic en Menú → "Configuración" → "Seleccionar carpetas de salida"',
        'step2_h3_3': '3. Elige el MODO DE CARPETAS:',
        'radio_single': '⬤ Carpeta única para todos',
        'radio_single_desc': 'una sola carpeta para todos los registros (doc y registros)',
        'radio_separate': '⬤ Carpetas separadas doc/reg',
        'radio_separate_desc': 'una carpeta para todos los documentos, una para todos los registros',
        'radio_per': '⬤ Carpeta por cada registro',
        'radio_per_desc': 'una carpeta distinta para cada registro en el archivo input',
        'step2_h3_4': '4. Tras elegir el modo, selecciona las carpetas requeridas (1, 2 o N ventanas de diálogo)',
        'step2_h3_5': '5. Al final muestra un resumen de todas las carpetas seleccionadas',
        'folders_saved_p': '✅ <strong>El modo y las carpetas se guardan</strong>. La próxima vez que abras un archivo input, se restauran automáticamente si son compatibles con el número de registros.',
        'warning_p': '⚠️ Si el nuevo archivo input tiene un número diferente de Documentos/Registros respecto a las carpetas guardadas, aparece un aviso y la selección se restablece para pedir nuevas carpetas.',
    },
    'de': {
        'new_h3_1': '1. Laden Sie eine Eingabedatei (Eingabedatei → Eingabe öffnen): das Formatfenster öffnet sich automatisch',
        'alternatively': 'Alternativ: ',
        'formats_saved_p': '✅ <strong>Die ausgewählten Formate werden gespeichert</strong> und beim nächsten Programmstart automatisch vorausgewählt.',
        'step2_new_h4': 'SCHRITT 2: AUSGABEORDNER AUSWÄHLEN',
        'step2_h3_1': '1. Das Ordnerfenster öffnet sich automatisch nach der Formatauswahl (wenn Sie eine Eingabedatei laden)',
        'step2_h3_2': '2. Alternativ: Klicken Sie auf Menü → „Einstellungen" → „Ausgabeordner auswählen"',
        'step2_h3_3': '3. Wählen Sie den ORDNERMODUS:',
        'radio_single': '⬤ Einzelner Ordner für alle',
        'radio_single_desc': 'ein Ordner für alle Datensätze (Dokumente und Register)',
        'radio_separate': '⬤ Separate Ordner doc/reg',
        'radio_separate_desc': 'ein Ordner für alle Dokumente, einer für alle Register',
        'radio_per': '⬤ Ordner pro Datensatz',
        'radio_per_desc': 'ein eigener Ordner für jeden Datensatz in der Eingabedatei',
        'step2_h3_4': '4. Wählen Sie nach der Moduswahl die erforderlichen Ordner aus (1, 2 oder N Auswahldialoge)',
        'step2_h3_5': '5. Am Ende wird eine Zusammenfassung aller ausgewählten Ordner angezeigt',
        'folders_saved_p': '✅ <strong>Modus und Ordner werden gespeichert</strong>. Beim nächsten Öffnen einer Eingabedatei werden sie automatisch wiederhergestellt, wenn sie mit der Anzahl der Datensätze kompatibel sind.',
        'warning_p': '⚠️ Wenn die neue Eingabedatei eine andere Anzahl von Dokumenten/Registern als die gespeicherten Ordner hat, wird eine Warnung angezeigt und die Auswahl wird zurückgesetzt.',
    },
    'fr': {
        'new_h3_1': "1. Chargez un fichier d'entrée (Fichier d'entrée → Ouvrir l'entrée) : la fenêtre des formats s'ouvre automatiquement",
        'alternatively': 'En alternative : ',
        'formats_saved_p': '✅ <strong>Les formats sélectionnés sont sauvegardés</strong> et présélectionnés automatiquement à la prochaine ouverture du programme.',
        'step2_new_h4': 'ÉTAPE 2 : SÉLECTIONNER LES DOSSIERS DE SORTIE',
        'step2_h3_1': "1. La fenêtre des dossiers s'ouvre automatiquement après le choix des formats (quand vous chargez un fichier d'entrée)",
        'step2_h3_2': '2. En alternative : Cliquez sur Menu → « Paramètres » → « Sélectionner les dossiers de sortie »',
        'step2_h3_3': '3. Choisissez le MODE DOSSIER :',
        'radio_single': '⬤ Dossier unique pour tous',
        'radio_single_desc': 'un seul dossier pour tous les enregistrements (doc et registres)',
        'radio_separate': '⬤ Dossiers séparés doc/reg',
        'radio_separate_desc': 'un dossier pour tous les documents, un pour tous les registres',
        'radio_per': '⬤ Dossier par enregistrement',
        'radio_per_desc': 'un dossier distinct pour chaque enregistrement dans le fichier d\'entrée',
        'step2_h3_4': '4. Après le choix du mode, sélectionnez les dossiers requis (1, 2 ou N fenêtres de sélection)',
        'step2_h3_5': '5. À la fin, affiche un résumé de tous les dossiers choisis',
        'folders_saved_p': '✅ <strong>Le mode et les dossiers sont sauvegardés</strong>. À la prochaine ouverture d\'un fichier d\'entrée, ils sont automatiquement restaurés s\'ils sont compatibles avec le nombre d\'enregistrements.',
        'warning_p': '⚠️ Si le nouveau fichier d\'entrée a un nombre différent de Documents/Registres par rapport aux dossiers sauvegardés, un avertissement s\'affiche et la sélection est réinitialisée.',
    },
    'pt': {
        'new_h3_1': '1. Carregue um arquivo de entrada (Arquivo entrada → Abrir entrada): a janela de formatos abre automaticamente',
        'alternatively': 'Em alternativa: ',
        'formats_saved_p': '✅ <strong>Os formatos selecionados são salvos</strong> e pré-selecionados automaticamente na próxima vez que abrir o programa.',
        'step2_new_h4': 'PASSO 2: SELECIONAR PASTAS DE SAÍDA',
        'step2_h3_1': '1. A janela de pastas abre automaticamente após a seleção dos formatos (quando você carrega um arquivo de entrada)',
        'step2_h3_2': '2. Em alternativa: Clique em Menu → "Configurações" → "Selecionar pastas de saída"',
        'step2_h3_3': '3. Escolha o MODO DE PASTAS:',
        'radio_single': '⬤ Pasta única para todos',
        'radio_single_desc': 'uma pasta para todos os registros (documentos e registros)',
        'radio_separate': '⬤ Pastas separadas doc/reg',
        'radio_separate_desc': 'uma pasta para todos os documentos, outra para todos os registros',
        'radio_per': '⬤ Pasta por registro',
        'radio_per_desc': 'uma pasta distinta para cada registro no arquivo de entrada',
        'step2_h3_4': '4. Após escolher o modo, selecione as pastas necessárias (1, 2 ou N janelas de seleção)',
        'step2_h3_5': '5. No final exibe um resumo de todas as pastas selecionadas',
        'folders_saved_p': '✅ <strong>O modo e as pastas são salvos</strong>. Na próxima vez que abrir um arquivo de entrada, são restaurados automaticamente se compatíveis com o número de registros.',
        'warning_p': '⚠️ Se o novo arquivo de entrada tiver um número diferente de Documentos/Registros em relação às pastas salvas, aparece um aviso e a seleção é redefinida.',
    },
    'nl': {
        'new_h3_1': '1. Laad een invoerbestand (Invoerbestand → Invoer openen): het formaatvenster opent automatisch',
        'alternatively': 'Als alternatief: ',
        'formats_saved_p': '✅ <strong>De geselecteerde indelingen worden opgeslagen</strong> en automatisch voorgeselecteerd de volgende keer dat u het programma opent.',
        'step2_new_h4': 'STAP 2: SELECTEER UITVOERMAPPEN',
        'step2_h3_1': '1. Het mappenvenster opent automatisch na de formaatselectie (wanneer u een invoerbestand laadt)',
        'step2_h3_2': '2. Als alternatief: Klik op Menu → "Instellingen" → "Uitvoermappen selecteren"',
        'step2_h3_3': '3. Kies de MAPPENMODUS:',
        'radio_single': '⬤ Eén map voor alles',
        'radio_single_desc': 'één map voor alle records (documenten en registers)',
        'radio_separate': '⬤ Aparte mappen doc/reg',
        'radio_separate_desc': 'één map voor alle documenten, één voor alle registers',
        'radio_per': '⬤ Map per record',
        'radio_per_desc': 'een aparte map voor elk record in het invoerbestand',
        'step2_h3_4': '4. Na het kiezen van de modus, selecteer de vereiste mappen (1, 2 of N keuzedialogen)',
        'step2_h3_5': '5. Aan het einde wordt een samenvatting van alle geselecteerde mappen getoond',
        'folders_saved_p': '✅ <strong>Modus en mappen worden opgeslagen</strong>. De volgende keer dat u een invoerbestand opent, worden ze automatisch hersteld als ze compatibel zijn met het aantal records.',
        'warning_p': '⚠️ Als het nieuwe invoerbestand een ander aantal Documenten/Registers heeft dan de opgeslagen mappen, wordt een waarschuwing getoond en wordt de selectie gereset.',
    },
    'ar': {
        'new_h3_1': '1. حمّل ملف الإدخال (ملف الإدخال ← افتح الإدخال): تفتح نافذة التنسيقات تلقائياً',
        'alternatively': 'بديلاً: ',
        'formats_saved_p': '✅ <strong>يتم حفظ التنسيقات المختارة</strong> وتحديدها مسبقاً تلقائياً في المرة التالية التي تفتح فيها البرنامج.',
        'step2_new_h4': 'الخطوة 2: اختر مجلدات الإخراج',
        'step2_h3_1': '1. تفتح نافذة المجلد تلقائياً بعد اختيار التنسيقات (عند تحميل ملف الإدخال)',
        'step2_h3_2': '2. بديلاً: انقر على القائمة ← "الإعدادات" ← "اختر مجلدات الإخراج"',
        'step2_h3_3': '3. اختر وضع المجلدات:',
        'radio_single': '⬤ مجلد واحد للجميع',
        'radio_single_desc': 'مجلد واحد لجميع السجلات (الوثائق والسجلات)',
        'radio_separate': '⬤ مجلدات منفصلة doc/reg',
        'radio_separate_desc': 'مجلد لجميع الوثائق، مجلد آخر لجميع السجلات',
        'radio_per': '⬤ مجلد لكل سجل',
        'radio_per_desc': 'مجلد مخصص لكل سجل في ملف الإدخال',
        'step2_h3_4': '4. بعد اختيار الوضع، اختر المجلدات المطلوبة (1، 2 أو N نوافذ اختيار)',
        'step2_h3_5': '5. في النهاية يعرض ملخصاً لجميع المجلدات المختارة',
        'folders_saved_p': '✅ <strong>يتم حفظ الوضع والمجلدات</strong>. في المرة التالية التي تفتح فيها ملف إدخال، يتم استعادتهم تلقائياً إذا كانوا متوافقين مع عدد السجلات.',
        'warning_p': '⚠️ إذا كان ملف الإدخال الجديد يحتوي على عدد مختلف من الوثائق/السجلات مقارنةً بالمجلدات المحفوظة، يظهر تحذير ويتم إعادة تعيين الاختيار.',
    },
    'he': {
        'new_h3_1': '1. טען קובץ קלט (קובץ קלט → פתח קלט): חלון הפורמטים נפתח אוטומטית',
        'alternatively': 'לחלופין: ',
        'formats_saved_p': '✅ <strong>הפורמטים הנבחרים נשמרים</strong> ומסומנים מראש אוטומטית בפעם הבאה שתפתח את התוכנית.',
        'step2_new_h4': 'שלב 2: בחר תיקיות פלט',
        'step2_h3_1': '1. חלון התיקיות נפתח אוטומטית לאחר בחירת הפורמטים (כאשר אתה טוען קובץ קלט)',
        'step2_h3_2': '2. לחלופין: לחץ על תפריט → "הגדרות" → "בחר תיקיות פלט"',
        'step2_h3_3': '3. בחר את מצב התיקיות:',
        'radio_single': '⬤ תיקייה אחת לכולם',
        'radio_single_desc': 'תיקייה אחת לכל הרשומות (מסמכים ורשמים)',
        'radio_separate': '⬤ תיקיות נפרדות doc/reg',
        'radio_separate_desc': 'תיקייה אחת לכל המסמכים, אחרת לכל הרשמים',
        'radio_per': '⬤ תיקייה לכל רשומה',
        'radio_per_desc': 'תיקייה נפרדת לכל רשומה בקובץ הקלט',
        'step2_h3_4': '4. לאחר בחירת המצב, בחר את התיקיות הנדרשות (1, 2 או N חלונות בחירה)',
        'step2_h3_5': '5. בסיום מוצג סיכום של כל התיקיות שנבחרו',
        'folders_saved_p': '✅ <strong>המצב והתיקיות נשמרים</strong>. בפעם הבאה שתפתח קובץ קלט, הם משוחזרים אוטומטית אם תואמים למספר הרשומות.',
        'warning_p': '⚠️ אם קובץ הקלט החדש מכיל מספר שונה של מסמכים/רשמים בהשוואה לתיקיות השמורות, מוצגת אזהרה והסלקציה מאופסת.',
    },
    'ru': {
        'new_h3_1': '1. Загрузите входной файл (Входной файл → Открыть ввод): окно форматов открывается автоматически',
        'alternatively': 'Альтернативно: ',
        'formats_saved_p': '✅ <strong>Выбранные форматы сохраняются</strong> и автоматически предвыбираются при следующем открытии программы.',
        'step2_new_h4': 'ШАГ 2: ВЫБЕРИТЕ ПАПКИ ВЫВОДА',
        'step2_h3_1': '1. Окно папок открывается автоматически после выбора форматов (при загрузке входного файла)',
        'step2_h3_2': '2. Альтернативно: Нажмите Меню → «Настройки» → «Выбрать папки вывода»',
        'step2_h3_3': '3. Выберите РЕЖИМ ПАПОК:',
        'radio_single': '⬤ Единая папка для всех',
        'radio_single_desc': 'одна папка для всех записей (документы и реестры)',
        'radio_separate': '⬤ Отдельные папки doc/reg',
        'radio_separate_desc': 'одна папка для всех документов, другая для всех реестров',
        'radio_per': '⬤ Папка для каждой записи',
        'radio_per_desc': 'отдельная папка для каждой записи во входном файле',
        'step2_h3_4': '4. После выбора режима выберите нужные папки (1, 2 или N диалогов выбора)',
        'step2_h3_5': '5. В конце показывается сводка всех выбранных папок',
        'folders_saved_p': '✅ <strong>Режим и папки сохраняются</strong>. При следующем открытии входного файла они автоматически восстанавливаются, если совместимы с числом записей.',
        'warning_p': '⚠️ Если новый входной файл содержит иное количество Документов/Реестров по сравнению с сохранёнными папками, отображается предупреждение и выбор сбрасывается.',
    },
    'ja': {
        'new_h3_1': '1. 入力ファイルを読み込む（入力ファイル → 入力を開く）：フォーマットダイアログが自動的に開きます',
        'alternatively': '代わりに：',
        'formats_saved_p': '✅ <strong>選択したフォーマットは保存され</strong>、次回プログラムを開いたときに自動的に事前選択されます。',
        'step2_new_h4': 'ステップ2：出力フォルダーを選択',
        'step2_h3_1': '1. フォルダーダイアログはフォーマット選択後に自動的に開きます（入力ファイルを読み込んだとき）',
        'step2_h3_2': '2. 代わりに：メニュー → 「設定」 → 「出力フォルダーを選択」をクリック',
        'step2_h3_3': '3. フォルダーモードを選んでください：',
        'radio_single': '⬤ すべてに単一フォルダー',
        'radio_single_desc': 'すべてのレコード（ドキュメントとレジスター）に1つのフォルダー',
        'radio_separate': '⬤ doc/reg別フォルダー',
        'radio_separate_desc': 'すべてのドキュメント用に1つ、すべてのレジスター用に1つ',
        'radio_per': '⬤ レコードごとのフォルダー',
        'radio_per_desc': '入力ファイルの各レコードに個別フォルダー',
        'step2_h3_4': '4. モード選択後に必要なフォルダーを選択します（1、2またはNのピッカーダイアログ）',
        'step2_h3_5': '5. 最後に選択したすべてのフォルダーの概要が表示されます',
        'folders_saved_p': '✅ <strong>モードとフォルダーは保存され</strong>、次に入力ファイルを開いたときにレコード数と互換性があれば自動的に復元されます。',
        'warning_p': '⚠️ 新しい入力ファイルのドキュメント/レジスター数が保存済みフォルダーと異なる場合、警告が表示され選択がリセットされます。',
    },
    'sv': {
        'new_h3_1': '1. Ladda en indatafil (Indatafil → Öppna indata): formatfönstret öppnas automatiskt',
        'alternatively': 'Alternativt: ',
        'formats_saved_p': '✅ <strong>De valda formaten sparas</strong> och förmarkeras automatiskt nästa gång du öppnar programmet.',
        'step2_new_h4': 'STEG 2: VÄLJ UTDATAMAPPAR',
        'step2_h3_1': '1. Mappfönstret öppnas automatiskt efter formatvalet (när du laddar en indatafil)',
        'step2_h3_2': '2. Alternativt: Klicka på Meny → "Inställningar" → "Välj utdatamappar"',
        'step2_h3_3': '3. Välj MAPPLÄGE:',
        'radio_single': '⬤ Enstaka mapp för alla',
        'radio_single_desc': 'en mapp för alla poster (dokument och register)',
        'radio_separate': '⬤ Separata mappar doc/reg',
        'radio_separate_desc': 'en mapp för alla dokument, en för alla register',
        'radio_per': '⬤ Mapp per post',
        'radio_per_desc': 'en separat mapp för varje post i indatafilen',
        'step2_h3_4': '4. Efter att ha valt läge, välj de nödvändiga mapparna (1, 2 eller N väljar-dialoger)',
        'step2_h3_5': '5. I slutet visas en sammanfattning av alla valda mappar',
        'folders_saved_p': '✅ <strong>Läge och mappar sparas</strong>. Nästa gång du öppnar en indatafil återställs de automatiskt om de är kompatibla med antalet poster.',
        'warning_p': '⚠️ Om den nya indatafilen har ett annat antal Dokument/Register jämfört med sparade mappar visas en varning och urvalet återställs.',
    },
    'zh': {
        'new_h3_1': '1. 加载输入文件（输入文件 → 打开输入）：格式窗口自动打开',
        'alternatively': '或者：',
        'formats_saved_p': '✅ <strong>所选格式已保存</strong>，下次打开程序时自动预选。',
        'step2_new_h4': '步骤 2：选择输出文件夹',
        'step2_h3_1': '1. 选择格式后（加载输入文件时），文件夹窗口自动打开',
        'step2_h3_2': '2. 或者：点击菜单 → "设置" → "选择输出文件夹"',
        'step2_h3_3': '3. 选择文件夹模式：',
        'radio_single': '⬤ 所有记录的单一文件夹',
        'radio_single_desc': '所有记录（文件和登记册）共用一个文件夹',
        'radio_separate': '⬤ 分开的 doc/reg 文件夹',
        'radio_separate_desc': '所有文件使用一个文件夹，所有登记册使用另一个',
        'radio_per': '⬤ 每条记录一个文件夹',
        'radio_per_desc': '输入文件中每条记录各有独立文件夹',
        'step2_h3_4': '4. 选择模式后，选择所需文件夹（1、2 或 N 个选择对话框）',
        'step2_h3_5': '5. 最后显示所有选定文件夹的摘要',
        'folders_saved_p': '✅ <strong>模式和文件夹已保存</strong>。下次打开输入文件时，如果与记录数兼容，则自动恢复。',
        'warning_p': '⚠️ 如果新输入文件的文档/登记册数量与已保存文件夹不同，将显示警告并重置选择。',
    },
    'ro': {
        'new_h3_1': '1. Încarcă un fișier de intrare (Fișier intrare → Deschide intrarea): fereastra formatelor se deschide automat',
        'alternatively': 'Alternativ: ',
        'formats_saved_p': '✅ <strong>Formatele selectate sunt salvate</strong> și preselectate automat data viitoare când deschizi programul.',
        'step2_new_h4': 'PASUL 2: SELECTAȚI FOLDERELE DE IEȘIRE',
        'step2_h3_1': '1. Fereastra folderelor se deschide automat după selectarea formatelor (când încarci un fișier de intrare)',
        'step2_h3_2': '2. Alternativ: Fă clic pe Meniu → Setări → „Selectează folderele de ieșire"',
        'step2_h3_3': '3. Alege MODUL FOLDERELOR:',
        'radio_single': '⬤ Folder unic pentru toți',
        'radio_single_desc': 'un singur folder pentru toate înregistrările (documente și registre)',
        'radio_separate': '⬤ Foldere separate doc/reg',
        'radio_separate_desc': 'un folder pentru toate documentele, altul pentru toate registrele',
        'radio_per': '⬤ Folder per înregistrare',
        'radio_per_desc': 'un folder distinct pentru fiecare înregistrare din fișierul de intrare',
        'step2_h3_4': '4. După alegerea modului, selectează folderele necesare (1, 2 sau N dialoguri de selecție)',
        'step2_h3_5': '5. La final afișează un rezumat al tuturor folderelor selectate',
        'folders_saved_p': '✅ <strong>Modul și folderele sunt salvate</strong>. Data viitoare când deschizi un fișier de intrare, sunt restaurate automat dacă sunt compatibile cu numărul de înregistrări.',
        'warning_p': '⚠️ Dacă noul fișier de intrare are un număr diferit de Documente/Registre față de folderele salvate, apare un avertisment și selecția este resetată.',
    },
    'el': {
        'new_h3_1': '1. Φορτώστε ένα αρχείο εισόδου (Αρχείο εισόδου → Άνοιγμα εισόδου): το παράθυρο μορφών ανοίγει αυτόματα',
        'alternatively': 'Εναλλακτικά: ',
        'formats_saved_p': '✅ <strong>Οι επιλεγμένες μορφές αποθηκεύονται</strong> και προεπιλέγονται αυτόματα την επόμενη φορά που θα ανοίξετε το πρόγραμμα.',
        'step2_new_h4': 'ΒΗΜΑ 2: ΕΠΙΛΟΓΗ ΦΑΚΕΛΩΝ ΕΞΟΔΟΥ',
        'step2_h3_1': '1. Το παράθυρο φακέλων ανοίγει αυτόματα μετά την επιλογή μορφών (όταν φορτώνετε αρχείο εισόδου)',
        'step2_h3_2': '2. Εναλλακτικά: Κάντε κλικ στο Μενού → "Ρυθμίσεις" → "Επιλογή φακέλων εξόδου"',
        'step2_h3_3': '3. Επιλέξτε τη ΛΕΙΤΟΥΡΓΊΑ ΦΑΚΕΛΩΝ:',
        'radio_single': '⬤ Ενιαίος φάκελος για όλους',
        'radio_single_desc': 'ένας φάκελος για όλες τις εγγραφές (έγγραφα και μητρώα)',
        'radio_separate': '⬤ Ξεχωριστοί φάκελοι doc/reg',
        'radio_separate_desc': 'ένας φάκελος για όλα τα έγγραφα, ένας για όλα τα μητρώα',
        'radio_per': '⬤ Φάκελος ανά εγγραφή',
        'radio_per_desc': 'ξεχωριστός φάκελος για κάθε εγγραφή στο αρχείο εισόδου',
        'step2_h3_4': '4. Μετά την επιλογή λειτουργίας, επιλέξτε τους απαιτούμενους φακέλους (1, 2 ή N παράθυρα επιλογής)',
        'step2_h3_5': '5. Στο τέλος εμφανίζεται περίληψη όλων των επιλεγμένων φακέλων',
        'folders_saved_p': '✅ <strong>Η λειτουργία και οι φάκελοι αποθηκεύονται</strong>. Την επόμενη φορά που θα ανοίξετε αρχείο εισόδου, αποκαθίστανται αυτόματα αν είναι συμβατοί με τον αριθμό εγγραφών.',
        'warning_p': '⚠️ Αν το νέο αρχείο εισόδου έχει διαφορετικό αριθμό Εγγράφων/Μητρώων σε σχέση με τους αποθηκευμένους φακέλους, εμφανίζεται προειδοποίηση και η επιλογή μηδενίζεται.',
    },
    'pl': {
        'new_h3_1': '1. Wczytaj plik wejściowy (Plik wejściowy → Otwórz wejście): okno formatów otwiera się automatycznie',
        'alternatively': 'Alternatywnie: ',
        'formats_saved_p': '✅ <strong>Wybrane formaty są zapisywane</strong> i automatycznie wstępnie wybierane następnym razem gdy otworzysz program.',
        'step2_new_h4': 'KROK 2: WYBIERZ FOLDERY WYJŚCIOWE',
        'step2_h3_1': '1. Okno folderów otwiera się automatycznie po wyborze formatów (gdy wczytasz plik wejściowy)',
        'step2_h3_2': '2. Alternatywnie: Kliknij Menu → „Ustawienia" → „Wybierz foldery wyjściowe"',
        'step2_h3_3': '3. Wybierz TRYB FOLDERÓW:',
        'radio_single': '⬤ Jeden folder dla wszystkich',
        'radio_single_desc': 'jeden folder dla wszystkich rekordów (dokumenty i rejestry)',
        'radio_separate': '⬤ Oddzielne foldery doc/reg',
        'radio_separate_desc': 'jeden folder dla wszystkich dokumentów, inny dla wszystkich rejestrów',
        'radio_per': '⬤ Folder na każdy rekord',
        'radio_per_desc': 'osobny folder dla każdego rekordu w pliku wejściowym',
        'step2_h3_4': '4. Po wyborze trybu, wybierz wymagane foldery (1, 2 lub N okien wyboru)',
        'step2_h3_5': '5. Na koniec wyświetlane jest podsumowanie wszystkich wybranych folderów',
        'folders_saved_p': '✅ <strong>Tryb i foldery są zapisywane</strong>. Następnym razem gdy otworzysz plik wejściowy, są automatycznie przywracane jeśli są zgodne z liczbą rekordów.',
        'warning_p': '⚠️ Jeśli nowy plik wejściowy ma inną liczbę Dokumentów/Rejestrów w porównaniu z zapisanymi folderami, wyświetlane jest ostrzeżenie i wybór jest resetowany.',
    },
    'da': {
        'new_h3_1': '1. Indlæs en inputfil (Inputfil → Åbn input): formatvinduet åbner automatisk',
        'alternatively': 'Alternativt: ',
        'formats_saved_p': '✅ <strong>De valgte formater gemmes</strong> og forudvælges automatisk næste gang du åbner programmet.',
        'step2_new_h4': 'TRIN 2: VÆLG OUTPUTMAPPER',
        'step2_h3_1': '1. Mappevinduet åbnes automatisk efter formatvalget (når du indlæser en inputfil)',
        'step2_h3_2': '2. Alternativt: Klik på Menu → "Indstillinger" → "Vælg outputmapper"',
        'step2_h3_3': '3. Vælg MAPPETILSTAND:',
        'radio_single': '⬤ Enkelt mappe til alle',
        'radio_single_desc': 'én mappe for alle poster (dokumenter og registre)',
        'radio_separate': '⬤ Separate mapper doc/reg',
        'radio_separate_desc': 'én mappe for alle dokumenter, én for alle registre',
        'radio_per': '⬤ Mappe per post',
        'radio_per_desc': 'en separat mappe for hver post i inputfilen',
        'step2_h3_4': '4. After choosing the mode, select the required folders (1, 2 or N valgdialogbokse)',
        'step2_h3_5': '5. Til sidst vises en oversigt over alle valgte mapper',
        'folders_saved_p': '✅ <strong>Tilstand og mapper gemmes</strong>. Næste gang du åbner en inputfil, gendannes de automatisk, hvis de er kompatible med antallet af poster.',
        'warning_p': '⚠️ Hvis den nye inputfil har et andet antal Dokumenter/Registre end de gemte mapper, vises en advarsel og valget nulstilles.',
    },
    'no': {
        'new_h3_1': '1. Last inn en inndatafil (Inndatafil → Åpne inndata): formatvinduet åpnes automatisk',
        'alternatively': 'Alternativt: ',
        'formats_saved_p': '✅ <strong>De valgte formatene lagres</strong> og forhåndsvelges automatisk neste gang du åpner programmet.',
        'step2_new_h4': 'STEG 2: VELG UTDATAMAPPER',
        'step2_h3_1': '1. Mappedialogen åpnes automatisk etter formatvalget (når du laster inn en inndatafil)',
        'step2_h3_2': '2. Alternativt: Klikk Meny → «Innstillinger» → «Velg utdatamapper»',
        'step2_h3_3': '3. Velg MAPPEMODUS:',
        'radio_single': '⬤ Enkelt mappe for alle',
        'radio_single_desc': 'én mappe for alle oppføringer (dokumenter og registre)',
        'radio_separate': '⬤ Separate mapper doc/reg',
        'radio_separate_desc': 'én mappe for alle dokumenter, én for alle registre',
        'radio_per': '⬤ Mappe per oppføring',
        'radio_per_desc': 'en separat mappe for hver oppføring i inndatafilen',
        'step2_h3_4': '4. Etter å ha valgt modus, velg de nødvendige mappene (1, 2 eller N velgerdialogbokser)',
        'step2_h3_5': '5. Til slutt vises en oppsummering av alle valgte mapper',
        'folders_saved_p': '✅ <strong>Modus og mapper lagres</strong>. Neste gang du åpner en inndatafil, gjenopprettes de automatisk hvis de er kompatible med antall oppføringer.',
        'warning_p': '⚠️ Hvis den nye inndatafilen har et annet antall Dokumenter/Registre enn de lagrede mappene, vises en advarsel og valget tilbakestilles.',
    },
    'tr': {
        'new_h3_1': '1. Bir giriş dosyası yükleyin (Giriş dosyası → Girişi aç): format penceresi otomatik açılır',
        'alternatively': 'Alternatif olarak: ',
        'formats_saved_p': '✅ <strong>Seçilen formatlar kaydedilir</strong> ve programı bir sonraki açışınızda otomatik olarak önceden seçilir.',
        'step2_new_h4': 'ADIM 2: ÇIKTI KLASÖRLERINI SEÇİN',
        'step2_h3_1': '1. Klasör penceresi format seçiminden sonra otomatik açılır (bir giriş dosyası yüklediğinizde)',
        'step2_h3_2': '2. Alternatif olarak: Menü → "Ayarlar" → "Çıktı klasörlerini seç" seçeneğine tıklayın',
        'step2_h3_3': '3. KLASÖR MODUNU seçin:',
        'radio_single': '⬤ Tümü için tek klasör',
        'radio_single_desc': 'tüm kayıtlar için bir klasör (belgeler ve siciller)',
        'radio_separate': '⬤ Ayrı klasörler doc/reg',
        'radio_separate_desc': 'tüm belgeler için bir klasör, tüm siciller için bir klasör',
        'radio_per': '⬤ Her kayıt için klasör',
        'radio_per_desc': 'giriş dosyasındaki her kayıt için ayrı bir klasör',
        'step2_h3_4': '4. Modu seçtikten sonra gerekli klasörleri seçin (1, 2 veya N seçim iletişim kutusu)',
        'step2_h3_5': '5. Sonunda seçilen tüm klasörlerin özeti gösterilir',
        'folders_saved_p': '✅ <strong>Mod ve klasörler kaydedilir</strong>. Bir sonraki giriş dosyası açılışında, kayıt sayısıyla uyumluysa otomatik olarak geri yüklenir.',
        'warning_p': '⚠️ Yeni giriş dosyasında kaydedilen klasörlerden farklı sayıda Belge/Sicil varsa uyarı gösterilir ve seçim sıfırlanır.',
    },
    'vi': {
        'new_h3_1': '1. Tải tệp đầu vào (Tệp đầu vào → Mở đầu vào): hộp thoại định dạng tự động mở',
        'alternatively': 'Thay thế: ',
        'formats_saved_p': '✅ <strong>Các định dạng đã chọn được lưu</strong> và tự động chọn trước lần tiếp theo bạn mở chương trình.',
        'step2_new_h4': 'BƯỚC 2: CHỌN THƯ MỤC ĐẦU RA',
        'step2_h3_1': '1. Cửa sổ thư mục tự động mở sau khi chọn định dạng (khi bạn tải tệp đầu vào)',
        'step2_h3_2': '2. Thay thế: Nhấp vào Menu → "Cài đặt" → "Chọn thư mục đầu ra"',
        'step2_h3_3': '3. Chọn CHẾ ĐỘ THƯ MỤC:',
        'radio_single': '⬤ Thư mục duy nhất cho tất cả',
        'radio_single_desc': 'một thư mục cho tất cả các bản ghi (tài liệu và sổ đăng ký)',
        'radio_separate': '⬤ Thư mục riêng doc/reg',
        'radio_separate_desc': 'một thư mục cho tất cả tài liệu, một cho tất cả sổ đăng ký',
        'radio_per': '⬤ Thư mục cho mỗi bản ghi',
        'radio_per_desc': 'thư mục riêng cho từng bản ghi trong tệp đầu vào',
        'step2_h3_4': '4. Sau khi chọn chế độ, chọn các thư mục cần thiết (1, 2 hoặc N hộp thoại chọn)',
        'step2_h3_5': '5. Cuối cùng hiển thị tóm tắt tất cả các thư mục đã chọn',
        'folders_saved_p': '✅ <strong>Chế độ và thư mục được lưu</strong>. Lần tiếp theo bạn mở tệp đầu vào, chúng được tự động khôi phục nếu tương thích với số lượng bản ghi.',
        'warning_p': '⚠️ Nếu tệp đầu vào mới có số lượng Tài liệu/Sổ đăng ký khác với thư mục đã lưu, sẽ hiển thị cảnh báo và lựa chọn được đặt lại.',
    },
}

# Step 1 and Step 2 h4 titles (old, for finding; new for replacement)
STEP1_H4 = {
    'es': 'PASO 1: SELECCIONAR FORMATOS DE IMAGEN',
    'de': 'SCHRITT 1: BILDERFORMATE AUSWÄHLEN',
    'fr': "ÉTAPE 1 : SÉLECTIONNER LES FORMATS D'IMAGE",
    'pt': 'PASSO 1: SELECIONAR FORMATOS DE IMAGEM',
    'nl': 'STAP 1: SELECTEER AFBEELDINGSFORMATEN',
    'ar': 'الخطوة 1: اختر تنسيقات الصور',
    'he': 'שלב 1: בחר פורמטים של תמונה',
    'ru': 'ШАГ 1: ВЫБЕРИТЕ ФОРМАТЫ ИЗОБРАЖЕНИЙ',
    'ja': 'ステップ1：画像フォーマットを選択',
    'sv': 'STEG 1: VÄLJ BILDFORMAT',
    'zh': '第一步：选择图片格式',
    'ro': 'PASUL 1: SELECTAȚI FORMATUL IMAGINII',
    'el': 'ΒΗΜΑ 1: ΕΠΙΛΟΓΗ ΜΟΡΦΩΝ ΕΙΚΟΝΑΣ',
    'pl': 'KROK 1: WYBIERZ FORMATY OBRAZU',
    'da': 'TRIN 1: VÆLG BILLEDER',
    'no': 'STEG 1: VELG BILDEFORMATER',
    'tr': 'ADIM 1: GÖRÜNTÜ FORMATLARINI SEÇİN',
    'vi': 'BƯỚC 1: CHỌN ĐỊNH DẠNG ẢNH',
}

STEP2_H4_OLD = {
    'es': 'PASO 2: SELECCIONAR CARPETA DE SALIDA',
    'de': 'SCHRITT 2: AUSGABEVERZEICHNIS AUSWÄHLEN',
    'fr': 'ÉTAPE 2 : SÉLECTIONNER LE DOSSIER DE SORTIE',
    'pt': 'PASSO 2: SELECIONAR PASTA DE SAÍDA',
    'nl': 'STAP 2: SELECTEER UITVOERMAP',
    'ar': 'الخطوة 2: حدد مجلد الإخراج',
    'he': 'שלב 2: בחר תיקיית פלט',
    'ru': 'ШАГ 2: ВЫБЕРИТЕ ВЫХОДНУЮ ПАПКУ',
    'ja': 'ステップ2：出力フォルダを選択',
    'sv': 'STEG 2: VÄLJ UTDATAK\u0e1b\u0e32\u0e23\u0e4c\u0e0a\u0e34',  # mangled - will search differently
    'zh': '步骤 2：选择输出文件夹',
    'ro': 'PASUL 2: SELECTAȚI FOLDERUL DE IEȘIRE',
    'el': 'ΒΗΜΑ 2: ΕΠΙΛΟΓΗ ΦΑΚΕΛΟΥ ΕΞΟΔΟΥ',
    'pl': 'KROK 2: WYBIERZ FOLDER WYJŚCIOWY',
    'da': 'TRIN 2: VÆLG OUTPUTMAPPE',
    'no': 'STEG 2: VELG UTDATAKART',
    'tr': 'ADIM 2: ÇIKTI KLASÖRÜNÜ SEÇİN',
    'vi': 'BƯỚC 2: CHỌN THƯ MỤC OUTPUT',
}

SPAN_STYLE = 'style="background: #f0f0f0; padding: 4px 8px; border-radius: 3px; font-weight: bold; display: inline-block; margin: 0 4px;"'

def build_new_step2(t, sep):
    """Build the new STEP 2 block."""
    lines = []
    lines.append(f'<h4>{t["step2_new_h4"]}</h4>')
    lines.append(f'<p>{sep}</p>')
    lines.append(f'<h3>{t["step2_h3_1"]}</h3>')
    lines.append(f'<h3>{t["step2_h3_2"]}</h3>')
    lines.append(f'<h3>{t["step2_h3_3"]}</h3>')
    lines.append(f'<p><span {SPAN_STYLE}>{t["radio_single"]}</span> → {t["radio_single_desc"]}</p>')
    lines.append(f'<p><span {SPAN_STYLE}>{t["radio_separate"]}</span> → {t["radio_separate_desc"]}</p>')
    lines.append(f'<p><span {SPAN_STYLE}>{t["radio_per"]}</span> → {t["radio_per_desc"]}</p>')
    lines.append(f'<h3>{t["step2_h3_4"]}</h3>')
    lines.append(f'<h3>{t["step2_h3_5"]}</h3>')
    lines.append(f'<p>{t["folders_saved_p"]}</p>')
    lines.append(f'<p>{t["warning_p"]}</p>')
    I = '            '
    return '\n'.join(I + l for l in lines)


total_ok = 0
total_fail = 0

for lang, t in TRANS.items():
    path = f'c:/ATK-Pro_v2.0/assets/{lang}/testuali/guida.html'
    with open(path, 'rb') as f:
        raw = f.read()
    is_crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    
    s1_title = STEP1_H4[lang]
    s2_title_old = STEP2_H4_OLD[lang]
    
    # Find STEP 1 h4
    idx_s1 = text.find(f'<h4>{s1_title}</h4>')
    if idx_s1 == -1:
        print(f'{lang}: STEP 1 not found!')
        total_fail += 1
        continue
    
    # Find STEP 2 h4 (search by pattern after STEP 1)
    # Use a pattern that matches the step2 structure
    region = text[idx_s1:idx_s1+6000]
    # Find old STEP 2 h4
    if s2_title_old and s2_title_old in region:
        s2_rel = region.find(f'<h4>{s2_title_old}</h4>')
        idx_s2 = idx_s1 + s2_rel
        s2_old_tag = f'<h4>{s2_title_old}</h4>'
    else:
        # Search for any h4 that looks like step 2
        m = re.search(r'<h4>[^<]*(?:2[：:]).+?</h4>', region[100:])
        if not m:
            print(f'{lang}: STEP 2 not found! Searching...')
            # Print all h4s in region
            for mh in re.finditer(r'<h4>[^<]+</h4>', region[100:]):
                print(f'  h4: {repr(mh.group())}')
            total_fail += 1
            continue
        idx_s2 = idx_s1 + 100 + m.start()
        s2_old_tag = m.group()
    
    # Find the separator line in STEP 1 (the ──── paragraph)
    sep_match = re.search(r'<p>─+</p>', region[:1000])
    sep_line = sep_match.group() if sep_match else '<p>──────────────────────────────────────</p>'
    sep_text = re.sub(r'</?p>', '', sep_line).strip()
    
    # === MODIFY STEP 1 ===
    # Extract the STEP 1 block (from s1 h4 to s2 h4 exclusive)
    step1_block = text[idx_s1:idx_s2]
    
    # In the step1_block:
    # 1. Renumber h3s: 4→5, 3→4, 2→3, 1→2 (in reverse order to avoid double-changing)
    def renumber_h3_in_block(blk):
        # Only change h3 numbered steps (not other h3 that might be in TIPS)
        # Find all h3 numbered steps, renumber them
        # Do in reverse order: 4→5, 3→4, 2→3, 1→2
        for n in range(5, 0, -1):  # 5, 4, 3, 2, 1
            blk = blk.replace(f'<h3>{n}.', f'<h3>{n+1}.', 1)
        return blk
    
    # Find the separator in step1_block and apply renumbering only after it
    sep_idx = step1_block.find('<p>─')
    if sep_idx >= 0:
        sep_end = step1_block.find('</p>', sep_idx) + 4
        before_sep = step1_block[:sep_end]
        after_sep = renumber_h3_in_block(step1_block[sep_end:])
        step1_block_new = before_sep + after_sep
    else:
        step1_block_new = renumber_h3_in_block(step1_block)
    
    # 2. Insert new h3.1 after the separator
    insert_after = sep_end if sep_idx >= 0 else step1_block_new.find('<h3>2.')
    if insert_after > 0:
        new_h3_1_line = f'\n            <h3>{t["new_h3_1"]}</h3>'
        step1_block_new = step1_block_new[:insert_after] + new_h3_1_line + step1_block_new[insert_after:]
    
    # 3. Add ✅ note before the TIPS h4
    tips_h4_match = re.search(r'<h4>📝', step1_block_new)
    if tips_h4_match:
        tips_pos = tips_h4_match.start()
        formats_note = f'            <p>{t["formats_saved_p"]}</p>\n'
        step1_block_new = step1_block_new[:tips_pos] + formats_note + step1_block_new[tips_pos:]
    else:
        # Add at the end of step1 block
        step1_block_new = step1_block_new.rstrip() + f'\n            <p>{t["formats_saved_p"]}</p>\n'
    
    # === BUILD NEW STEP 2 ===
    new_step2 = build_new_step2(t, sep_text)
    
    # Find end of old STEP 2 block (next h4 that's not a sub-heading)
    step2_region = text[idx_s2:]
    # Find h4 markers after the STEP 2 h4 tag
    step2_h4_len = len(s2_old_tag)
    # The end of STEP 2 is the next h4 (STEP 3 or 📌 IMPORTANTE or similar)
    next_h4_match = re.search(r'<h4>', step2_region[step2_h4_len:])
    if next_h4_match:
        step2_block_end = idx_s2 + step2_h4_len + next_h4_match.start()
        old_step2_block = text[idx_s2:step2_block_end]
    else:
        # Fallback: take 2000 chars
        old_step2_block = text[idx_s2:idx_s2+2000]
        step2_block_end = idx_s2 + 2000
    
    # === ASSEMBLE NEW TEXT ===
    new_step2_with_nl = new_step2 + '\n'
    new_text = text[:idx_s1] + step1_block_new + new_step2_with_nl + text[step2_block_end:]
    
    if is_crlf:
        out_bytes = new_text.replace('\n', '\r\n').encode('utf-8')
    else:
        out_bytes = new_text.encode('utf-8')
    
    with open(path, 'wb') as f:
        f.write(out_bytes)
    
    print(f'{lang}: OK (STEP1: {len(text[idx_s1:idx_s2])}→{len(step1_block_new)}, STEP2: {len(old_step2_block)}→{len(new_step2)})')
    total_ok += 1

print(f'\nDone: {total_ok} OK, {total_fail} FAIL')
