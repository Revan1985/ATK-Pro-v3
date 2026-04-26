"""
Prompt di base per la Traduzione OCR, divisi per tipologia documentale.
Ogni tipo fornisce il contesto storico-linguistico necessario all'IA per tradurre correttamente.
"""


def get_available_types():
    return [
        "Documento Burocratico Napoleonico (Italiano Arcaico)",
        "Atto Ecclesiastico in Latino",
        "Corrispondenza Privata Ottocentesca",
        "Testo in Dialetto Locale",
        "Documento Legale / Notarile in Volgare",
        "Testo in Latino Ecclesiastico Medievale",
        "Traduzione Libera (Nessun Contesto Specifico)",
    ]


def compose_translation_prompt(doc_type, source_text, target_lang, context_info=""):
    """
    Costruisce il prompt per la traduzione storico-paleografica.
    """
    base = (
        f"Sei uno specialista accademico di storia, paleografia e linguistica storica italiana.\n"
        f"Traduci il seguente documento storico nella lingua target: '{target_lang}'.\n\n"
        "REGOLE:\n"
        "1. Mantieni la struttura del testo originale (a capo, paragrafi, numerazione degli atti).\n"
        "2. Non omettere nessuna parte del testo, anche le formule ripetitive.\n"
        "3. Conserva i nomi propri di persona e di luogo nella forma originale (non tradurre 'Giovanni' in 'John').\n"
        "4. Segnala i passaggi di lettura incerta con [?] nel testo tradotto.\n"
        "5. Non aggiungere note a piè di pagina o commenti: solo la traduzione.\n"
    )

    type_specific = {
        "Documento Burocratico Napoleonico (Italiano Arcaico)": (
            "\nCONTESTO: Documento ufficiale del periodo napoleonico o della Restaurazione (1800-1860 ca.).\n"
            "- La lingua è italiano burocratico arcaico con influenze francesi e formule latine.\n"
            "- Termini chiave: 'quondam' (fu, defunto padre), 'fu' (stesso significato),\n"
            "  'domiciliato in' (residente a), 'profisione' (professione, grafia arcaica),\n"
            "  'Ufficiale dello Stato Civile' (funzionario anagrafico).\n"
            "- Mantieni le date in cifre anche se nel testo originale sono in lettere.\n"
        ),
        "Atto Ecclesiastico in Latino": (
            "\nCONTESTO: Documento ecclesiastico in latino (registri parrocchiali, atti di curia, ecc.).\n"
            "- Il latino usato è il latino ecclesiastico medievale o moderno, non il classico.\n"
            "- Formule ricorrenti: 'In nomine Domini', 'ego infrascriptus', 'testibus vocatis',\n"
            "  'die/mensis/anno Domini', 'renuntians exceptioni'.\n"
            "- Traduci sciogliendo le abbreviazioni tipiche (d.nus = dominus, s.tus = sanctus, ecc.).\n"
            "- I nomi propri latini vanno resi nella forma italiana corrente (Ioannes → Giovanni).\n"
        ),
        "Corrispondenza Privata Ottocentesca": (
            "\nCONTESTO: Lettera o corrispondenza privata del XIX secolo.\n"
            "- La lingua è italiano letterario o semi-colto dell'Ottocento, talvolta con toscanismi.\n"
            "- Conserva il tono e lo stile dell'autore (formale, familiare, affettuoso).\n"
            "- I riferimenti culturali, geografici e personali vanno mantenuti inalterati.\n"
        ),
        "Testo in Dialetto Locale": (
            "\nCONTESTO: Testo parzialmente o interamente in dialetto italiano locale.\n"
            "- Traduci verso l'italiano standard moderno, poi nella lingua target.\n"
            "- Segnala con [dialetto: X] i termini dialettali particolarmente opachi.\n"
            "- Non forzare una traduzione per termini dialettali senza equivalente certo: usa [?].\n"
        ),
        "Documento Legale / Notarile in Volgare": (
            "\nCONTESTO: Documento notarile o legale in italiano volgare (XIII-XVIII secolo).\n"
            "- La lingua può essere il volgare toscano antico, il veneziano, il lombardo, ecc.\n"
            "- Formule tipiche: 'costituito personalmente', 'per spontanea volontà', 'rogato da me notaio',\n"
            "  'pro anima sua', 'lascio e lego'.\n"
            "- Mantieni la struttura tripartita degli atti: protocollo, dispositivo, escatocollo.\n"
        ),
        "Testo in Latino Ecclesiastico Medievale": (
            "\nCONTESTO: Documento in latino medievale (secoli VIII-XV), produzione ecclesiastica o notarile.\n"
            "- Il latino è medievale con grafie non classiche (e.g. 'nichil' per 'nihil', 'aliquid' alternato a 'aliquit').\n"
            "- Le abbreviazioni sono numerose: scioglile esplicitamente nella traduzione.\n"
            "- Formule diplomatiche standard: 'In nomine Sancte et Individue Trinitatis', 'Actum est hoc'.\n"
        ),
    }

    specific = type_specific.get(doc_type, (
        "\nCONTESTO: Traduzione generica. Applica il tuo giudizio storico-linguistico.\n"
    ))

    prompt = base + specific

    if context_info.strip():
        prompt += (
            "\n\n--- GLOSSARIO E CONTESTO SPECIFICO FORNITO DALL'UTENTE ---\n"
            f"{context_info.strip()}\n"
            "--- FINE GLOSSARIO ---\n"
        )

    prompt += f"\n\n--- TESTO DA TRADURRE ---\n{source_text}\n--- FINE TESTO ---"
    return prompt
