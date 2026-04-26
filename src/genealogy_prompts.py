def get_available_types():
    return [
        "Atto di Nascita / Battesimo",
        "Atto di Matrimonio",
        "Atto di Morte",
        "Stati delle Anime Granducato di Toscana",
        "Stato delle Anime (Generico)",
        "Processetto Matrimoniale",
        "Censimento Storico",
        "Ricerca Libera / Altro"
    ]

def compose_extraction_prompt(doc_type, user_tips=""):
    base = """Sei un esperto Paleografo e Genealogista. Analizza l'immagine ed estrai i dati in formato JSON.
REGOLE DI OUTPUT: Restituisci ESCLUSIVAMENTE l'oggetto JSON richiesto in modo testuale pulito. 
NON AGGIUNGERE markdown, testo prima o dopo il JSON. 
NON INSERIRE commenti all'interno del codice JSON.
"""

    generic_json = """
Struttura JSON richiesta per ogni record:
{
  "records": [
    {
      "name": {"first": "...", "last": "..."},
      "sex": "M/F",
      "birth": {"date": "...", "place": "..."},
      "original_fields": {
         "1": "Numero Casa", "2": "Numero Famiglia", "3": "Progressivo Persona", "4": "Cognome", "5": "Nome", "6": "Età", 
         "14": "Religione", "15": "Patria", "16": "Professione", "19": "Osservazioni"
      }, 
      "associations": [...]
    }
  ]
}
"""

    # --- PROTOCOLLO FLUIDO E PALEOGRAFICO (v48.0 - Split & Merge) ---
    if "Granducato di Toscana" in doc_type:
        specific = """
ISTRUZIONE DOCUMENTO: Stati delle Anime (Granducato di Toscana).
RUOLO: Sei uno Scanner Paleografico "Cieco". Concentrati *ESCLUSIVAMENTE* sulla foto che stai vedendo ora.

--- REGOLE PALEOGRAFICHE ---
1. TUTTI GLI INDIVIDUI: Trascrivi OGNI SINGOLA PERSONA presente nell'immagine (tipicamente 25 righe per pagina intera). Trascrivi anche se vedi solo l'inizio o la fine di una famiglia.
2. NOMI e COGNOMI ESATTI: Trascrivi esattamente le lettere incise. NON USARE IL TUO DIZIONARIO. Non correggere cognomi rari (es. se leggi 'Andrei' non usare 'Ambrogi'). 
3. ATTENZIONE ALLE VOCALI: Fai molta attenzione all'ultima vocale (es. 'Gaspero' non è 'Gaspera'). Trascrivi la parola completa.
4. SEGNI DI RIPETIZIONE: Trascrivi le virgolette (") come una virgoletta escaped (\\\"). NON USARE MAI virgolette triple (\"\"\").
5. CHIAVI NUMERICHE (1-20):
   1. Casa | 2. Famiglia | 3. Progressivo
   4. Cognome | 5. Nome | 6. Età
   7/8/9. Stato Maschio (Celibe/Ammogliato/Vedovo)
   10/11/12. Stato Femmina (Nubile/Maritata/Vedova)
   14. Religione | 15. Patria | 16. Professione

STRUTTURA LISTA JSON (Tutte le persone):
[
  {"1": "1", "2": "1", "3": "1", "4": "Acciaj", "5": "Gaspero", "6": "60", "7": "", "8": "1", "14": "Cattolica", "16": "Possidente"},
  {"1": "1", "2": "1", "3": "2", "4": "\"", "5": "Rosa", "6": "62", "11": "1", "14": "\"", "16": "\""}
]
"""
        return f"{base}\n{specific}\nNOTE PERENTORIE (RIGORE GRAFICO):\n{user_tips}"
    
    # PER TUTTI GLI ALTRI DOCUMENTI
    return f"{base}\n{generic_json}\nNOTE AGGIUNTIVE:\n{user_tips}"

    return f"{base}\nTIPOLOGIA ATTO: {doc_type}\nNOTE:\n{user_tips}"
