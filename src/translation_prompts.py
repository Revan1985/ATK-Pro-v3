"""
Prompt per la traduzione di documenti storici italiani, strutturati per famiglie di tipologie.
Allineato alle 55 tipologie di BUILTIN_TYPES in document_type_manager.py.
"""

# ─────────────────────────────────────────────────────────────────────────────
# CLASSIFICATORI DI FAMIGLIA
# ─────────────────────────────────────────────────────────────────────────────

def _is_stato_civile(dt: str) -> bool:
    kw = ("scn", "scr", "sci", "stato civile", "atto di nascita", "atto di matrimonio",
          "atto di morte", "nascita / battesimo", "processetto", "pubblicazioni di matrimonio")
    d = dt.lower()
    return any(k in d for k in kw)

def _is_parrocchiale(dt: str) -> bool:
    kw = ("parrocchiale", "battesimi", "matrimoni", "morti / sepolture", "cresimati",
          "esposti", "nati illegittimi")
    d = dt.lower()
    return any(k in d for k in kw)

def _is_censimento(dt: str) -> bool:
    kw = ("stati delle anime", "censimento", "anagrafe", "foglio di famiglia",
          "stato di famiglia", "stato delle anime", "foglio di famiglia anagrafe")
    d = dt.lower()
    return any(k in d for k in kw)

def _is_catasto(dt: str) -> bool:
    kw = ("catasto", "rivele", "numerazione dei fuochi", "onciario", "murattiano", "gregoriano")
    d = dt.lower()
    return any(k in d for k in kw)

def _is_militare(dt: str) -> bool:
    kw = ("matricola", "leva militare", "foglio matricolare", "ruolo di matricola")
    d = dt.lower()
    return any(k in d for k in kw)

def _is_notarile(dt: str) -> bool:
    kw = ("notarile", "testamento", "latino ecclesiastico", "latino", "processetto")
    d = dt.lower()
    return any(k in d for k in kw) and not _is_stato_civile(dt) and not _is_parrocchiale(dt)

def _is_emigrazione(dt: str) -> bool:
    kw = ("passaporto", "espatrio", "consolari", "ospedalieri", "defunti ospedalieri")
    d = dt.lower()
    return any(k in d for k in kw)

def _is_corrispondenza(dt: str) -> bool:
    kw = ("lettera", "corrispondenza", "stampa antico", "testo a stampa")
    d = dt.lower()
    return any(k in d for k in kw)

def _is_indice(dt: str) -> bool:
    kw = ("indice", "protocollo notarile", "registro degli atti")
    d = dt.lower()
    return any(k in d for k in kw)

def _is_matrimonio_religioso(dt: str) -> bool:
    return "matrimonio religioso" in dt.lower()


# ─────────────────────────────────────────────────────────────────────────────
# BLOCCO BASE (comune a tutte le famiglie)
# ─────────────────────────────────────────────────────────────────────────────

_BASE = (
    "Sei uno specialista accademico di storia, paleografia e linguistica storica italiana.\n"
    "Traduci il seguente documento storico nella lingua target: '{target_lang}'.\n\n"
    "REGOLE GENERALI:\n"
    "1. Mantieni la struttura del testo originale (a capo, paragrafi, numerazione degli atti).\n"
    "2. Non omettere alcuna parte del testo, neppure le formule ripetitive.\n"
    "3. Conserva i nomi propri di persona e di luogo nella forma originale (non tradurre 'Giovanni' in 'John').\n"
    "4. Segnala i passaggi di lettura incerta con [?] nel testo tradotto.\n"
    "5. Non aggiungere note a piè di pagina o commenti: restituisci solo la traduzione.\n"
)


# ─────────────────────────────────────────────────────────────────────────────
# FAMIGLIE DI PROMPT
# ─────────────────────────────────────────────────────────────────────────────

def _prompt_stato_civile(dt: str, target_lang: str) -> str:
    d = dt.lower()
    intro = _BASE.format(target_lang=target_lang)

    if "scn" in d or "napoleonic" in d:
        ctx = (
            "\nCONTESTO — Stato Civile Napoleonico (1806-1815):\n"
            "- Lingua italiana burocratica arcaica con forti influenze francesi.\n"
            "- Formule ricorrenti: 'costituito avanti a noi', 'Ufficiale dello Stato Civile',\n"
            "  'del quale abbiamo preso atto', 'dichiarante', 'testimoni sottoscritti'.\n"
            "- 'quondam' / 'fu' indicano il genitore defunto; mantieni 'fu' nella traduzione.\n"
            "- Le date sono spesso in lettere (es. «il tre di maggio»): trascrivi in cifre nella traduzione.\n"
        )
    elif "toscana" in d:
        ctx = (
            "\nCONTESTO — Stato Civile della Restaurazione / Granducato di Toscana (1817-1865):\n"
            "- Italiano burocratico toscano con qualche residuo napoleonico.\n"
            "- Formula tipica: 'comparve avanti di noi', 'Cancelliere dello Stato Civile'.\n"
            "- 'quondam' alternato a 'del fu' per indicare genitore defunto.\n"
            "- Il Granducato usava il sistema metrico decimale dal 1782: mantieni le unità originali.\n"
        )
    elif "due sicilie" in d:
        ctx = (
            "\nCONTESTO — Stato Civile del Regno delle Due Sicilie (1816-1865):\n"
            "- Italiano burocratico meridionale con influenze borboniche.\n"
            "- Formule tipiche: 'avanti di noi Sindaco, Uffiziale dello Stato Civile',\n"
            "  'nella casa comunale', 'regnicolo' (suddito del regno).\n"
            "- La professione è spesso espressa in dialetto napoletano/siciliano: segnalalo con [dial.].\n"
        )
    elif "piemonte" in d:
        ctx = (
            "\nCONTESTO — Stato Civile del Regno di Sardegna / Piemonte (1837-1865):\n"
            "- Italiano burocratico piemontese con influenze francesi (il francese era lingua ufficiale fino al 1847).\n"
            "- Possibili commistioni francese/italiano: traduci entrambe le parti.\n"
            "- Formule tipiche: 'avanti di noi Sindaco', 'borgata di', 'mandamento di'.\n"
        )
    elif "veneto" in d:
        ctx = (
            "\nCONTESTO — Stato Civile Lombardo-Veneto / Veneto (1816-1866):\n"
            "- Italiano burocratico con influenze austriache; documenti talvolta anche in tedesco.\n"
            "- Se presenti sezioni in tedesco, traducile separatamente indicando [DE].\n"
            "- Formule tipiche: 'Imperial Regio Comune di', 'I.R. Ufficio dello Stato Civile'.\n"
        )
    elif "sci" in d or "dal 1866" in d:
        ctx = (
            "\nCONTESTO — Stato Civile Italiano Unificato (dal 1866):\n"
            "- Italiano burocratico post-unitario, standardizzato su base napoletana.\n"
            "- Formule fisse dettate dal Codice Civile del 1865; la struttura è molto regolare.\n"
            "- 'ufficiale dello stato civile', 'comparso davanti a noi', 'nel comune di'.\n"
        )
    elif "processetto" in d:
        ctx = (
            "\nCONTESTO — Processetto Matrimoniale / Allegati:\n"
            "- Fascicolo istruttorio che precede il matrimonio; include estratti di battesimo,\n"
            "  estratti di morte, atti di notorietà, licenze parrocchiali.\n"
            "- Lingua mista: italiano burocratico e formule latine ecclesiastiche.\n"
            "- Documenti di provenienza diversa possono avere stili differenti: mantienili distinti.\n"
        )
    elif "pubblicazioni" in d:
        ctx = (
            "\nCONTESTO — Pubblicazioni di Matrimonio (registro dei bandi):\n"
            "- Registro dei bandi matrimoniali pubblicati in chiesa o in comune.\n"
            "- Testo breve e formulaico; l'interesse genealogico è nei nomi e nelle date.\n"
            "- Mantieni l'ordine dei bandi così come appaiono nel registro.\n"
        )
    else:
        ctx = (
            "\nCONTESTO — Atto di Stato Civile (generico):\n"
            "- Documento ufficiale di stato civile italiano (nascita, matrimonio, morte).\n"
            "- Lingua italiana burocratica arcaica; 'quondam'/'fu' = genitore defunto.\n"
            "- Mantieni le formule di rito nella traduzione senza semplificarle.\n"
        )
    return intro + ctx


def _prompt_parrocchiale(dt: str, target_lang: str) -> str:
    d = dt.lower()
    intro = _BASE.format(target_lang=target_lang)

    if "esposti" in d or "illegittimi" in d:
        ctx = (
            "\nCONTESTO — Registro degli Esposti / Nati Illegittimi:\n"
            "- Registro tenuto dall'orfanotrofio, brefotrofio o parrocchia.\n"
            "- Lingua mista italiano/latino; i nomi attribuiti agli esposti erano spesso fittizi.\n"
            "- Formule tipiche: 'fu trovato/a', 'di padre incognito', 'battezzato/a sotto condizione'.\n"
            "- Mantieni le annotazioni marginali (adozione, morte, professione futura) se presenti.\n"
        )
    elif "battesimi" in d or "battesimo" in d or "nascita" in d:
        ctx = (
            "\nCONTESTO — Registro Parrocchiale dei Battesimi (secc. XVI-XIX):\n"
            "- Lingua latina ecclesiastica, con formule standardizzate post-Concilio di Trento (1563).\n"
            "- Formule tipiche: 'ego infrascriptus baptizavi', 'fuerunt patrini', 'die/mense/anno Domini'.\n"
            "- I nomi latini vanno resi nella forma italiana corrente (Ioannes→Giovanni, Petrus→Pietro).\n"
            "- Sciogliere le abbreviazioni: d.no = domino, q.m = quondam, f. = filius/filia.\n"
        )
    elif "matrimoni" in d or "matrimonio" in d:
        ctx = (
            "\nCONTESTO — Registro Parrocchiale dei Matrimoni (secc. XVI-XIX):\n"
            "- Lingua latina ecclesiastica post-Tridentina.\n"
            "- Formule tipiche: 'in facie Ecclesiae', 'nullis detecto impedimento',\n"
            "  'testes fuerunt', 'copulavi in matrimonium'.\n"
            "- I nomi vanno resi nella forma italiana; conserva i cognomi nella forma originale.\n"
        )
    elif "morti" in d or "sepolture" in d or "morte" in d:
        ctx = (
            "\nCONTESTO — Registro Parrocchiale dei Morti / Sepolture (secc. XVI-XIX):\n"
            "- Lingua latina ecclesiastica; include spesso i sacramenti ricevuti.\n"
            "- Formule tipiche: 'obiit', 'sepultus/a in', 'recepit sacramenta', 'aetatis annorum'.\n"
            "- Mantieni i riferimenti topografici (cappella, sepoltura, tomba di famiglia).\n"
        )
    elif "cresimati" in d:
        ctx = (
            "\nCONTESTO — Registro Parrocchiale dei Cresimati (secc. XVI-XIX):\n"
            "- Lingua latina; contiene nome, cognome, padrino/madrina, vescovo officiante.\n"
            "- Formule tipiche: 'confirmatus/a a', 'patrinus/matrina fuit', 'die visitationis'.\n"
        )
    else:
        ctx = (
            "\nCONTESTO — Registro Parrocchiale (generico, secc. XVI-XIX):\n"
            "- Lingua latina ecclesiastica post-Tridentina.\n"
            "- Sciogliere abbreviazioni e rendere i nomi latini in forma italiana moderna.\n"
        )
    return intro + ctx


def _prompt_censimento(dt: str, target_lang: str) -> str:
    d = dt.lower()
    intro = _BASE.format(target_lang=target_lang)

    if "granducato di toscana" in d or "stati delle anime" in d:
        ctx = (
            "\nCONTESTO — Stati delle Anime del Granducato di Toscana (secc. XVII-XIX):\n"
            "- Registro parrocchiale per comunità; struttura tabulare con colonne per nucleo familiare.\n"
            "- Lingua italiana arcaica con formule toscane; l'età è spesso espressa in anni e mesi.\n"
            "- Le colonne indicano: numero di fuoco, cognome/nome, parentela, età, professione, note.\n"
            "- Mantieni la struttura tabulare nella traduzione (righe → famiglie).\n"
        )
    elif "lombardo-veneto" in d or "anagrafe" in d:
        ctx = (
            "\nCONTESTO — Anagrafe / Censimento Lombardo-Veneto (sec. XIX):\n"
            "- Registro amministrativo imperiale austriaco; lingua italiana o tedesca.\n"
            "- Se presenti sezioni in tedesco, traducile indicando [DE] prima della traduzione.\n"
            "- Struttura tabulare: colonne per nome, cognome, età, professione, relazione familiare.\n"
        )
    elif "foglio di famiglia" in d or "foglio di famiglia anagrafe" in d:
        ctx = (
            "\nCONTESTO — Foglio di Famiglia Anagrafe Comunale (post-1864):\n"
            "- Documento amministrativo post-unitario; italiano burocratico standardizzato.\n"
            "- Contiene: intestatario, componenti, date nascita/matrimonio/morte, professioni, provenienza.\n"
            "- Mantieni la struttura del modulo; segnala le cancellature con [cancellato].\n"
        )
    elif "stato di famiglia" in d:
        ctx = (
            "\nCONTESTO — Stato di Famiglia / Atto di Notorietà:\n"
            "- Documento ufficiale che elenca i componenti di una famiglia in una data.\n"
            "- Lingua italiana burocratica; rilasciato dal comune o dall'ufficio di stato civile.\n"
        )
    else:
        ctx = (
            "\nCONTESTO — Censimento Storico (generico):\n"
            "- Documento di rilevazione demografica; struttura tabulare per nuclei familiari.\n"
            "- Mantieni la struttura originale; interpreta le abbreviazioni di colonna nel contesto.\n"
        )
    return intro + ctx


def _prompt_catasto(dt: str, target_lang: str) -> str:
    d = dt.lower()
    intro = _BASE.format(target_lang=target_lang)

    if "onciario" in d:
        ctx = (
            "\nCONTESTO — Catasto Onciario (Due Sicilie, sec. XVIII):\n"
            "- Registro fiscale borbonico compilato in italiano/napoletano; unità fiscale = oncia.\n"
            "- Struttura: 'numero di fuoco' → intestatario → componenti → beni immobili/mobili → imposte.\n"
            "- Termini chiave: 'fuoco' (nucleo familiare), 'once' (unità monetaria fiscale),\n"
            "  'possidente' (proprietario terriero), 'massaro' (contadino affittuario).\n"
            "- Mantieni i termini fiscali originali con la traduzione in parentesi [trad.].\n"
        )
    elif "murattiano" in d:
        ctx = (
            "\nCONTESTO — Catasto Murattiano (Due Sicilie, 1808-1815):\n"
            "- Catasto geometrico-particellare di tipo napoleonico; lingua italiana con influenze francesi.\n"
            "- Struttura: particella, confini (quattro lati), qualità colturale, superficie, rendita.\n"
            "- Termini chiave: 'particella', 'vani' (stanze), 'palmi quadrati' (unità di misura).\n"
        )
    elif "gregoriano" in d:
        ctx = (
            "\nCONTESTO — Catasto Gregoriano (Stato Pontificio, 1816-1835):\n"
            "- Catasto pontificio geometrico; lingua italiana burocratica con formule latine.\n"
            "- Struttura: intestatario → descrizione particellare → confini → uso del suolo → valore.\n"
            "- Unità di misura: 'rubbia', 'scorzo', 'quarto', 'tavola'.\n"
        )
    elif "rivele" in d or "numerazione dei fuochi" in d:
        ctx = (
            "\nCONTESTO — Rivele / Numerazione dei Fuochi (Due Sicilie, secc. XVI-XVII):\n"
            "- Dichiarazione fiscale presentata dal capofamiglia; lingua italiana arcaica/napoletana.\n"
            "- Struttura: dichiarante → membri del fuoco → beni dichiarati → debiti/crediti.\n"
            "- 'Rivela' = autodichiarazione fiscale; 'fuoco' = unità familiare tassabile.\n"
        )
    else:
        ctx = (
            "\nCONTESTO — Catasto Storico (generico):\n"
            "- Registro fiscale-patrimoniale; struttura tabulare per proprietari e beni.\n"
            "- Mantieni le unità di misura e fiscali originali con traduzione in parentesi.\n"
        )
    return intro + ctx


def _prompt_militare(dt: str, target_lang: str) -> str:
    d = dt.lower()
    intro = _BASE.format(target_lang=target_lang)

    if "foglio matricolare" in d:
        ctx = (
            "\nCONTESTO — Foglio Matricolare (scheda individuale, 1865-1940):\n"
            "- Documento personale militare dell'Esercito Italiano; lingua italiana burocratica.\n"
            "- Struttura: dati anagrafici, connotati fisici, istruzione, storia militare (arruolamento,\n"
            "  gradi, campagne, decorazioni, congedo o morte in servizio).\n"
            "- Abbreviazioni frequenti: S.Ten. (Sottotenente), Ten. (Tenente), Cap. (Capitano),\n"
            "  f.f. (facente funzione), b.e. (buona condotta), R.D. (Regio Decreto).\n"
            "- Mantieni le sigle militari originali con la traduzione in parentesi alla prima occorrenza.\n"
        )
    else:  # Ruolo di Matricola / Leva Militare
        ctx = (
            "\nCONTESTO — Ruolo di Matricola / Registro di Leva Militare (1865-1940):\n"
            "- Registro di leva per comune o mandamento; lingua italiana burocratica.\n"
            "- Struttura tabulare: numero di matricola, cognome/nome, dati anagrafici,\n"
            "  connotati fisici, distretto militare, decisione della commissione (abile, riformato, ecc.).\n"
            "- Mantieni i codici di valutazione e i giudizi della commissione nella forma originale.\n"
        )
    return intro + ctx


def _prompt_notarile(dt: str, target_lang: str) -> str:
    d = dt.lower()
    intro = _BASE.format(target_lang=target_lang)

    if "testamento" in d:
        ctx = (
            "\nCONTESTO — Testamento (atto notarile specifico):\n"
            "- Documento legale; struttura: intestazione → identità testatore → lasciti → firma notaio.\n"
            "- Lingua italiana o latina (per testamenti più antichi) con formule giuridiche tipiche.\n"
            "- Formule chiave: 'lascio e lego', 'istituisco erede universale', 'pro anima mea',\n"
            "  'legato pio', 'esecutori testamentari'.\n"
            "- Mantieni la struttura dei lasciti; segnala gli importi monetari con l'unità originale.\n"
        )
    elif "latino" in d:
        ctx = (
            "\nCONTESTO — Atto in Latino Ecclesiastico / Notarile:\n"
            "- Latino medievale o moderno con grafie non classiche (nichil, aliquit, thibi, ecc.).\n"
            "- Sciogliere le abbreviazioni esplicitamente; i nomi propri latini → forma italiana.\n"
            "- Formule diplomatiche tipiche: 'In nomine Domini', 'ego infrascriptus notarius',\n"
            "  'renuntians exceptioni', 'promittens sub hypotheca omnium bonorum'.\n"
            "- Mantieni la struttura tripartita: protocollo, dispositivo, escatocollo.\n"
        )
    elif "protocollo notarile" in d or "indice" in d:
        ctx = (
            "\nCONTESTO — Protocollo Notarile / Indice degli Atti:\n"
            "- Registro di repertorio notarile; struttura tabulare con numero d'atto, data, parti, oggetto.\n"
            "- Lingua italiana burocratica arcaica; i riferimenti agli atti usano formule standardizzate.\n"
            "- Non tradurre le qualifiche notarili (notaio, procuratore, tutore); mantienile in originale.\n"
        )
    else:  # Documento Notarile generico
        ctx = (
            "\nCONTESTO — Documento Notarile (generico, secc. XIII-XIX):\n"
            "- Lingua italiana (volgare o burocratica) o latina, a seconda del periodo.\n"
            "- Formule tipiche: 'costituito personalmente', 'per spontanea volontà', 'rogato da me notaio',\n"
            "  'ricevuto per fede', 'stipulato nell'anno del Signore'.\n"
            "- Mantieni la struttura tripartita degli atti: protocollo, dispositivo, escatocollo.\n"
        )
    return intro + ctx


def _prompt_emigrazione(dt: str, target_lang: str) -> str:
    d = dt.lower()
    intro = _BASE.format(target_lang=target_lang)

    if "passaporto" in d or "espatrio" in d:
        ctx = (
            "\nCONTESTO — Passaporto / Permesso di Espatrio (sec. XIX-XX):\n"
            "- Documento amministrativo bilingue (italiano + lingua del paese di destinazione).\n"
            "- Struttura: dati anagrafici, connotati fisici (altezza, colore occhi/capelli),\n"
            "  motivo del viaggio, destinazione, validità.\n"
            "- Tradurre solo la parte in italiano; segnala le sezioni in altra lingua con [lingua].\n"
        )
    elif "consolari" in d:
        ctx = (
            "\nCONTESTO — Atti Consolari Italiani all'Estero:\n"
            "- Documento prodotto dal consolato italiano in paese straniero.\n"
            "- Lingua italiana burocratica; talvolta con note a margine in lingua locale.\n"
            "- Può riguardare: nascite, matrimoni, morti, cittadinanza, leva militare all'estero.\n"
            "- Mantieni i riferimenti normativi italiani (R.D., Codice Civile, art.) nella forma originale.\n"
        )
    elif "ospedalieri" in d or "defunti ospedale" in d:
        ctx = (
            "\nCONTESTO — Registro dei Defunti Ospedalieri:\n"
            "- Registro tenuto dall'ospedale; lingua italiana burocratica.\n"
            "- Contiene: nome, età, provenienza, malattia/causa di morte, data ricovero e decesso.\n"
            "- I termini medici arcaici vanno tradotti con il termine moderno in parentesi [mod.].\n"
        )
    else:
        ctx = (
            "\nCONTESTO — Documento di emigrazione / estero (generico):\n"
            "- Documento amministrativo relativo a mobilità geografica o attività consolare.\n"
        )
    return intro + ctx


def _prompt_corrispondenza(dt: str, target_lang: str) -> str:
    d = dt.lower()
    intro = _BASE.format(target_lang=target_lang)

    if "lettera" in d or "corrispondenza" in d:
        ctx = (
            "\nCONTESTO — Lettera / Corrispondenza Privata (sec. XIX-XX):\n"
            "- Lingua italiana letteraria o semi-colta; tono variabile (formale, familiare, affettuoso).\n"
            "- Conserva il tono e lo stile dell'autore; non standardizzare le espressioni dialettali.\n"
            "- I riferimenti culturali, geografici e personali vanno mantenuti inalterati.\n"
            "- Le formule di apertura ('Carissimo/a', 'Egregio Signore') e chiusura ('Devotissimo') vanno tradotte.\n"
        )
    else:  # Testo a stampa antico
        ctx = (
            "\nCONTESTO — Testo a Stampa Antico (sec. XV-XIX):\n"
            "- Lingua italiana arcaica (toscano letterario, volgare illustre) o latina.\n"
            "- Grafia pre-riforma: j per i, u per v, nessi latinizzanti (ph, th, ch), accenti anomali.\n"
            "- Non modernizzare la grafia nella traduzione: rendi il significato, non la forma.\n"
            "- I titoli, le dediche e le note tipografiche sono parte del documento: traducile tutte.\n"
        )
    return intro + ctx


def _prompt_matrimonio_religioso(dt: str, target_lang: str) -> str:
    intro = _BASE.format(target_lang=target_lang)
    ctx = (
        "\nCONTESTO — Matrimonio Religioso post-Concordato (1929+):\n"
        "- Documento della Chiesa Cattolica con effetti civili ai sensi del Concordato del 1929.\n"
        "- Lingua italiana; struttura mista ecclesiastica e burocratica.\n"
        "- Include: dati sposi, dichiarazione di libertà di stato, eventuali dispense, firme.\n"
        "- Mantieni le formule sacramentali nella forma originale e aggiungine la traduzione.\n"
    )
    return intro + ctx


def _prompt_generico(dt: str, target_lang: str) -> str:
    intro = _BASE.format(target_lang=target_lang)
    ctx = (
        "\nCONTESTO — Documento generico / non classificato:\n"
        "- Applica il tuo giudizio storico-linguistico in base al contenuto.\n"
        "- Se rilevi una tipologia specifica (atto notarile, lettera, ecc.) adatta lo stile di traduzione.\n"
    )
    return intro + ctx


# ─────────────────────────────────────────────────────────────────────────────
# BLOCCO GLOSSARIO E TESTO DA TRADURRE
# ─────────────────────────────────────────────────────────────────────────────

def _append_text(base_prompt: str, source_text: str, context_info: str) -> str:
    if context_info.strip():
        base_prompt += (
            "\n\n--- GLOSSARIO E CONTESTO SPECIFICO FORNITO DALL'UTENTE ---\n"
            f"{context_info.strip()}\n"
            "--- FINE GLOSSARIO ---\n"
        )
    base_prompt += f"\n\n--- TESTO DA TRADURRE ---\n{source_text}\n--- FINE TESTO ---"
    return base_prompt


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def compose_translation_prompt(doc_type: str, source_text: str, target_lang: str,
                               context_info: str = "") -> str:
    """
    Costruisce il prompt di traduzione per il doc_type specificato.
    Allineato alle 55 tipologie di BUILTIN_TYPES.

    Args:
        doc_type:     Label esatta della tipologia (dalla lista BUILTIN_TYPES).
        source_text:  Testo OCR da tradurre.
        target_lang:  Lingua di destinazione (es. 'italiano moderno', 'inglese', 'spagnolo').
        context_info: Glossario o contesto aggiuntivo fornito dall'utente.
    Returns:
        Prompt completo pronto per l'invio all'IA.
    """
    dt = doc_type.strip()

    if _is_stato_civile(dt):
        base = _prompt_stato_civile(dt, target_lang)
    elif _is_parrocchiale(dt):
        base = _prompt_parrocchiale(dt, target_lang)
    elif _is_censimento(dt):
        base = _prompt_censimento(dt, target_lang)
    elif _is_catasto(dt):
        base = _prompt_catasto(dt, target_lang)
    elif _is_militare(dt):
        base = _prompt_militare(dt, target_lang)
    elif _is_matrimonio_religioso(dt):
        base = _prompt_matrimonio_religioso(dt, target_lang)
    elif _is_emigrazione(dt):
        base = _prompt_emigrazione(dt, target_lang)
    elif _is_corrispondenza(dt):
        base = _prompt_corrispondenza(dt, target_lang)
    elif _is_notarile(dt):
        base = _prompt_notarile(dt, target_lang)
    elif _is_indice(dt):
        base = _prompt_notarile(dt, target_lang)   # riusa famiglia notarile
    else:
        base = _prompt_generico(dt, target_lang)

    return _append_text(base, source_text, context_info)

