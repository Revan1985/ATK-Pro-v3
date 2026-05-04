"""
Prompt GEDCOM per estrazione genealogica, divisi per famiglia di tipologia documentale.
Ogni tipologia o famiglia di tipologie fornisce istruzioni JSON-specifiche all'IA.
"""

# ─────────────────────────────────────────────────────────────────────────────
# RILEVAMENTO FAMIGLIE
# ─────────────────────────────────────────────────────────────────────────────

def _is_nascita(dt):
    return any(k in dt for k in ("Nascita", "Battesim", "Esposti", "Illegittim"))

def _is_matrimonio(dt):
    return any(k in dt for k in ("Matrimoni", "Matrimoniali", "Processetto", "Pubblicazioni di Matrimonio"))

def _is_morte(dt):
    return any(k in dt for k in ("Morte", "Sepoltur", "Ospedalieri"))

def _is_censimento(dt):
    return any(k in dt for k in (
        "Granducato di Toscana", "Censimento Storico",
        "Anagrafe / Censimento", "Stato di Famiglia",
        "Foglio di Famiglia", "Stato delle Anime",
    ))

def _is_catasto(dt):
    return any(k in dt for k in ("Catasto", "Rivele", "Fuochi"))

def _is_militare(dt):
    return any(k in dt for k in ("Matricola", "Matricolare", "Leva"))

def _is_altro(dt):
    return any(k in dt for k in ("Passaporto", "Consolari", "Espatrio"))

def _is_cresima(dt):
    return any(k in dt for k in ("Cresim", "Conferm", "Crism", "Cresimati", "Confermati"))

def _is_comunione(dt):
    return any(k in dt for k in ("Prima Comunione", "Comunione", "Comunicati"))

def _is_adozione(dt):
    return any(k in dt for k in ("Adozione", "Adottato", "Adozioni"))

def _is_ordinazione(dt):
    return any(k in dt for k in ("Ordinazione", "Sacerdozio", "Chierici", "Ordinati"))

# ─────────────────────────────────────────────────────────────────────────────
# PROMPT BASE COMUNE
# ─────────────────────────────────────────────────────────────────────────────

_BASE = (
    "Sei un esperto Paleografo e Genealogista specializzato in documenti storici italiani.\n"
    "Analizza il documento ed estrai i dati genealogici in formato JSON.\n"
    "REGOLE DI OUTPUT:\n"
    "- Restituisci ESCLUSIVAMENTE l'oggetto JSON. NESSUN markdown, NESSUN testo prima o dopo.\n"
    "- NON inserire commenti nel JSON.\n"
    "- Per valori assenti usa stringa vuota \"\".\n"
    "- Non inventare dati non presenti nel documento.\n"
    "- Trascrivi nomi, cognomi e luoghi ESATTAMENTE come scritti (nessuna normalizzazione).\n"
)

# ─────────────────────────────────────────────────────────────────────────────
# FAMIGLIA: ATTI DI NASCITA / BATTESIMO
# ─────────────────────────────────────────────────────────────────────────────

_JSON_NASCITA = """{
  "metadata": {"comunita": "NOME_COMUNE", "parrocchia": "NOME_PARROCCHIA", "anno": "1810"},
  "atti": [
    {
      "numero_atto": "42",
      "tipo": "nascita",
      "soggetto": {
        "cognome": "Rossi", "nome": "Carlo", "sesso": "M",
        "soprannome": "", "prefisso_nome": "", "suffisso_nome": "",
        "data_nascita": "3 maggio 1810", "luogo_nascita": "Roma", "ora_nascita": "ore dieci",
        "data_battesimo": "", "luogo_battesimo": ""
      },
      "padre": {
        "cognome": "Rossi", "nome": "Giovanni", "eta": "35",
        "prefisso_nome": "",
        "professione": "falegname", "domicilio": "via dei Fiori 5",
        "luogo_nascita": "Roma", "fu": false
      },
      "madre": {
        "cognome_nubile": "Bianchi", "nome": "Maria", "eta": "30",
        "prefisso_nome": "",
        "professione": "", "domicilio": "", "luogo_nascita": ""
      },
      "testimoni": [
        {"cognome": "Verdi", "nome": "Luigi", "eta": "40", "soprannome": "", "professione": "commerciante", "domicilio": ""},
        {"cognome": "Neri", "nome": "Antonio", "eta": "45", "soprannome": "", "professione": "possidente", "domicilio": ""}
      ],
      "note": ""
    }
  ]
}"""

def _prompt_nascita(dt, user_tips):
    if "SCN" in dt or "1806" in dt:
        variante = (
            "\nVARIANTE SCN (Stato Civile Napoleonico, 1806-1815):\n"
            "- Le date sono in lettere ('L'anno milleottocentosei, il giorno tre maggio').\n"
            "- Il dichiarante è il padre che si presenta fisicamente all'ufficiale comunale.\n"
            "- L'ufficiale è il Sindaco o un delegato comunale, NON un parroco.\n"
        )
    elif "Toscana" in dt:
        variante = (
            "\nVARIANTE SCR/Toscana (Granducato, 1817-1865):\n"
            "- L'ufficiale è il parroco delegato dello Stato. Le date sono in cifre arabiche.\n"
            "- Il battesimo può essere riportato nell'atto stesso: includi in 'note'.\n"
            "- Formule ecclesiastiche intercalate: riportale in 'note'.\n"
        )
    elif "Due Sicilie" in dt:
        variante = (
            "\nVARIANTE SCR/Due Sicilie (1816-1865):\n"
            "- L'ufficiale è il Sindaco Decurionale. Età indicata come 'di anni X'.\n"
            "- Quattro testimoni (non due). Nomi e cognomi dialettali: trascrivi esattamente.\n"
        )
    elif "Piemonte" in dt:
        variante = (
            "\nVARIANTE SCR/Piemonte (Codice Albertino, 1837-1865):\n"
            "- Linguaggio molto burocratico e standardizzato.\n"
            "- Atto può essere in francese o bilingue (Savoia, Nizza, Valle d'Aosta): riporta lingua originale.\n"
        )
    elif "Veneto" in dt:
        variante = (
            "\nVARIANTE SCR/Veneto (Lombardo-Veneto, 1816-1866):\n"
            "- Formule di matrice austriaca. Possibile testo in tedesco o latino: riporta in 'note'.\n"
        )
    elif "SCI" in dt or "dal 1866" in dt:
        variante = (
            "\nVARIANTE SCI (Stato Civile Italiano, dal 1866):\n"
            "- Formato standardizzato nazionale. Ufficiale: Sindaco o delegato.\n"
            "- Annotazioni a margine frequenti: riportale in 'note'.\n"
        )
    elif "Parrocchiale" in dt or "Battesim" in dt:
        variante = (
            "\nVARIANTE PARROCCHIALE (sec. XVI-XIX):\n"
            "- Redatto dal parroco in italiano o latino.\n"
            "- Struttura: nome battezzato, padre, madre (cognome da nubile), padrino/madrina.\n"
            "- Includi padrino/madrina nei 'testimoni' con ruolo in 'professione'.\n"
        )
    elif "Esposti" in dt or "Illegittim" in dt:
        variante = (
            "\nVARIANTE ESPOSTI/ILLEGITTIMI:\n"
            "- Cognome del bambino esposto: cognome convenzionale dell'istituto o 'Esposto'.\n"
            "- Padre spesso 'ignoto': usa stringa vuota.\n"
            "- Balia, istituto, trovante: inserisci in 'testimoni' con ruolo in 'professione'.\n"
            "- Segni identificativi (nastro, medaglia, lettera): includi in 'note'.\n"
        )
    else:
        variante = ""

    return (
        f"{_BASE}\nTIPOLOGIA: {dt}\n"
        "COMPITO: Estrai tutti gli atti di nascita o battesimo presenti nella pagina.\n"
        f"{variante}\n"
        "STRUTTURA JSON RICHIESTA (SEGUI ESATTAMENTE):\n"
        f"{_JSON_NASCITA}\n\n"
        "ATTENZIONE:\n"
        "- Più atti nella pagina → inseriscili come elementi separati nell'array 'atti'.\n"
        "- 'fu': true se il genitore è defunto ('fu', 'fù', 'quondam', 'q.m').\n"
        "- 'sesso': 'M' per maschio, 'F' per femmina.\n"
        f"\nNOTE AGGIUNTIVE UTENTE:\n{user_tips}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FAMIGLIA: ATTI DI MATRIMONIO
# ─────────────────────────────────────────────────────────────────────────────

_JSON_MATRIMONIO = """{
  "metadata": {"comunita": "NOME_COMUNE", "anno": "1850"},
  "atti": [
    {
      "numero_atto": "12",
      "tipo": "matrimonio",
      "data_matrimonio": "15 aprile 1850",
      "luogo_matrimonio": "Roma",
      "sposo": {
        "cognome": "Rossi", "nome": "Giovanni", "eta": "28",
        "soprannome": "", "prefisso_nome": "",
        "data_nascita": "", "luogo_nascita": "",
        "professione": "falegname", "domicilio": "via dei Fiori 5",
        "religione": "", "istruzione": "", "titolo": "",
        "stato_civile": "celibe",
        "padre_cognome": "Rossi", "padre_nome": "Pietro", "padre_fu": false,
        "madre_cognome": "Neri", "madre_nome": "Anna"
      },
      "sposa": {
        "cognome": "Bianchi", "nome": "Maria", "eta": "22",
        "soprannome": "", "prefisso_nome": "",
        "data_nascita": "", "luogo_nascita": "",
        "professione": "", "domicilio": "via Roma 3",
        "religione": "", "istruzione": "", "titolo": "",
        "stato_civile": "nubile",
        "padre_cognome": "Bianchi", "padre_nome": "Carlo", "padre_fu": true,
        "madre_cognome": "Verdi", "madre_nome": "Rosa"
      },
      "testimoni": [
        {"cognome": "Neri", "nome": "Luigi", "eta": "40", "soprannome": "", "professione": "commerciante", "domicilio": ""},
        {"cognome": "Russo", "nome": "Paolo", "eta": "35", "soprannome": "", "professione": "possidente", "domicilio": ""}
      ],
      "note": ""
    }
  ]
}"""

def _prompt_matrimonio(dt, user_tips):
    if "SCN" in dt or "1806" in dt:
        variante = (
            "\nVARIANTE SCN:\n"
            "- Quattro testimoni maschi maggiorenni. Le date sono in lettere.\n"
            "- Pubblicazioni precedenti: riportale in 'note'.\n"
        )
    elif "Due Sicilie" in dt:
        variante = (
            "\nVARIANTE SCR/Due Sicilie:\n"
            "- Quattro testimoni (caratteristica borbonica). 'Decurionato': riporta in 'note'.\n"
        )
    elif "Toscana" in dt:
        variante = (
            "\nVARIANTE SCR/Toscana:\n"
            "- Il parroco officia come ministro del sacramento e come ufficiale civile.\n"
            "- Formule latine canoniche intercalate: riportale in 'note'.\n"
        )
    elif "Processetto" in dt or "Allegati" in dt:
        variante = (
            "\nVARIANTE PROCESSETTO/ALLEGATI MATRIMONIALI:\n"
            "- Documento istruttorio pre-matrimoniale, non l'atto di matrimonio.\n"
            "- Contiene interrogatori, battesimi, stati liberi degli sposi.\n"
            "- Estrai sposo e sposa dai dati anagrafici nei documenti allegati.\n"
            "- In 'note': indica il tipo di allegato (stato libero, fede di battesimo, ecc.).\n"
        )
    elif "Pubblicazioni" in dt:
        variante = (
            "\nVARIANTE PUBBLICAZIONI DI MATRIMONIO (registro bandi):\n"
            "- Non è l'atto di matrimonio, ma il registro delle pubblicazioni (bandi).\n"
            "- Estrai sposo, sposa, date delle pubblicazioni (in 'note').\n"
            "- Il matrimonio potrebbe non aver avuto luogo: indica l'incertezza in 'note'.\n"
        )
    elif "Religioso" in dt:
        variante = (
            "\nVARIANTE MATRIMONIO RELIGIOSO POST-CONCORDATO (1929+):\n"
            "- Atto canonico con effetti civili per il Concordato del 1929.\n"
            "- Parroco officiante e parrocchia: includi in 'note'.\n"
        )
    else:
        variante = ""

    return (
        f"{_BASE}\nTIPOLOGIA: {dt}\n"
        "COMPITO: Estrai tutti gli atti di matrimonio presenti nella pagina.\n"
        f"{variante}\n"
        "STRUTTURA JSON RICHIESTA (SEGUI ESATTAMENTE):\n"
        f"{_JSON_MATRIMONIO}\n\n"
        "ATTENZIONE:\n"
        "- Più atti nella pagina → elementi separati nell'array 'atti'.\n"
        "- 'padre_fu': true se il genitore è defunto ('fu', 'quondam').\n"
        "- 'stato_civile': 'celibe'/'vedovo' per lo sposo, 'nubile'/'vedova' per la sposa.\n"
        f"\nNOTE AGGIUNTIVE UTENTE:\n{user_tips}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FAMIGLIA: ATTI DI MORTE / SEPOLTURA
# ─────────────────────────────────────────────────────────────────────────────

_JSON_MORTE = """{
  "metadata": {"comunita": "NOME_COMUNE", "anno": "1870"},
  "atti": [
    {
      "numero_atto": "7",
      "tipo": "morte",
      "defunto": {
        "cognome": "Rossi", "nome": "Giovanni", "sesso": "M",
        "soprannome": "", "prefisso_nome": "", "suffisso_nome": "",
        "data_morte": "12 marzo 1870", "luogo_morte": "Roma", "ora_morte": "ore due di notte",
        "data_nascita": "", "luogo_nascita": "",
        "eta": "65", "professione": "falegname", "domicilio": "via dei Fiori 5",
        "religione": "", "istruzione": "", "titolo": "",
        "stato_civile": "vedovo",
        "padre_cognome": "Rossi", "padre_nome": "Pietro", "padre_fu": true,
        "madre_cognome": "Neri", "madre_nome": "Anna", "madre_fu": true,
        "coniuge_cognome": "Bianchi", "coniuge_nome": "Maria",
        "causa_morte": "febbre tifoide",
        "data_sepoltura": "", "luogo_sepoltura": "", "tipo_sepoltura": ""
      },
      "dichiaranti": [
        {"cognome": "Verdi", "nome": "Luigi", "eta": "40", "soprannome": "", "professione": "vicino di casa", "domicilio": "", "relazione": "vicino"},
        {"cognome": "Neri", "nome": "Carlo", "eta": "35", "soprannome": "", "professione": "commerciante", "domicilio": "", "relazione": "parente"}
      ],
      "note": ""
    }
  ]
}"""

def _prompt_morte(dt, user_tips):
    if "Due Sicilie" in dt:
        variante = (
            "\nVARIANTE SCR/Due Sicilie:\n"
            "- Cause di morte spesso in dialetto meridionale: trascrivi esattamente, non correggere.\n"
            "- L'ufficiale è il Sindaco Decurionale: riporta in 'note'.\n"
        )
    elif "Toscana" in dt:
        variante = (
            "\nVARIANTE SCR/Toscana:\n"
            "- Note di sepoltura (luogo, data, sacramenti): includi in 'note'.\n"
            "- Cause di morte arcaiche: 'vizio di petto', 'accidente apoplettico'.\n"
        )
    elif "Ospedalieri" in dt:
        variante = (
            "\nVARIANTE REGISTRO DEFUNTI OSPEDALIERI:\n"
            "- Registro di reparto/istituto ospedaliero. Dati anagrafici possono essere incompleti.\n"
            "- In 'note': reparto, numero letto, medico curante (se indicati).\n"
            "- La causa di morte è quasi sempre indicata: riportala esattamente.\n"
        )
    elif "Parrocchiale" in dt or "Sepoltur" in dt:
        variante = (
            "\nVARIANTE PARROCCHIALE (Morti/Sepolture):\n"
            "- Il registro può essere in italiano o latino.\n"
            "- La data è spesso quella della sepoltura, non della morte.\n"
            "- In 'note': sacramenti ricevuti, luogo di sepoltura, eventuali lasciti.\n"
        )
    else:
        variante = ""

    return (
        f"{_BASE}\nTIPOLOGIA: {dt}\n"
        "COMPITO: Estrai tutti gli atti di morte o sepoltura presenti nella pagina.\n"
        f"{variante}\n"
        "STRUTTURA JSON RICHIESTA (SEGUI ESATTAMENTE):\n"
        f"{_JSON_MORTE}\n\n"
        "ATTENZIONE:\n"
        "- 'causa_morte': trascrivi esattamente come scritto, anche in dialetto o terminologia arcaica.\n"
        "- 'stato_civile': 'celibe'/'nubile'/'coniugato'/'coniugata'/'vedovo'/'vedova'.\n"
        "- 'padre_fu'/'madre_fu': true se indicati come già defunti ('fu', 'quondam').\n"
        "- Più atti nella pagina → elementi separati nell'array 'atti'.\n"
        f"\nNOTE AGGIUNTIVE UTENTE:\n{user_tips}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FAMIGLIA: CENSIMENTI / STATI ANIME
# ─────────────────────────────────────────────────────────────────────────────

_TOSCANA_SPECIFIC = """
ISTRUZIONE DOCUMENTO: Stati delle Anime (Granducato di Toscana).
RUOLO: Sei uno Scanner Paleografico "Cieco". Concentrati *ESCLUSIVAMENTE* sulla foto che stai vedendo ora.

--- REGOLE PALEOGRAFICHE ---
1. TUTTI GLI INDIVIDUI: Trascrivi OGNI SINGOLA PERSONA presente nell'immagine (tipicamente 25 righe per pagina intera). Trascrivi anche se vedi solo l'inizio o la fine di una famiglia.
2. NOMI e COGNOMI ESATTI: Trascrivi esattamente le lettere incise. NON USARE IL TUO DIZIONARIO. Non correggere cognomi rari.
3. ATTENZIONE ALLE VOCALI: Fai molta attenzione all'ultima vocale. Trascrivi la parola completa.
4. SEGNI DI RIPETIZIONE: Trascrivi le virgolette (") come una virgoletta escaped (\\\"). NON USARE MAI virgolette triple.
5. CHIAVI NUMERICHE (1-20):
   1. Casa | 2. Famiglia | 3. Progressivo
   4. Cognome | 5. Nome | 6. Età
   7/8/9. Stato Maschio (Celibe/Ammogliato/Vedovo)
   10/11/12. Stato Femmina (Nubile/Maritata/Vedova)
   14. Religione | 15. Patria | 16. Professione
   17. Indigenti/Beni | 18. Istruzione | 19. Osservazioni
6. OSSERVAZIONI (chiave "19"): Se la colonna Osservazioni contiene un testo (es. "Capo di famiglia", "assente", ecc.), includilo SEMPRE con chiave "19". Ometti la chiave solo se la cella è vuota o contiene solo trattini.

STRUTTURA LISTA JSON (Tutte le persone):
[
  {"1": "1", "2": "1", "3": "1", "4": "Acciaj", "5": "Gaspero", "6": "60", "7": "", "8": "1", "14": "Cattolico", "15": "Poncarale", "16": "Possidente", "17": "", "18": "", "19": "Capo di famiglia"},
  {"1": "1", "2": "1", "3": "2", "4": "\\"", "5": "Rosa", "6": "62", "11": "1", "14": "", "15": "", "16": "\\"", "17": "", "18": "", "19": ""}
]
"""

_JSON_CENSIMENTO = """{
  "metadata": {"comunita": "NOME_COMUNE", "parrocchia": "NOME_PARROCCHIA", "anno": "1850"},
  "righe": [
    {"1": "1", "2": "1", "3": "1", "4": "Rossi", "5": "Giovanni", "6": "45", "8": "1", "15": "Roma", "16": "contadino", "19": "capofamiglia"},
    {"1": "1", "2": "1", "3": "2", "4": "\\"",    "5": "Maria",    "6": "40", "11": "1", "15": "\\"", "16": "massaia"},
    {"1": "1", "2": "1", "3": "3", "4": "\\"",    "5": "Carlo",    "6": "15", "7": "1",  "15": "\\"", "16": ""}
  ]
}"""

def _prompt_censimento(dt, user_tips):
    if "Granducato di Toscana" in dt:
        return f"{_BASE}\n{_TOSCANA_SPECIFIC}\nNOTE PERENTORIE (RIGORE GRAFICO):\n{user_tips}"

    if "Lombardo-Veneto" in dt or "Lombardo" in dt:
        variante = (
            "\nVARIANTE LOMBARDO-VENETO (sec. XIX):\n"
            "- Censimento di matrice austriaca, struttura tabellare rigida.\n"
            "- Intestazioni di colonna possibili in tedesco: riporta i valori in italiano.\n"
            "- Il numero di famiglia (col. 2) può corrispondere al numero di casa.\n"
        )
    elif "Stato di Famiglia" in dt or "Notoriet" in dt:
        variante = (
            "\nVARIANTE STATO DI FAMIGLIA:\n"
            "- Certifica la composizione del nucleo familiare.\n"
            "- Includi la relazione di parentela in 'professione' (es. 'moglie', 'figlio', 'genero').\n"
        )
    elif "Foglio di Famiglia" in dt:
        variante = (
            "\nVARIANTE FOGLIO DI FAMIGLIA ANAGRAFE COMUNALE (post-1864):\n"
            "- Registro anagrafico standardizzato post-unitario.\n"
            "- La relazione col capofamiglia va inserita in 'professione' (col. 16).\n"
        )
    else:
        variante = (
            "\nVARIANTE CENSIMENTO GENERICO:\n"
            "- Estrai ogni persona con: n. casa (col.1), n. famiglia (col.2), progressivo (col.3),\n"
            "  cognome (col.4), nome (col.5), età (col.6), stato civile (col.7-12),\n"
            "  religione (col.14), luogo origine (col.15), professione (col.16), note (col.19).\n"
        )

    return (
        f"{_BASE}\nTIPOLOGIA: {dt}\n"
        "COMPITO: Estrai TUTTE le persone presenti nel documento.\n"
        f"{variante}\n"
        "STRUTTURA JSON RICHIESTA:\n"
        f"{_JSON_CENSIMENTO}\n\n"
        "REGOLE:\n"
        "- I segni di ripetizione ('\"', 'id.', 'idem', '//', 'detto') → trascrivi come '\\\"'.\n"
        "- Trascrivi ESATTAMENTE nomi, cognomi, professioni: nessuna normalizzazione.\n"
        "- Stato civile: 7=Celibe_M, 8=Ammogliato_M, 9=Vedovo_M, 10=Nubile_F, 11=Maritata_F, 12=Vedova_F.\n"
        f"\nNOTE AGGIUNTIVE UTENTE:\n{user_tips}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FAMIGLIA: CATASTI
# ─────────────────────────────────────────────────────────────────────────────

_JSON_CATASTO = """{
  "metadata": {"comunita": "NOME_COMUNE", "anno": "1742", "tipo_catasto": "Onciario"},
  "famiglie": [
    {
      "numero_fuoco": "1",
      "cognome": "Rossi",
      "componenti": [
        {"3": "1", "4": "Rossi", "5": "Giovanni", "6": "45", "8": "1", "14": "Cattolico", "15": "Roma", "16": "contadino", "17": "", "18": "", "19": "capofamiglia"},
        {"3": "2", "4": "\\"", "5": "Maria",    "6": "40", "11": "1", "14": "",          "15": "",     "16": "",          "17": "", "18": "", "19": "moglie"},
        {"3": "3", "4": "\\"", "5": "Carlo",    "6": "12", "7": "1",  "14": "",          "15": "",     "16": "",          "17": "", "18": "", "19": "figlio"}
      ],
      "beni": "1 moggio di terreno arativo in contrada X; 1 casa di abitazione"
    }
  ]
}"""

def _prompt_catasto(dt, user_tips):
    if "Onciario" in dt:
        variante = (
            "\nVARIANTE CATASTO ONCIARIO (Due Sicilie, sec. XVIII):\n"
            "- Censimento fiscale del Regno di Napoli. Beni espressi in 'once' (unità fiscale).\n"
            "- I 'fuochi' sono le unità familiari censite: usa 'numero_fuoco'.\n"
            "- In 'beni': terreni, case, animali, capitali dichiarati con valore in once.\n"
        )
    elif "Murattiano" in dt:
        variante = (
            "\nVARIANTE CATASTO MURATTIANO (Due Sicilie, 1808-1815):\n"
            "- Registro di PROPRIETÀ IMMOBILIARI (non demografico come l'Onciario).\n"
            "- In 'beni': natura del bene, superficie, confini, valore catastale.\n"
            "- Il 'capofamiglia' è il proprietario del bene.\n"
        )
    elif "Gregoriano" in dt:
        variante = (
            "\nVARIANTE CATASTO GREGORIANO (Stato Pontificio, 1816-1835):\n"
            "- Registro di PROPRIETÀ IMMOBILIARI. Struttura tabellare.\n"
            "- In 'beni': natura del bene, classe, perticato, rendita catastale.\n"
        )
    elif "Rivele" in dt or "Fuochi" in dt:
        variante = (
            "\nVARIANTE RIVELE / NUMERAZIONE DEI FUOCHI (Due Sicilie, sec. XVI-XVII):\n"
            "- Le 'Rivele' sono dichiarazioni dei capifamiglia ai fini fiscali.\n"
            "- I 'fuochi' sono le unità familiari: usa 'numero_fuoco'.\n"
            "- In 'beni': terreni, case, animali, censi dichiarati.\n"
        )
    else:
        variante = ""

    return (
        f"{_BASE}\nTIPOLOGIA: {dt}\n"
        "COMPITO: Estrai tutte le famiglie/proprietari e i loro componenti/beni.\n"
        f"{variante}\n"
        "STRUTTURA JSON RICHIESTA:\n"
        f"{_JSON_CATASTO}\n\n"
        "REGOLE:\n"
        "- I segni di ripetizione → trascrivi come '\\\"'.\n"
        "- Trascrivi ESATTAMENTE nomi, cognomi, toponimi: nessuna normalizzazione.\n"
        "- In 'beni': testo libero con tutti i beni e valori indicati nel documento.\n"
        f"\nNOTE AGGIUNTIVE UTENTE:\n{user_tips}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FAMIGLIA: DOCUMENTI MILITARI
# ─────────────────────────────────────────────────────────────────────────────

_JSON_MILITARE = """{
  "metadata": {"distretto": "NOME_DISTRETTO", "classe": "1870", "anno": "1890"},
  "atti": [
    {
      "tipo": "militare",
      "cognome": "Rossi", "nome": "Giovanni",
      "soprannome": "", "prefisso_nome": "",
      "eta": "",
      "data_nascita": "3 maggio 1850", "luogo_nascita": "Roma",
      "domicilio": "", "residenza": "",
      "religione": "", "istruzione": "",
      "descrizione": "",
      "padre_cognome": "Rossi", "padre_nome": "Pietro",
      "madre_cognome": "Bianchi", "madre_nome": "Maria",
      "professione_civile": "contadino",
      "numero_matricola": "1234",
      "grado": "Soldato", "corpo": "Fanteria", "arma": "62 Reggimento",
      "data_arruolamento": "10 gennaio 1870",
      "data_congedo": "15 marzo 1873",
      "campagne": "Guerra 1866",
      "ferite": "",
      "decorazioni": "",
      "causa_congedo": "Fine ferma",
      "note": ""
    }
  ]
}"""

def _prompt_militare(dt, user_tips):
    if "Foglio Matricolare" in dt:
        variante = (
            "\nVARIANTE FOGLIO MATRICOLARE (scheda individuale):\n"
            "- Documento individuale che segue tutta la carriera militare del soldato.\n"
            "- In 'campagne': tutte le campagne di guerra elencate.\n"
            "- In 'decorazioni': tutte le onorificenze e medaglie.\n"
            "- In 'causa_congedo': fine ferma, riforma, invalido, ecc.\n"
        )
    else:
        variante = (
            "\nVARIANTE RUOLO DI MATRICOLA / LEVA (registro collettivo):\n"
            "- Registro che elenca più soggetti per la stessa classe di leva.\n"
            "- Estrai ogni soggetto come elemento separato dell'array 'atti'.\n"
            "- In 'note': giudizio di idoneità ('idoneo', 'riformato', 'esonerato', ecc.).\n"
        )

    return (
        f"{_BASE}\nTIPOLOGIA: {dt}\n"
        "COMPITO: Estrai tutti i dati militari presenti nel documento.\n"
        f"{variante}\n"
        "STRUTTURA JSON RICHIESTA:\n"
        f"{_JSON_MILITARE}\n\n"
        "REGOLE:\n"
        "- Trascrivi ESATTAMENTE gradi, corpi, decorazioni: nessuna abbreviazione inventata.\n"
        "- Date nel formato originale del documento.\n"
        "- Se un campo non è presente, usa stringa vuota \"\".\n"
        f"\nNOTE AGGIUNTIVE UTENTE:\n{user_tips}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FAMIGLIA: DOCUMENTI VARI (Passaporti, Consolari, ecc.)
# ─────────────────────────────────────────────────────────────────────────────

_JSON_ALTRO = """{
  "metadata": {"comunita": "", "anno": ""},
  "atti": [
    {
      "tipo": "documento",
      "numero_atto": "",
      "soggetto": {
        "cognome": "", "nome": "", "sesso": "M",
        "soprannome": "", "prefisso_nome": "",
        "eta": "",
        "data_nascita": "", "luogo_nascita": "",
        "professione": "", "domicilio": "", "residenza": "",
        "religione": "", "istruzione": "", "titolo": "",
        "descrizione": "",
        "numero_documento": "", "data_rilascio": "",
        "destinazione": "", "data_emigrazione": "",
        "padre_cognome": "", "padre_nome": "",
        "madre_cognome": "", "madre_nome": ""
      },
      "note": ""
    }
  ]
}"""

def _prompt_altro(dt, user_tips):
    if "Passaporto" in dt or "Espatrio" in dt:
        variante = (
            "\nVARIANTE PASSAPORTO/PERMESSO DI ESPATRIO:\n"
            "- Estrai: titolare, data e luogo di nascita, professione, domicilio.\n"
            "- 'destinazione': paese/luogo di destinazione dell'espatrio.\n"
            "- 'data_emigrazione': data di partenza o validità del passaporto.\n"
            "- 'numero_documento': numero del passaporto o permesso.\n"
            "- 'data_rilascio': data di rilascio del documento.\n"
            "- 'descrizione': descrizione fisica del titolare (se presente nel documento).\n"
        )
    elif "Consolari" in dt:
        variante = (
            "\nVARIANTE ATTI CONSOLARI ITALIANI ALL'ESTERO:\n"
            "- Il consolato può aver registrato nascite, matrimoni, morti di cittadini italiani all'estero.\n"
            "- In 'note': paese estero, consolato, tipo di atto.\n"
        )
    elif "Religioso" in dt:
        variante = (
            "\nVARIANTE MATRIMONIO RELIGIOSO POST-CONCORDATO (1929+):\n"
            "- In 'note': parrocchia, parroco, data registrazione civile.\n"
        )
    else:
        variante = ""

    return (
        f"{_BASE}\nTIPOLOGIA: {dt}\n"
        "COMPITO: Estrai tutti i dati anagrafici presenti nel documento.\n"
        f"{variante}\n"
        "STRUTTURA JSON RICHIESTA:\n"
        f"{_JSON_ALTRO}\n"
        f"\nNOTE AGGIUNTIVE UTENTE:\n{user_tips}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FAMIGLIA: CRESIMA / CONFERMAZIONE
# ─────────────────────────────────────────────────────────────────────────────

_JSON_CRESIMA = """{
  "metadata": {"comunita": "", "parrocchia": "", "anno": ""},
  "atti": [
    {
      "numero_atto": "",
      "tipo": "cresima",
      "data_cresima": "15 aprile 1820", "luogo_cresima": "Roma",
      "soggetto": {
        "cognome": "Rossi", "nome": "Carlo", "sesso": "M",
        "soprannome": "", "prefisso_nome": "",
        "eta": "12", "data_nascita": "", "luogo_nascita": ""
      },
      "padre": {"cognome": "Rossi", "nome": "Giovanni", "prefisso_nome": "", "professione": "falegname"},
      "madre": {"cognome_nubile": "Bianchi", "nome": "Maria", "prefisso_nome": ""},
      "padrino": {"cognome": "Verdi", "nome": "Luigi", "soprannome": "", "professione": ""},
      "vescovo": "Mons. Mario Rossi",
      "note": ""
    }
  ]
}"""

def _prompt_cresima(dt, user_tips):
    return (
        f"{_BASE}\nTIPOLOGIA: {dt}\n"
        "COMPITO: Estrai tutti gli atti di cresima/confermazione presenti nel documento.\n"
        "STRUTTURA JSON RICHIESTA:\n"
        f"{_JSON_CRESIMA}\n\n"
        "ATTENZIONE:\n"
        "- 'tipo': usa sempre 'cresima'.\n"
        "- 'vescovo': nome del vescovo/ministro che ha amministrato il sacramento.\n"
        "- 'padrino': il padrino o madrina della cresima (non del battesimo).\n"
        "- Padrino/madrina vanno in 'padrino', non nei 'testimoni'.\n"
        "- Pi\u00f9 atti nella pagina \u2192 elementi separati nell'array 'atti'.\n"
        f"\nNOTE AGGIUNTIVE UTENTE:\n{user_tips}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FAMIGLIA: PRIMA COMUNIONE
# ─────────────────────────────────────────────────────────────────────────────

_JSON_COMUNIONE = """{
  "metadata": {"comunita": "", "parrocchia": "", "anno": ""},
  "atti": [
    {
      "numero_atto": "",
      "tipo": "comunione",
      "data_comunione": "5 aprile 1820", "luogo_comunione": "Roma",
      "soggetto": {
        "cognome": "Rossi", "nome": "Carlo", "sesso": "M",
        "soprannome": "", "prefisso_nome": "",
        "eta": "10", "data_nascita": "", "luogo_nascita": ""
      },
      "padre": {"cognome": "Rossi", "nome": "Giovanni", "prefisso_nome": ""},
      "madre": {"cognome_nubile": "Bianchi", "nome": "Maria", "prefisso_nome": ""},
      "note": ""
    }
  ]
}"""

def _prompt_comunione(dt, user_tips):
    return (
        f"{_BASE}\nTIPOLOGIA: {dt}\n"
        "COMPITO: Estrai tutti gli atti di prima comunione presenti nel documento.\n"
        "STRUTTURA JSON RICHIESTA:\n"
        f"{_JSON_COMUNIONE}\n\n"
        "ATTENZIONE:\n"
        "- 'tipo': usa sempre 'comunione'.\n"
        "- Et\u00e0 tipica: 8-12 anni.\n"
        "- Pi\u00f9 atti \u2192 elementi separati nell'array 'atti'.\n"
        f"\nNOTE AGGIUNTIVE UTENTE:\n{user_tips}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FAMIGLIA: ATTI DI ADOZIONE
# ─────────────────────────────────────────────────────────────────────────────

_JSON_ADOZIONE = """{
  "metadata": {"comunita": "", "anno": ""},
  "atti": [
    {
      "numero_atto": "",
      "tipo": "adozione",
      "data_adozione": "10 marzo 1870", "luogo_adozione": "Roma",
      "adottato": {
        "cognome": "Esposto", "nome": "Carlo", "sesso": "M",
        "soprannome": "", "prefisso_nome": "",
        "eta": "5", "data_nascita": "", "luogo_nascita": ""
      },
      "padre_adottivo": {"cognome": "Rossi", "nome": "Giovanni", "professione": "possidente"},
      "madre_adottiva": {"cognome_nubile": "Bianchi", "nome": "Maria"},
      "padre_biologico": {"cognome": "", "nome": ""},
      "madre_biologica": {"cognome_nubile": "", "nome": ""},
      "note": ""
    }
  ]
}"""

def _prompt_adozione(dt, user_tips):
    return (
        f"{_BASE}\nTIPOLOGIA: {dt}\n"
        "COMPITO: Estrai tutti gli atti di adozione presenti nel documento.\n"
        "STRUTTURA JSON RICHIESTA:\n"
        f"{_JSON_ADOZIONE}\n\n"
        "ATTENZIONE:\n"
        "- 'tipo': usa sempre 'adozione'.\n"
        "- 'padre_biologico'/'madre_biologica': compila solo se indicati esplicitamente nel documento.\n"
        "- Per esposti/trovatelli: genitori biologici solitamente ignoti \u2192 lascia vuoti.\n"
        "- Pi\u00f9 atti \u2192 elementi separati nell'array 'atti'.\n"
        f"\nNOTE AGGIUNTIVE UTENTE:\n{user_tips}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FAMIGLIA: ORDINAZIONI SACERDOTALI
# ─────────────────────────────────────────────────────────────────────────────

_JSON_ORDINAZIONE = """{
  "metadata": {"diocesi": "", "anno": ""},
  "atti": [
    {
      "numero_atto": "",
      "tipo": "ordinazione",
      "data_ordinazione": "22 settembre 1840", "luogo_ordinazione": "Roma",
      "tipo_ordinazione": "Presbiterato",
      "soggetto": {
        "cognome": "Rossi", "nome": "Carlo",
        "soprannome": "", "prefisso_nome": "Don",
        "data_nascita": "", "luogo_nascita": "",
        "titolo": "Don", "religione": "Cattolico"
      },
      "vescovo": "Mons. Mario Bianchi",
      "diocesi": "Diocesi di Roma",
      "padre": {"cognome": "Rossi", "nome": "Giovanni"},
      "madre": {"cognome_nubile": "Neri", "nome": "Anna"},
      "note": ""
    }
  ]
}"""

def _prompt_ordinazione(dt, user_tips):
    return (
        f"{_BASE}\nTIPOLOGIA: {dt}\n"
        "COMPITO: Estrai tutti gli atti di ordinazione sacerdotale presenti nel documento.\n"
        "STRUTTURA JSON RICHIESTA:\n"
        f"{_JSON_ORDINAZIONE}\n\n"
        "ATTENZIONE:\n"
        "- 'tipo': usa sempre 'ordinazione'.\n"
        "- 'tipo_ordinazione': es. 'Diaconato', 'Presbiterato', 'Episcopato', 'Ordini Minori'.\n"
        "- 'vescovo': il vescovo consacrante.\n"
        "- 'titolo': titolo ecclesiastico (Don, Padre, Fra, ecc.).\n"
        "- Pi\u00f9 atti \u2192 elementi separati nell'array 'atti'.\n"
        f"\nNOTE AGGIUNTIVE UTENTE:\n{user_tips}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FALLBACK GENERICO
# ─────────────────────────────────────────────────────────────────────────────

_JSON_GENERICO = """{
  "metadata": {"comunita": "", "anno": ""},
  "atti": [
    {
      "tipo": "documento",
      "numero_atto": "",
      "soggetto": {
        "cognome": "", "nome": "", "sesso": "M",
        "eta": "",
        "data_nascita": "", "luogo_nascita": "",
        "professione": "", "domicilio": "",
        "religione": "", "istruzione": "", "titolo": "",
        "descrizione": "",
        "padre_cognome": "", "padre_nome": "",
        "madre_cognome": "", "madre_nome": ""
      },
      "note": ""
    }
  ]
}"""

def _prompt_generico(dt, user_tips):
    return (
        f"{_BASE}\nTIPOLOGIA: {dt}\n"
        "COMPITO: Estrai tutti i dati genealogici presenti nel documento.\n"
        "STRUTTURA JSON RICHIESTA:\n"
        f"{_JSON_GENERICO}\n"
        "ATTENZIONE:\n"
        "- Usa il formato 'atti' con tipo=documento per ogni individuo trovato.\n"
        "- Includi TUTTI i campi presenti nel documento, anche se non nell'esempio.\n"
        f"\nNOTE AGGIUNTIVE UTENTE:\n{user_tips}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FUNZIONE PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────

def get_available_types():
    return [
        "Atto di Nascita / Battesimo",
        "Atto di Matrimonio",
        "Atto di Morte",
        "Atto di Cresima / Confermazione",
        "Prima Comunione",
        "Atto di Adozione",
        "Ordinazione Sacerdotale",
        "Stati delle Anime Granducato di Toscana",
        "Stato delle Anime (Generico)",
        "Processetto Matrimoniale",
        "Censimento Storico",
        "Ricerca Libera / Altro",
    ]


def compose_extraction_prompt(doc_type, user_tips=""):
    dt = str(doc_type)
    if _is_nascita(dt):
        return _prompt_nascita(dt, user_tips)
    elif _is_matrimonio(dt):
        return _prompt_matrimonio(dt, user_tips)
    elif _is_morte(dt):
        return _prompt_morte(dt, user_tips)
    elif _is_cresima(dt):
        return _prompt_cresima(dt, user_tips)
    elif _is_comunione(dt):
        return _prompt_comunione(dt, user_tips)
    elif _is_adozione(dt):
        return _prompt_adozione(dt, user_tips)
    elif _is_ordinazione(dt):
        return _prompt_ordinazione(dt, user_tips)
    elif _is_censimento(dt):
        return _prompt_censimento(dt, user_tips)
    elif _is_catasto(dt):
        return _prompt_catasto(dt, user_tips)
    elif _is_militare(dt):
        return _prompt_militare(dt, user_tips)
    elif _is_altro(dt):
        return _prompt_altro(dt, user_tips)
    else:
        return _prompt_generico(dt, user_tips)
