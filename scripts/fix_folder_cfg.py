import re, os

BASE = 'c:/ATK-Pro_v2.0/assets'

I18 = '            '   # 12 spaces
I20 = '                ' # 16 spaces

LANGS = {
    'fr': {
        'h4': 'CONFIGURATION DES DOSSIERS',
        'intro': 'Lors de la premi\u00e8re ex\u00e9cution, le programme cr\u00e9e automatiquement les dossiers suivants\u00a0:',
        'win': '<strong>Windows\u00a0:</strong> <code>C:\\Users\\[VotreNom]\\Documents\\ATK-Pro\\output\\</code>',
        'win_doc': '<strong>Windows\u00a0:</strong> <code>C:\\Users\\[VotreNom]\\Documents\\ATK-Pro\\output\\doc\\</code> (par d\u00e9faut pour les documents)',
        'win_reg': '<strong>Windows\u00a0:</strong> <code>C:\\Users\\[VotreNom]\\Documents\\ATK-Pro\\output\\reg\\</code> (par d\u00e9faut pour les registres)',
        'linux': '<strong>Linux/macOS\u00a0:</strong> analogues sous <code>~/Documents/ATK-Pro/output/</code>',
        'input': 'Dossier <code>input/</code> correspondant (facultatif)',
        'final': 'Pour modifier les dossiers de sortie, utilisez Menu \u2192 Param\u00e8tres \u2192 \u00ab\u00a0S\u00e9lectionner les dossiers de sortie\u00a0\u00bb. Vos choix sont sauvegard\u00e9s et restaur\u00e9s automatiquement \u00e0 la prochaine session.',
    },
    'ru': {
        'h4': '\u041d\u0410\u0421\u0422\u0420\u041e\u0419\u041a\u0410 \u041f\u0410\u041f\u041e\u041a',
        'intro': '\u041f\u0440\u0438 \u043f\u0435\u0440\u0432\u043e\u043c \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0438 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0430 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0441\u043e\u0437\u0434\u0430\u0451\u0442 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0435 \u043f\u0430\u043f\u043a\u0438:',
        'win': '<strong>Windows:</strong> <code>C:\\Users\\[\u0418\u043c\u044f]\\Documents\\ATK-Pro\\output\\</code>',
        'win_doc': '<strong>Windows:</strong> <code>C:\\Users\\[\u0418\u043c\u044f]\\Documents\\ATK-Pro\\output\\doc\\</code> (\u043f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e \u0434\u043b\u044f \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u043e\u0432)',
        'win_reg': '<strong>Windows:</strong> <code>C:\\Users\\[\u0418\u043c\u044f]\\Documents\\ATK-Pro\\output\\reg\\</code> (\u043f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e \u0434\u043b\u044f \u0440\u0435\u0435\u0441\u0442\u0440\u043e\u0432)',
        'linux': '<strong>Linux/macOS:</strong> \u0430\u043d\u0430\u043b\u043e\u0433\u0438\u0447\u043d\u043e \u0432 <code>~/Documents/ATK-Pro/output/</code>',
        'input': '\u0421\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0449\u0430\u044f \u043f\u0430\u043f\u043a\u0430 <code>input/</code> (\u043d\u0435\u043e\u0431\u044f\u0437\u0430\u0442\u0435\u043b\u044c\u043d\u043e)',
        'final': '\u0414\u043b\u044f \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u043f\u0430\u043f\u043e\u043a \u0432\u044b\u0432\u043e\u0434\u0430 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435 \u041c\u0435\u043d\u044e \u2192 \u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u2192 \u00ab\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u043f\u0430\u043f\u043a\u0438 \u0432\u044b\u0432\u043e\u0434\u0430\u00bb. \u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0441\u043e\u0445\u0440\u0430\u043d\u044f\u044e\u0442\u0441\u044f \u0438 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0432\u043e\u0441\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u044e\u0442\u0441\u044f \u043f\u0440\u0438 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0435\u043c \u0437\u0430\u043f\u0443\u0441\u043a\u0435.',
    },
    'ja': {
        'h4': '\u30d5\u30a9\u30eb\u30c0\u8a2d\u5b9a',
        'intro': '\u521d\u56de\u5b9f\u884c\u6642\u306b\u3001\u30d7\u30ed\u30b0\u30e9\u30e0\u306f\u4ee5\u4e0b\u306e\u30d5\u30a9\u30eb\u30c0\u30fc\u3092\u81ea\u52d5\u7684\u306b\u4f5c\u6210\u3057\u307e\u3059\uff1a',
        'win': '<strong>Windows\uff1a</strong><code>C:\\Users\\[\u30e6\u30fc\u30b6\u30fc\u540d]\\Documents\\ATK-Pro\\output\\</code>',
        'win_doc': '<strong>Windows\uff1a</strong><code>C:\\Users\\[\u30e6\u30fc\u30b6\u30fc\u540d]\\Documents\\ATK-Pro\\output\\doc\\</code>\uff08\u30c9\u30ad\u30e5\u30e1\u30f3\u30c8\u306e\u30c7\u30d5\u30a9\u30eb\u30c8\uff09',
        'win_reg': '<strong>Windows\uff1a</strong><code>C:\\Users\\[\u30e6\u30fc\u30b6\u30fc\u540d]\\Documents\\ATK-Pro\\output\\reg\\</code>\uff08\u30ec\u30b8\u30b9\u30bf\u30fc\u306e\u30c7\u30d5\u30a9\u30eb\u30c8\uff09',
        'linux': '<strong>Linux/macOS\uff1a</strong><code>~/Documents/ATK-Pro/output/</code>\u4ee5\u4e0b\u306b\u540c\u69d8',
        'input': '\u5bfe\u5fdc\u3059\u308b<code>input/</code>\u30d5\u30a9\u30eb\u30c0\uff08\u30aa\u30d7\u30b7\u30e7\u30f3\uff09',
        'final': '\u51fa\u529b\u30d5\u30a9\u30eb\u30c0\u30fc\u3092\u5909\u66f4\u3059\u308b\u306b\u306f\u30e1\u30cb\u30e5\u30fc \u2192 \u8a2d\u5b9a \u2192 \u300c\u51fa\u529b\u30d5\u30a9\u30eb\u30c0\u30fc\u3092\u9078\u629e\u300d\u3092\u4f7f\u7528\u3057\u307e\u3059\u3002\u8a2d\u5b9a\u306f\u4fdd\u5b58\u3055\u308c\u3001\u6b21\u56de\u8d77\u52d5\u6642\u306b\u81ea\u52d5\u7684\u306b\u5fa9\u5143\u3055\u308c\u307e\u3059\u3002',
    },
    'sv': {
        'h4': 'KONFIGURATIONSKATALOGER',
        'intro': 'Vid f\u00f6rsta k\u00f6rningen skapar programmet automatiskt f\u00f6ljande mappar:',
        'win': '<strong>Windows:</strong> <code>C:\\Users\\[DittNamn]\\Documents\\ATK-Pro\\output\\</code>',
        'win_doc': '<strong>Windows:</strong> <code>C:\\Users\\[DittNamn]\\Documents\\ATK-Pro\\output\\doc\\</code> (standard f\u00f6r dokument)',
        'win_reg': '<strong>Windows:</strong> <code>C:\\Users\\[DittNamn]\\Documents\\ATK-Pro\\output\\reg\\</code> (standard f\u00f6r register)',
        'linux': '<strong>Linux/macOS:</strong> analogt under <code>~/Documents/ATK-Pro/output/</code>',
        'input': 'Motsvarande <code>input/</code>-mapp (valfritt)',
        'final': 'F\u00f6r att \u00e4ndra utdatamapparna, anv\u00e4nd Meny \u2192 Inst\u00e4llningar \u2192 \u201eV\u00e4lj utdatamappar\u201f. Dina val sparas och \u00e5terst\u00e4lls automatiskt vid n\u00e4sta session.',
    },
    'zh': {
        'h4': '\u6587\u4ef6\u5939\u914d\u7f6e',
        'intro': '\u9996\u6b21\u8fd0\u884c\u65f6\uff0c\u7a0b\u5e8f\u4f1a\u81ea\u52a8\u521b\u5efa\u4ee5\u4e0b\u6587\u4ef6\u5939\uff1a',
        'win': '<strong>Windows\uff1a</strong><code>C:\\Users\\[\u60a8\u7684\u540d\u5b57]\\Documents\\ATK-Pro\\output\\</code>',
        'win_doc': '<strong>Windows\uff1a</strong><code>C:\\Users\\[\u60a8\u7684\u540d\u5b57]\\Documents\\ATK-Pro\\output\\doc\\</code>\uff08\u6587\u4ef6\u7684\u9ed8\u8ba4\u6587\u4ef6\u5939\uff09',
        'win_reg': '<strong>Windows\uff1a</strong><code>C:\\Users\\[\u60a8\u7684\u540d\u5b57]\\Documents\\ATK-Pro\\output\\reg\\</code>\uff08\u767b\u8bb0\u518c\u7684\u9ed8\u8ba4\u6587\u4ef6\u5939\uff09',
        'linux': '<strong>Linux/macOS\uff1a</strong><code>~/Documents/ATK-Pro/output/</code>\u4e0b\u7c7b\u4f3c',
        'input': '\u5bf9\u5e94\u7684 <code>input/</code> \u6587\u4ef6\u5939\uff08\u53ef\u9009\uff09',
        'final': '\u8981\u4fee\u6539\u8f93\u51fa\u6587\u4ef6\u5939\uff0c\u8bf7\u4f7f\u7528\u83dc\u5355 \u2192 \u8bbe\u7f6e \u2192 \u201c\u9009\u62e9\u8f93\u51fa\u6587\u4ef6\u5939\u201d\u3002\u60a8\u7684\u9009\u62e9\u5df2\u4fdd\u5b58\uff0c\u4e0b\u6b21\u542f\u52a8\u65f6\u81ea\u52a8\u6062\u590d\u3002',
    },
    'ro': {
        'h4': 'CONFIGURARE FOLDERE',
        'intro': 'La prima rulare, programul creeaz\u0103 automat urm\u0103toarele foldere:',
        'win': '<strong>Windows:</strong> <code>C:\\Users\\[NumeleTau]\\Documents\\ATK-Pro\\output\\</code>',
        'win_doc': '<strong>Windows:</strong> <code>C:\\Users\\[NumeleTau]\\Documents\\ATK-Pro\\output\\doc\\</code> (implicit pentru documente)',
        'win_reg': '<strong>Windows:</strong> <code>C:\\Users\\[NumeleTau]\\Documents\\ATK-Pro\\output\\reg\\</code> (implicit pentru registre)',
        'linux': '<strong>Linux/macOS:</strong> similar sub <code>~/Documents/ATK-Pro/output/</code>',
        'input': 'Folderul <code>input/</code> corespunz\u0103tor (op\u0163ional)',
        'final': 'Pentru a modifica folderele de ie\u015fire, folose\u015fte Meniu \u2192 Set\u0103ri \u2192 \u201eSelecteaz\u0103 folderele de ie\u015fire\u201f. Alegerile tale sunt salvate \u015fi restaurate automat la urm\u0103toarea sesiune.',
    },
    'el': {
        'h4': '\u0394\u0399\u0391\u039c\u039f\u03a1\u03a6\u03a9\u03a3\u0397 \u03a6\u0391\u039a\u0395\u039b\u03a9\u039d',
        'intro': '\u039a\u03b1\u03c4\u03ac \u03c4\u03b7\u03bd \u03c0\u03c1\u03ce\u03c4\u03b7 \u03b5\u03ba\u03c4\u03ad\u03bb\u03b5\u03c3\u03b7, \u03c4\u03bf \u03c0\u03c1\u03cc\u03b3\u03c1\u03b1\u03bc\u03bc\u03b1 \u03b4\u03b7\u03bc\u03b9\u03bf\u03c5\u03c1\u03b3\u03b5\u03af \u03b1\u03c5\u03c4\u03cc\u03bc\u03b1\u03c4\u03b1 \u03c4\u03bf\u03c5\u03c2 \u03b5\u03be\u03ae\u03c2 \u03c6\u03b1\u03ba\u03ad\u03bb\u03bf\u03c5\u03c2:',
        'win': '<strong>Windows:</strong> <code>C:\\Users\\[\u038c\u03bd\u03bf\u03bc\u03b1]\\Documents\\ATK-Pro\\output\\</code>',
        'win_doc': '<strong>Windows:</strong> <code>C:\\Users\\[\u038c\u03bd\u03bf\u03bc\u03b1]\\Documents\\ATK-Pro\\output\\doc\\</code> (\u03c0\u03c1\u03bf\u03b5\u03c0\u03b9\u03bb\u03bf\u03b3\u03ae \u03b3\u03b9\u03b1 \u03ad\u03b3\u03b3\u03c1\u03b1\u03c6\u03b1)',
        'win_reg': '<strong>Windows:</strong> <code>C:\\Users\\[\u038c\u03bd\u03bf\u03bc\u03b1]\\Documents\\ATK-Pro\\output\\reg\\</code> (\u03c0\u03c1\u03bf\u03b5\u03c0\u03b9\u03bb\u03bf\u03b3\u03ae \u03b3\u03b9\u03b1 \u03bc\u03b7\u03c4\u03c1\u03ce\u03b1)',
        'linux': '<strong>Linux/macOS:</strong> \u03b1\u03bd\u03ac\u03bb\u03bf\u03b3\u03b1 \u03c5\u03c0\u03cc <code>~/Documents/ATK-Pro/output/</code>',
        'input': '\u039f \u03b1\u03bd\u03c4\u03af\u03c3\u03c4\u03bf\u03b9\u03c7\u03bf\u03c2 \u03c6\u03ac\u03ba\u03b5\u03bb\u03bf\u03c2 <code>input/</code> (\u03c0\u03c1\u03b1\u03b9\u03c1\u03b5\u03c4\u03b9\u03ba\u03cc)',
        'final': '\u0393\u03b9\u03b1 \u03b1\u03bb\u03bb\u03b1\u03b3\u03ae \u03c6\u03b1\u03ba\u03ad\u03bb\u03c9\u03bd \u03b5\u03be\u03cc\u03b4\u03bf\u03c5 \u03c7\u03c1\u03b7\u03c3\u03b9\u03bc\u03bf\u03c0\u03bf\u03b9\u03ae\u03c3\u03c4\u03b5 \u039c\u03b5\u03bd\u03bf\u03cd \u2192 \u03a1\u03c5\u03b8\u03bc\u03af\u03c3\u03b5\u03b9\u03c2 \u2192 \u201c\u0395\u03c0\u03b9\u03bb\u03bf\u03b3\u03ae \u03c6\u03b1\u03ba\u03ad\u03bb\u03c9\u03bd \u03b5\u03be\u03cc\u03b4\u03bf\u03c5\u201d. \u039f\u03b9 \u03b5\u03c0\u03b9\u03bb\u03bf\u03b3\u03ad\u03c2 \u03c3\u03b1\u03c2 \u03b1\u03c0\u03bf\u03b8\u03b7\u03ba\u03b5\u03cd\u03bf\u03bd\u03c4\u03b1\u03b9 \u03ba\u03b1\u03b9 \u03b5\u03c0\u03b1\u03bd\u03b1\u03c6\u03ad\u03c1\u03bf\u03bd\u03c4\u03b1\u03b9 \u03b1\u03c5\u03c4\u03cc\u03bc\u03b1\u03c4\u03b1 \u03c3\u03c4\u03b7\u03bd \u03b5\u03c0\u03cc\u03bc\u03b5\u03bd\u03b7 \u03c3\u03b5\u03c3\u03af\u03b1.',
    },
    'pl': {
        'h4': 'KONFIGURACJA FOLDER\u00d3W',
        'intro': 'Przy pierwszym uruchomieniu program automatycznie tworzy nast\u0119puj\u0105ce foldery:',
        'win': '<strong>Windows:</strong> <code>C:\\Users\\[TwojeImie]\\Documents\\ATK-Pro\\output\\</code>',
        'win_doc': '<strong>Windows:</strong> <code>C:\\Users\\[TwojeImie]\\Documents\\ATK-Pro\\output\\doc\\</code> (domy\u015blny dla dokument\u00f3w)',
        'win_reg': '<strong>Windows:</strong> <code>C:\\Users\\[TwojeImie]\\Documents\\ATK-Pro\\output\\reg\\</code> (domy\u015blny dla rejestr\u00f3w)',
        'linux': '<strong>Linux/macOS:</strong> analogicznie pod <code>~/Documents/ATK-Pro/output/</code>',
        'input': 'Odpowiadaj\u0105cy folder <code>input/</code> (opcjonalnie)',
        'final': 'Aby zmieni\u0107 foldery wyj\u015bciowe, u\u017cyj Menu \u2192 Ustawienia \u2192 \u201eWybierz foldery wyj\u015bciowe\u201f. Twoje wybory s\u0105 zapisywane i automatycznie przywracane przy nast\u0119pnej sesji.',
    },
    'da': {
        'h4': 'MAPPEKONFIGURATION',
        'intro': 'Ved f\u00f8rste k\u00f8rsel opretter programmet automatisk f\u00f8lgende mapper:',
        'win': '<strong>Windows:</strong> <code>C:\\Users\\[DitNavn]\\Documents\\ATK-Pro\\output\\</code>',
        'win_doc': '<strong>Windows:</strong> <code>C:\\Users\\[DitNavn]\\Documents\\ATK-Pro\\output\\doc\\</code> (standard for dokumenter)',
        'win_reg': '<strong>Windows:</strong> <code>C:\\Users\\[DitNavn]\\Documents\\ATK-Pro\\output\\reg\\</code> (standard for registre)',
        'linux': '<strong>Linux/macOS:</strong> tilsvarende under <code>~/Documents/ATK-Pro/output/</code>',
        'input': 'Tilsvarende <code>input/</code>-mappe (valgfrit)',
        'final': 'For at \u00e6ndre outputmapperne skal du bruge Menu \u2192 Indstillinger \u2192 \u201eV\u00e6lg outputmapper\u201f. Dine valg gemmes og gendannes automatisk ved n\u00e6ste session.',
    },
    'no': {
        'h4': 'MAPPEKONFIGURASJON',
        'intro': 'Ved f\u00f8rste kj\u00f8ring oppretter programmet automatisk f\u00f8lgende mapper:',
        'win': '<strong>Windows:</strong> <code>C:\\Users\\[DittNavn]\\Documents\\ATK-Pro\\output\\</code>',
        'win_doc': '<strong>Windows:</strong> <code>C:\\Users\\[DittNavn]\\Documents\\ATK-Pro\\output\\doc\\</code> (standard for dokumenter)',
        'win_reg': '<strong>Windows:</strong> <code>C:\\Users\\[DittNavn]\\Documents\\ATK-Pro\\output\\reg\\</code> (standard for registre)',
        'linux': '<strong>Linux/macOS:</strong> tilsvarende under <code>~/Documents/ATK-Pro/output/</code>',
        'input': 'Tilsvarende <code>input/</code>-mappe (valgfritt)',
        'final': 'For \u00e5 endre utdatamappene bruker du Meny \u2192 Innstillinger \u2192 \u00abVelg utdatamapper\u00bb. Valgene dine lagres og gjenopprettes automatisk ved neste \u00f8kt.',
    },
    'tr': {
        'h4': 'KLAS\u00d6R YAPILANDIRMASI',
        'intro': 'Program ilk \u00e7al\u0131\u015ft\u0131r\u0131ld\u0131\u011f\u0131nda otomatik olarak \u015fu klas\u00f6rleri olu\u015fturur:',
        'win': '<strong>Windows:</strong> <code>C:\\Users\\[Adiniz]\\Documents\\ATK-Pro\\output\\</code>',
        'win_doc': '<strong>Windows:</strong> <code>C:\\Users\\[Adiniz]\\Documents\\ATK-Pro\\output\\doc\\</code> (belgeler i\u00e7in varsay\u0131lan)',
        'win_reg': '<strong>Windows:</strong> <code>C:\\Users\\[Adiniz]\\Documents\\ATK-Pro\\output\\reg\\</code> (siciller i\u00e7in varsay\u0131lan)',
        'linux': '<strong>Linux/macOS:</strong> benzer \u015fekilde <code>~/Documents/ATK-Pro/output/</code> alt\u0131nda',
        'input': 'Kar\u015f\u0131l\u0131k gelen <code>input/</code> klas\u00f6r\u00fc (iste\u011fe ba\u011fl\u0131)',
        'final': '\u00c7\u0131kt\u0131 klas\u00f6rlerini de\u011fi\u015ftirmek i\u00e7in Men\u00fc \u2192 Ayarlar \u2192 "\u00c7\u0131kt\u0131 klas\u00f6rlerini se\u00e7" kullan\u0131n. Se\u00e7imleriniz kaydedilir ve bir sonraki oturumda otomatik olarak geri y\u00fcklenir.',
    },
    'vi': {
        'h4': 'C\u1ea4U H\u00ccNH TH\u01af M\u1ee4C',
        'intro': 'Khi ch\u1ea1y l\u1ea7n \u0111\u1ea7u, ch\u01b0\u01a1ng tr\u00ecnh t\u1ef1 \u0111\u1ed9ng t\u1ea1o c\u00e1c th\u01b0 m\u1ee5c sau:',
        'win': '<strong>Windows:</strong> <code>C:\\Users\\[TenBan]\\Documents\\ATK-Pro\\output\\</code>',
        'win_doc': '<strong>Windows:</strong> <code>C:\\Users\\[TenBan]\\Documents\\ATK-Pro\\output\\doc\\</code> (m\u1eb7c \u0111\u1ecbnh cho t\u00e0i li\u1ec7u)',
        'win_reg': '<strong>Windows:</strong> <code>C:\\Users\\[TenBan]\\Documents\\ATK-Pro\\output\\reg\\</code> (m\u1eb7c \u0111\u1ecbnh cho s\u1ed5 \u0111\u0103ng k\u00fd)',
        'linux': '<strong>Linux/macOS:</strong> t\u01b0\u01a1ng t\u1ef1 trong <code>~/Documents/ATK-Pro/output/</code>',
        'input': 'Th\u01b0 m\u1ee5c <code>input/</code> t\u01b0\u01a1ng \u1ee9ng (t\u00f9y ch\u1ecdn)',
        'final': '\u0110\u1ec3 thay \u0111\u1ed5i th\u01b0 m\u1ee5c \u0111\u1ea7u ra, s\u1eed d\u1ee5ng Menu \u2192 C\u00e0i \u0111\u1eb7t \u2192 \u201cCh\u1ecdn th\u01b0 m\u1ee5c \u0111\u1ea7u ra\u201d. L\u1ef1a ch\u1ecdn \u0111\u01b0\u1ee3c l\u01b0u v\u00e0 t\u1ef1 \u0111\u1ed9ng kh\u00f4i ph\u1ee5c khi b\u1eaft \u0111\u1ea7u phi\u00ean ti\u1ebfp theo.',
    },
}


def build_new_block(d, temp_paras):
    new = (
        I18 + f'<h4>\U0001f4c2 {d["h4"]}</h4>\n' +
        I18 + f'<p>{d["intro"]}</p>\n' +
        I18 + '<ul>\n' +
        I20 + f'<li>{d["win"]}</li>\n' +
        I20 + f'<li>{d["win_doc"]}</li>\n' +
        I20 + f'<li>{d["win_reg"]}</li>\n' +
        I20 + f'<li>{d["linux"]}</li>\n' +
        I20 + f'<li>{d["input"]}</li>\n' +
        I18 + '</ul>' +
        temp_paras +
        I18 + f'<p>{d["final"]}</p>'
    )
    return new


total_ok = 0
total_fail = 0

for lang, d in LANGS.items():
    path = f'c:/ATK-Pro_v2.0/assets/{lang}/testuali/guida.html'

    with open(path, 'rb') as f:
        raw = f.read()
    is_crlf = b'\r\n' in raw

    # Work in LF-normalized text
    text = raw.decode('utf-8').replace('\r\n', '\n')

    h4_pos = text.find('<h4>\U0001f4c2')
    if h4_pos == -1:
        print(f'{lang}: h4 NOT FOUND!')
        total_fail += 1
        continue

    ul1_end = text.find('</ul>', h4_pos) + 5
    ul2_end = text.find('</ul>', ul1_end) + 5

    old_block = text[h4_pos:ul2_end]

    # Temp paras: from end of first </ul> to start of last <p> before second <ul>
    last_p_before_ul2 = text.rfind('<p>', h4_pos, text.find('</ul>', ul1_end))
    temp_paras = text[ul1_end:last_p_before_ul2]

    new_block = build_new_block(d, temp_paras)

    if old_block not in text:
        print(f'{lang}: OLD BLOCK NOT FOUND IN TEXT!')
        total_fail += 1
        continue

    new_text = text.replace(old_block, new_block, 1)

    if is_crlf:
        out_bytes = new_text.replace('\n', '\r\n').encode('utf-8')
    else:
        out_bytes = new_text.encode('utf-8')

    with open(path, 'wb') as f:
        f.write(out_bytes)

    print(f'{lang}: OK ({"CRLF" if is_crlf else "LF"}) {len(old_block)}->{len(new_block)} chars')
    total_ok += 1

print(f'\nDone: {total_ok} OK, {total_fail} FAIL')
