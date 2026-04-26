"""
Prompt di base per l'OCR Avanzato, divisi per tipologia documentale.
Ogni tipo fornisce linee guida paleografiche specifiche all'IA.
"""


def get_available_types():
    return [
        "Atto di Stato Civile (Nascita / Battesimo)",
        "Atto di Stato Civile (Matrimonio)",
        "Atto di Stato Civile (Morte / Sepoltura)",
        "Stato delle Anime / Censimento Parrocchiale",
        "Documento Notarile",
        "Lettera / Corrispondenza Privata",
        "Testo a Stampa Antico",
        "Manoscritto Generico / Altro",
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
            "- Presta attenzione ai campi: nome del neonato, genitori (padre e madre con cognome da nubile),\n"
            "  data e luogo di nascita, testimoni, ufficiale o parroco.\n"
            "- I nomi di persona sono spesso abbreviati (Gio. = Giovanni, Batta. = Battista, Fran.co = Francesco).\n"
            "- Le date sono in lettere: 'il giorno tre maggio milleottocentosei'.\n"
        ),
        "Atto di Stato Civile (Matrimonio)": (
            "\nTIPOLOGIA: Atto di matrimonio (XIX secolo, registro civile o parrocchiale).\n"
            "- Campi chiave: sposo e sposa (nome, cognome, età, professione, domicilio),\n"
            "  padri e madri di entrambi, testimoni.\n"
            "- Frequenti formule latine come 'in facie Ecclesiae' nei registri parrocchiali.\n"
        ),
        "Atto di Stato Civile (Morte / Sepoltura)": (
            "\nTIPOLOGIA: Atto di morte o sepoltura (XIX secolo).\n"
            "- Campi chiave: nome e cognome del defunto, età, causa di morte (se indicata),\n"
            "  data e luogo del decesso, dichiaranti, sepoltura.\n"
            "- Presta attenzione ai termini medici arcaici per le cause di morte.\n"
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
        ),
        "Documento Notarile": (
            "\nTIPOLOGIA: Documento notarile (contratto, testamento, atto di compravendita, ecc.).\n"
            "- Formula di apertura tipica: 'In Dei nomine amen...' o 'Regnante...'\n"
            "- Presta attenzione ai nomi delle parti contraenti, testimoni, notaio rogante.\n"
            "- Le abbreviazioni dei titoli (Ser, Dominus, fu = quondam) sono frequenti.\n"
            "- Conserva le formule legali anche se apparentemente ridondanti.\n"
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
    }

    specific = type_specific.get(doc_type, (
        "\nTIPOLOGIA: Manoscritto generico. Applica le regole generali di trascrizione.\n"
    ))

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
