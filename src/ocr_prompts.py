"""
Prompt di base per l'OCR Avanzato, divisi per tipologia documentale.
Ogni tipo fornisce linee guida paleografiche specifiche all'IA.
"""


def get_available_types():
    return [
        "Atto di Stato Civile (Nascita / Battesimo)",
        "Atto di Stato Civile (Matrimonio)",
        "Atto di Stato Civile (Morte / Sepoltura)",
        "Processetto / Allegati Matrimoniali",
        "Stati delle Anime Granducato di Toscana",
        "Stato delle Anime / Censimento Parrocchiale",
        "Censimento Storico (Generico)",
        "Indice / Registro degli Atti",
        "Documento Notarile",
        "Atto in Latino Ecclesiastico",
        "Lettera / Corrispondenza Privata",
        "Testo a Stampa Antico",
        "Documento Generico / Non Classificato",
    ]


def compose_ocr_prompt(doc_type, user_instructions="", example_text=""):
    """
    Costruisce il prompt per la trascrizione paleografica in base alla tipologia.
    """
    base = (
        "Sei un esperto paleografo con specializzazione in documenti storici italiani.\n"
        "COMPITO: Trascrivi FEDELMENTE il testo contenuto nell'immagine.\n\n"
        "REGOLE ASSOLUTE:\n"
        "1. Non normalizzare nomi propri, cognomi o termini dialettali: trascrivili esattamente come scritti.\n"
        "2. Mantieni la disposizione del testo originale (a capo, paragrafi, colonne).\n"
        "3. Indica le letture incerte con [?] immediatamente dopo la parola dubia.\n"
        "4. Sciogli le abbreviazioni ovvie tra parentesi angolate < >.\n"
        "5. Non aggiungere commenti, titoli o note a margine: solo il testo trascritto.\n"
    )

    type_specific = {
        "Atto di Stato Civile (Nascita / Battesimo)": (
            "\nTIPOLOGIA: Atto di nascita o battesimo (XIX secolo, registro civile o parrocchiale).\n"
            "- Campi chiave: nome del neonato, genitori (padre e madre con cognome da nubile),"
            " data e luogo di nascita, testimoni, ufficiale o parroco.\n"
            "- I nomi di persona sono spesso abbreviati (Gio. = Giovanni, Batta. = Battista, Fran.co = Francesco).\n"
            "- Il termine 'fu' indica genitore defunto (es. 'figlio di Giovanni fu Isidoro'): trascrivilo letteralmente.\n"
            "- Le date sono in lettere: 'il giorno tre maggio milleottocentosei'.\n"
            "- MARGINALIA: trascrivi qualsiasi annotazione a margine separandola con il tag [MARGINE: ...].\n"
            "- Per cognomi dialettali con variante fonetica plausibile, aggiungi la variante subito dopo"
            " tra parentesi quadre: es. Bortolato [Bortolotti].\n"
            "- Se la pagina contiene PIÙ DI UN ATTO, separa ciascuno con la riga '--- ATTO N ---'"
            " (dove N è il numero progressivo), prima di ogni atto incluso il primo.\n"
        ),
        "Atto di Stato Civile (Matrimonio)": (
            "\nTIPOLOGIA: Atto di matrimonio (XIX secolo, registro civile o parrocchiale).\n"
            "- Campi chiave: sposo e sposa (nome, cognome, età, professione, domicilio),"
            " padri e madri di entrambi (con 'fu' se defunti), testimoni.\n"
            "- Il termine 'fu' indica genitore defunto: trascrivilo letteralmente.\n"
            "- Frequenti formule latine come 'in facie Ecclesiae' nei registri parrocchiali.\n"
            "- MARGINALIA: trascrivi annotazioni a margine (spesso rimandano a successive nascite o morti)"
            " separandole con il tag [MARGINE: ...].\n"
            "- Per cognomi dialettali con variante fonetica plausibile, aggiungi la variante tra parentesi"
            " quadre: es. Mancuso [Mancusa].\n"
            "- Se la pagina contiene PIÙ DI UN ATTO, separa ciascuno con la riga '--- ATTO N ---'"
            " (dove N è il numero progressivo), prima di ogni atto incluso il primo.\n"
        ),
        "Atto di Stato Civile (Morte / Sepoltura)": (
            "\nTIPOLOGIA: Atto di morte o sepoltura (XIX secolo).\n"
            "- Campi chiave: nome e cognome del defunto, età, causa di morte (se indicata),"
            " data e luogo del decesso, dichiaranti, sepoltura.\n"
            "- Il termine 'fu' indica genitore defunto: trascrivilo letteralmente.\n"
            "- Presta attenzione ai termini medici arcaici per le cause di morte.\n"
            "- MARGINALIA: trascrivi annotazioni a margine separandole con il tag [MARGINE: ...].\n"
            "- Per cognomi con variante fonetica plausibile (defunto, dichiaranti o testimoni),"
            " aggiungi la variante tra parentesi quadre: es. Ricci [Rizzi].\n"
            "- Se la pagina contiene PIÙ DI UN ATTO, separa ciascuno con la riga '--- ATTO N ---'"
            " (dove N è il numero progressivo), prima di ogni atto incluso il primo.\n"
        ),
        "Processetto / Allegati Matrimoniali": (
            "\nTIPOLOGIA: Processetto matrimoniale o allegati (documenti istruttori pre-matrimonio).\n"
            "Il processetto include: interrogatori degli sposi e dei testimoni, estratti di battesimo,"
            " estratti di morte dei genitori defunti, eventuali dispense.\n"
            "- Identifica e trascrivi le singole sezioni: intestazione dell'ufficio,"
            " domande del cancelliere, risposte dei comparenti, sottoscrizioni e sigilli.\n"
            "- I comparenti indicano spesso 'figlio/a di ... fu ...' (genitore defunto):"
            " trascrivi 'fu' letteralmente.\n"
            "- Le deposizioni testimoniali iniziano tipicamente con formule come"
            " 'Comparso avanti di me...' o 'Il sottoscritto dichiara...'.\n"
            "- Le dispense papali o vescovili hanno intestazioni in latino: trascrivile integralmente.\n"
            "- Ogni documento all'interno del fascicolo va separato con una riga vuota e il tag"
            " [DOCUMENTO N:] come intestazione.\n"
            "- MARGINALIA: trascrivi annotazioni a margine separandole con il tag [MARGINE: ...].\n"
            "- Se un singolo foglio contiene più deposizioni o atti distinti, separa ciascuno con"
            " '--- ATTO N ---' prima di ogni sezione.\n"
        ),
        "Stati delle Anime Granducato di Toscana": (
            "\nTIPOLOGIA: Stato delle Anime del Granducato di Toscana"
            " (formato codificato dalle Sovrane Disposizioni — Biglietto della R. Segreteria di Stato 12 novembre 1840).\n"
            "\nSTRUTTURA DELLE COLONNE (FISSA PER LEGGE — leggi TUTTE le colonne per ogni riga):\n"
            "  Col.1  = N° Casa\n"
            "  Col.2  = N° Famiglia\n"
            "  Col.3  = N° Progressivo Persona\n"
            "  Col.4  = Cognome\n"
            "  Col.5  = Nome\n"
            "  Col.6  = Età\n"
            "  Col.7  = Stato civile Maschio: Celibe (barrare)\n"
            "  Col.8  = Stato civile Maschio: Ammogliato (barrare)\n"
            "  Col.9  = Stato civile Maschio: Vedovo (barrare)\n"
            "  Col.10 = Stato civile Femmina: Nubile (barrare)\n"
            "  Col.11 = Stato civile Femmina: Maritata (barrare)\n"
            "  Col.12 = Stato civile Femmina: Vedova (barrare)\n"
            "  Col.14 = Religione\n"
            "  Col.15 = Patria (luogo di origine)\n"
            "  Col.16 = Professione\n"
            "  Col.19 = Osservazioni\n"
            "\nREGOLE OBBLIGATORIE PER LA TRASCRIZIONE A TABELLA:\n"
            "- Trascrivi OGNI riga come una riga di testo con i valori separati da ' | ',"
            " nell'ordine: N°Casa | N°Fam | Prog | Cognome | Nome | Età | Celibe | Ammogliato | Vedovo"
            " | Nubile | Maritata | Vedova | Religione | Patria | Professione | Osservazioni\n"
            "- Inizia con una riga di intestazione con i nomi delle colonne separati da ' | '.\n"
            "- I segni ditto (\") o 'idem' indicano ripetizione del valore precedente in quella colonna:\n"
            "  TRASCRIVILI come \" senza espanderli.\n"
            "- Le colonne stato civile (7–12) contengono un segno grafico (croce, tratto, X) o sono vuote:\n"
            "  trascrivi '1' se barrata, '' se vuota.\n"
            "- NON saltare righe: anche le righe con soli segni ditto vanno trascritte.\n"
            "- Se una colonna è vuota scrivi uno spazio tra i separatori: | |\n"
            "- Se un valore è illeggibile usa [?].\n"
            "- TRASCRIVI NOMI E COGNOMI ESATTAMENTE come scritti: non correggere, non normalizzare.\n"
            "- DOPPIA PAGINA: se l'immagine mostra due pagine affiancate (foglio aperto),"
            " le colonne di sinistra e di destra formano insieme un'unica riga: trascrivile come"
            " riga continua unita da ' | ', non come due righe separate.\n"
        ),
        "Stato delle Anime / Censimento Parrocchiale": (
            "\nTIPOLOGIA: Stato delle Anime o censimento parrocchiale (TABELLA MULTI-COLONNA).\n"
            "\nSTRUTTURA ATTESA DELLE COLONNE (leggi TUTTE le colonne per ogni riga):\n"
            "  Col.1 = N° d'ordine Casa | Col.2 = N° Famiglia | Col.3 = N° Persona\n"
            "  Col.4 = Cognome | Col.5 = Nome | Col.6 = Età | Col.7 = Stato civile\n"
            "  Col.8 = Religione/Patria | Col.9 = Professione | Col.10 = Osservazioni\n"
            "\nREGOLE OBBLIGATORIE PER LA TRASCRIZIONE A TABELLA:\n"
            "- Trascrivi OGNI riga come una riga di testo con i valori separati da ' | '.\n"
            "  Esempio: 1 | 1 | 1 | Davini | Enrico | 45 | M | Poncarale | Contadino |\n"
            "- Inizia con una riga di intestazione con i nomi delle colonne separati da ' | '.\n"
            "- I segni ditto (\") o 'idem' indicano ripetizione del valore precedente in quella colonna:\n"
            "  TRASCRIVILI come \" senza espanderli.\n"
            "- NON saltare righe: anche le righe con soli segni ditto vanno trascritte.\n"
            "- Se una colonna è vuota scrivi uno spazio tra i separatori: | |\n"
            "- Se un valore è illeggibile usa [?].\n"
            "- NON aggiungere note o commenti: solo la tabella.\n"
            "- DOPPIA PAGINA: se l'immagine mostra due pagine affiancate (foglio aperto),"
            " le colonne di sinistra e di destra formano insieme un'unica riga: trascrivile come"
            " riga continua unita da ' | ', non come due righe separate.\n"
        ),
        "Censimento Storico (Generico)": (
            "\nTIPOLOGIA: Censimento storico (es. censimento statale 1861, 1871, 1881, 1901).\n"
            "- La struttura è tabellare: trascrivi ogni riga con i valori separati da ' | '.\n"
            "- Inizia con una riga di intestazione riportando i nomi delle colonne come indicati nel documento.\n"
            "- Colonne tipiche: N° ordine | Cognome e Nome | Relazione col capofamiglia"
            " | Sesso | Anno di nascita | Stato civile | Professione | Istruzione | Note.\n"
            "- I segni ditto (\") o 'idem' indicano ripetizione del valore soprastante:"
            " TRASCRIVILI come \" senza espanderli.\n"
            "- NON saltare righe vuote o con soli segni ditto.\n"
            "- Se un valore è illeggibile usa [?].\n"
            "- DOPPIA PAGINA: se l'immagine mostra due pagine affiancate (foglio aperto),"
            " le colonne di sinistra e di destra formano insieme un'unica riga: trascrivile come"
            " riga continua unita da ' | ', non come due righe separate.\n"
        ),
        "Documento Notarile": (
            "\nTIPOLOGIA: Documento notarile (contratto, testamento, atto di compravendita, ecc.).\n"
            "- Formula di apertura tipica: 'In Dei nomine amen...' o 'Regnante...'\n"
            "- Presta attenzione ai nomi delle parti contraenti, testimoni, notaio rogante.\n"
            "- Le abbreviazioni dei titoli (Ser, Dominus, fu = quondam) sono frequenti.\n"
            "- Conserva le formule legali anche se apparentemente ridondanti.\n"
            "- Il termine 'fu' equivale al latino 'quondam': trascrivilo letteralmente.\n"
            "- Per cognomi con variante grafica (es. forme latinizzate o dialettali),"
            " aggiungi la variante tra parentesi quadre: es. De Marchi [de Marchis].\n"
        ),
        "Atto in Latino Ecclesiastico": (
            "\nTIPOLOGIA: Atto ecclesiastico in latino (registro parrocchiale pre-napoleonico,"
            " dispensa, atto sinodale, necrologio, ecc.).\n"
            "- Trascrivi il testo in latino esattamente come scritto, senza tradurre.\n"
            "- Le abbreviazioni latine sono frequentissime: sciogli quelle ovvie"
            " tra parentesi angolate < >. Es: Xbris = <Decembris>, 7bris = <Septembris>,"
            " Joannis = <Johannis>, fil. = <filius/filia>, ux. = <uxor>.\n"
            "- Il 'fu' si esprime in latino come 'quondam' (qm, q.m): trascrivilo letteralmente.\n"
            "- Le date usano lo stile romano (Kalendas, Nonas, Idus) o l'anno ab Incarnatione:"
            " trascrivile come appaiono.\n"
            "- Mantieni la struttura del documento: formula di apertura, corpo, sottoscrizioni,"
            " sigilli o croci notarili.\n"
            "- MARGINALIA: trascrivi annotazioni a margine separandole con il tag [MARGINE: ...].\n"
        ),
        "Lettera / Corrispondenza Privata": (
            "\nTIPOLOGIA: Lettera o corrispondenza privata.\n"
            "- Mantieni l'intestazione (luogo, data) e la formula di chiusura.\n"
            "- La grafia privata è spesso corsiva e irregolare: privilegia la lettura letterale.\n"
            "- Non correggere errori ortografici o grammaticali dello scrivente.\n"
        ),
        "Testo a Stampa Antico": (
            "\nTIPOLOGIA: Testo a stampa antico (incunabolo, cinquecentina, ecc.).\n"
            "- Distingui la 's' lunga (ſ) dalla 'f' moderna.\n"
            "- Mantieni le varianti grafiche arcaiche (ex → et, & → e, œ, æ).\n"
            "- Segnala le interruzioni di pagina con [PAGINA NUOVA].\n"
        ),
        "Indice / Registro degli Atti": (
            "\nTIPOLOGIA: Indice o sommario di registro storico (indice degli atti di nascita, matrimonio,"
            " morte, o altro registro civile/parrocchiale).\n"
            "- La struttura è tabellare o a elenco: trascrivi fedelmente ogni riga.\n"
            "- Colonne tipiche: N° atto | Cognome e Nome | Data | Pagina/Foglio | Note.\n"
            "- Usa ' | ' come separatore di colonna; includi una riga di intestazione con i nomi"
            " delle colonne come indicati nel registro.\n"
            "- Trascrivi i cognomi esattamente come scritti, senza normalizzare.\n"
            "- I numeri di atto o di pagina/foglio sono riferimenti critici: trascrivili con"
            " massima precisione.\n"
            "- Se l'indice è su più colonne affiancate (es. due colonne per A–M e N–Z),"
            " trascrivile come due blocchi separati da una riga vuota, ognuno con la propria intestazione.\n"
            '- I segni ditto (") o \'idem\' indicano cognome uguale alla riga precedente:'
            ' TRASCRIVILI come " senza espanderli.\n'
            "- DOPPIA PAGINA: se l'immagine mostra due pagine affiancate (foglio aperto),"
            " le colonne di sinistra e di destra formano insieme un'unica riga: trascrivile come"
            " riga continua unita da ' | ', non come due righe separate.\n"
        ),
        "Documento Generico / Non Classificato": (
            "\nTIPOLOGIA: Documento non classificato (nessuna tipologia predefinita applicabile).\n"
            "- Trascrivi il testo esattamente come appare, preservando la struttura visiva originale.\n"
            "- Se il documento ha colonne o tabelle, usa ' | ' come separatore di colonna.\n"
            "- Se il documento ha sezioni distinte (titoli, paragrafi, firme), separale con una riga vuota.\n"
            "- Segnala con [MARGINE: ...] qualsiasi annotazione a margine o fuori dal corpo principale.\n"
        ),
    }

    specific = type_specific.get(doc_type, type_specific["Documento Generico / Non Classificato"])

    prompt = base + specific

    if example_text.strip():
        prompt += (
            "\n\n--- TRASCRIZIONE DI RIFERIMENTO ---\n"
            "La seguente trascrizione è di una pagina dello stesso documento.\n"
            "Usala per imparare la calligrafia e il vocabolario specifico dello scrivano:\n\n"
            f"{example_text.strip()}\n"
            "--- FINE RIFERIMENTO ---\n"
        )

    if user_instructions.strip():
        prompt += f"\n\n--- ISTRUZIONI AGGIUNTIVE ---\n{user_instructions.strip()}\n"

    prompt += "\n\nINIZIA ORA LA TRASCRIZIONE:"
    return prompt
