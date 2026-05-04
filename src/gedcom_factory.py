import datetime
import re
import os
import csv
import json
import logging

class GedcomGenerator:
    """Sincronia v15.2.2 - Architettura di Ferro (Completa)"""
    
    MONTH_MAP = {
        'gennaio': 'JAN', 'febbraio': 'FEB', 'marzo': 'MAR', 'aprile': 'APR',
        'maggio': 'MAY', 'giugno': 'JUN', 'luglio': 'JUL', 'agosto': 'AUG',
        'settembre': 'SEP', 'ottobre': 'OCT', 'novembre': 'NOV', 'dicembre': 'DEC'
    }

    TOSCANA_COLUMN_LABELS = {
        '1': 'Casa_Nr', '2': 'Famiglia_Nr', '3': 'Persona_Nr',
        '4': 'Cognome', '5': 'Nome', '6': 'Eta',
        '7': 'Celibe_M', '8': 'Ammogliato_M', '9': 'Vedovo_M',
        '10': 'Nubile_F', '11': 'Maritata_F', '12': 'Vedova_F',
        '14': 'Religione', '15': 'Patria', '16': 'Professione',
        '17': 'Indigenti', '18': 'Istruzione', '19': 'Osservazioni'
    }

    # Mappa universale chiave → tag GEDCOM 5.5.1 INDI-level.
    # Accetta qualsiasi forma di chiave: colonna numerica (es. '14'), chiave semantica
    # (es. 'professione'), o tag GEDCOM diretto (es. 'OCCU').
    # Valore speciale None = il campo richiede logica posizionale (BIRT/PLAC vs NATI).
    # Per aggiungere un campo da una nuova tipologia documentale: aggiungere una riga.

    # Tag GEDCOM 5.5.1 che richiedono event structure (no valore flat su stessa riga).
    _EVENT_STRUCT_TAGS = frozenset({'EMIG', 'IMMI', 'NATU', 'CENS', 'GRAD', 'RETI'})

    # Chiavi semantiche specifiche per sotto-livelli di eventi strutturati.
    # Formato: chiave_json → (tag_evento, sub_tag)  dove sub_tag in {DATE, PLAC, NOTE}
    _EVENT_SEMANTIC_KEYS = {
        'destinazione':           ('EMIG', 'PLAC'),
        'luogo_emigrazione':      ('EMIG', 'PLAC'),
        'data_emigrazione':       ('EMIG', 'DATE'),
        'luogo_immigrazione':     ('IMMI', 'PLAC'),
        'data_immigrazione':      ('IMMI', 'DATE'),
        'data_naturalizzazione':  ('NATU', 'DATE'),
        'luogo_naturalizzazione': ('NATU', 'PLAC'),
        'data_censimento':        ('CENS', 'DATE'),
        'luogo_censimento':       ('CENS', 'PLAC'),
        'data_laurea':            ('GRAD', 'DATE'),
        'luogo_laurea':           ('GRAD', 'PLAC'),
        'data_pensione':          ('RETI', 'DATE'),
        'luogo_pensione':         ('RETI', 'PLAC'),
    }

    GEDCOM_TAG_MAP = {
        # ── Chiavi numeriche (censimenti, stati delle anime) ──────────────────
        '14': 'RELI',   # Religione
        '15': None,     # Patria → 2 PLAC (se c'è BIRT) o 1 NATI (altrimenti)
        '16': 'OCCU',   # Professione
        '17': 'PROP',   # Indigenti / beni
        '18': 'EDUC',   # Istruzione
        '19': 'NOTE',   # Osservazioni
        '20': 'TITL',   # Titolo nobiliare
        '21': 'CAST',   # Casta / classe sociale
        '22': 'DSCR',   # Descrizione fisica
        '23': 'NCHI',   # Numero figli
        '24': 'IDNO',   # Numero identificativo (matricola, codice)
        '25': 'RESI',   # Residenza / domicilio
        '26': 'NMR',    # Numero matrimoni
        # ── Chiavi semantiche (atti di stato civile, catasti, altri formati) ──
        'religione':          'RELI',
        'professione':        'OCCU',
        'professione_civile': 'OCCU',
        'istruzione':         'EDUC',
        'titolo':             'TITL',
        'titolo_nobiliare':   'TITL',
        'note':               'NOTE',
        'osservazioni':       'NOTE',
        'beni':               'PROP',
        'condizione':         'PROP',
        'casta':              'CAST',
        'descrizione':        'DSCR',
        'numero_figli':       'NCHI',
        'luogo_origine':      None,   # → PLAC/NATI come '15'
        'patria':             None,   # → PLAC/NATI come '15'
        # Nuove chiavi semantiche per IDNO / RESI / NMR / SSN
        'domicilio':          'RESI',
        'residenza':          'RESI',
        'indirizzo':          'RESI',
        'matricola':          'IDNO',
        'numero_matricola':   'IDNO',
        'codice':             'IDNO',
        'numero_documento':   'IDNO',
        'numero_matrimoni':   'NMR',
        'ssn':                'SSN',
        'codice_fiscale':     'SSN',
        'destinazione':       None,   # passaporto: meta → EMIG (gestito da _EVENT_SEMANTIC_KEYS)
        'data_rilascio':      'NOTE',  # passaporto: data rilascio → nota
        'numero_fuoco':       'REFN',  # catasto: identificativo del fuoco/famiglia
        'grado':              'TITL',  # militare/nobiltà: grado o rango formale
        'campagne':           '_MILT', # militare: campagne di guerra
        'stato_civile':       'NOTE',  # celibe, coniugato, vedovo, ecc. → NOTE (nessun tag GEDCOM 5.5.1 standard)
        # ── Personal name structure (GEDCOM 5.5.1 — level 2 sotto NAME) ──────────
        'soprannome':   'NICK',   # soprannome / alias
        'alias':        'NICK',
        'prefisso_nome':'NPFX',   # Don, Fra', Rev., Ser, ecc.
        'suffisso_nome':'NSFX',   # fu, q., jr, sr, ecc.
        # ── Tag GEDCOM diretti (pass-through: chi chiama può già usare il tag) ─
        'RELI': 'RELI', 'OCCU': 'OCCU', 'EDUC': 'EDUC', 'NOTE': 'NOTE',
        'TITL': 'TITL', 'PROP': 'PROP', 'CAST': 'CAST', 'DSCR': 'DSCR',
        'NCHI': 'NCHI', 'IDNO': 'IDNO', 'RESI': 'RESI', 'NMR':  'NMR',
        'SSN':  'SSN',  'NATI': 'NATI', 'NATU': 'NATU', 'EMIG': 'EMIG',
        'IMMI': 'IMMI', 'CENS': 'CENS', 'PROB': 'PROB', 'WILL': 'WILL',
        'GRAD': 'GRAD', 'RETI': 'RETI', 'BAPL': 'BAPL', 'CONL': 'CONL',
        'ENDL': 'ENDL', 'SLGC': 'SLGC', 'AFN':  'AFN',  'REFN': 'REFN',
        'NICK': 'NICK', 'NPFX': 'NPFX', 'NSFX': 'NSFX',
        # Enriched accettati da GEDCOM 5.5.1 (tag non-standard ma ampiamente supportati):
        '_MILT': '_MILT',   # Servizio militare
        '_DNA':  '_DNA',    # Profilo genetico
        '_MDCL': '_MDCL',   # Informazioni mediche
    }

    def __init__(self, source_system="ATK-Pro"):
        self.source_system = source_system
        self.individuals = [] # (iid, lines)
        self.unified_records = []
        self.families = []
        self.sources = []
        self.indi_count = 0
        self.fam_count = 0
        self.sour_count = 0
        self.curr_source_url  = ""
        self.curr_page_label  = ""
        self.curr_source_id   = None  # impostato da _ensure_canvas_sour on-demand
        self.last_record_casa = ""
        self.last_record_famiglia = ""
        self.last_record_cognome = ""
        self.curr_comunita = ""
        self.curr_parrocchia = ""
        self.curr_anno = ""
        self.curr_canvas_image = ""  # percorso locale dell'immagine canvas corrente → OBJE

    def _sanitize_value(self, val):
        if val is None: return ""
        if isinstance(val, (dict, list)): return "[PULIZIA]"
        v = str(val).split("\n")[0].split("\r")[0].strip()
        if v.upper() in ["NONE", "NULL", "N/A", "UNKNOWN"]: return ""
        # Sincro v40.1: Rimozione totale di virgolette e semicolon per integrità Excel
        v = v.replace('"', '').replace("'", "").replace(";", ",")
        # Rimuovi marcatori di incertezza OCR come [?] mantenendo il valore base
        import re as _re
        v_clean = _re.sub(r'\s*\[\?+\]\s*', '', v).strip()
        if v_clean:
            v = v_clean
        if any(c in v for c in "{}[]"): return "[PULIZIA]"
        return v

    def _format_date(self, d):
        if not d: return ""
        d = d.lower().strip()
        for it, en in self.MONTH_MAP.items(): d = d.replace(it, en)
        return d.upper()

    def load_existing_gedcom(self, path):
        try:
            if not os.path.exists(path): return
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Carichiamo solo il conteggio per evitare duplicati ID
                ids = re.findall(r'0 (@I(\d+)@) INDI', content)
                for _, num in ids:
                    if int(num) > self.indi_count: self.indi_count = int(num)
        except: pass

    def load_existing_csv(self, path):
        try:
            if not os.path.exists(path): return
            with open(path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    if row.get('ID_Persona'):
                        # Manteniamo traccia degli ultimi valori per la propagazione
                        if row.get('Casa_Nr'): self.last_record_casa = row['Casa_Nr']
                        if row.get('Famiglia_Nr'): self.last_record_famiglia = row['Famiglia_Nr']
                        if row.get('Cognome'): self.last_record_cognome = row['Cognome']
        except: pass

    def parse_user_notes_metadata(self, notes):
        if not notes: return
        c = re.search(r'Comunit[àa][:\s]+(.*?)(?:[,;\n]|$)', notes, re.I)
        p = re.search(r'Parrocchia[:\s]+(.*?)(?:[,;\n]|$)', notes, re.I)
        a = re.search(r'Anno[:\s]+(\d{4})', notes, re.I)
        if c: self.curr_comunita = c.group(1).strip()
        if p: self.curr_parrocchia = p.group(1).strip()
        if a: self.curr_anno = a.group(1).strip()
    def set_canvas_source(self, url, page_label=None):
        """Registra la sorgente IIIF del canvas corrente (deferred: il record SOUR
        viene creato on-demand alla prima aggiunta INDI, per includere anche i
        metadati estratti dall'AI come parrocchia/anno)."""
        self.curr_source_url = url or ""
        self.curr_page_label = page_label or ""
        self.curr_source_id  = None  # reset: SOUR verra' creato al momento giusto

    def set_canvas_image(self, path):
        """Registra il percorso dell'immagine sorgente del canvas corrente → OBJE."""
        self.curr_canvas_image = path or ""

    def _collect_and_write_event_structs(self, lines, data, written_tags):
        """Raccoglie campi semantici che alimentano eventi strutturati GEDCOM 5.5.1
        (EMIG, IMMI, NATU, CENS, GRAD, RETI) e li scrive con la corretta gerarchia
        livello-1 / livello-2 invece del formato flat non-conforme."""
        parts = {}  # tag → {'DATE': str, 'PLAC': str}

        for key, raw_val in data.items():
            k = str(key).strip()
            val = self._sanitize_value(raw_val)
            if not val:
                continue
            # Chiavi semantiche esplicite (data_emigrazione, luogo_emigrazione, ecc.)
            mapping = self._EVENT_SEMANTIC_KEYS.get(k)
            if mapping:
                tag, sub = mapping
                if tag not in parts:
                    parts[tag] = {}
                if sub not in parts[tag]:
                    parts[tag][sub] = self._format_date(val) if sub == 'DATE' else val
                continue
            # Pass-through diretto del tag (es. chiave 'EMIG' con valore "Roma 1895"):
            # prova a dedurre se è data o luogo.
            tag_direct = self.GEDCOM_TAG_MAP.get(k)
            if tag_direct in self._EVENT_STRUCT_TAGS and k not in self._EVENT_SEMANTIC_KEYS:
                if tag_direct not in parts:
                    parts[tag_direct] = {}
                fmt = self._format_date(val)
                if fmt and 'DATE' not in parts[tag_direct]:
                    parts[tag_direct]['DATE'] = fmt
                elif not fmt and 'PLAC' not in parts[tag_direct]:
                    parts[tag_direct]['PLAC'] = val

        # Scrittura in ordine canonico
        for tag in ('EMIG', 'IMMI', 'NATU', 'CENS', 'GRAD', 'RETI'):
            if tag in written_tags or tag not in parts:
                continue
            lines.append(f"1 {tag}")
            p = parts[tag]
            if 'DATE' in p: lines.append(f"2 DATE {p['DATE']}")
            if 'PLAC' in p: lines.append(f"2 PLAC {p['PLAC']}")
            written_tags.add(tag)

    def _build_name_lines(self, first, last, npfx="", nsfx="", nick=""):
        """Costruisce le righe GEDCOM 5.5.1 per la struttura PERSONAL_NAME.
        Ritorna una lista di stringhe (livello 1 NAME + eventuali level-2 sub-tag)."""
        # Componi il valore del tag NAME (human-readable, standard 5.5.1)
        given = f"{npfx} {first}".strip() if npfx else first
        if last:
            full = f"{given} /{last}/"
            if nsfx: full += f" {nsfx}"
        else:
            full = given
            if nsfx: full += f" {nsfx}"
        lines = [f"1 NAME {full}"]
        # Substructure machine-readable (GEDCOM 5.5.1 §55)
        if npfx:  lines.append(f"2 NPFX {npfx}")
        if first: lines.append(f"2 GIVN {first}")
        if last:  lines.append(f"2 SURN {last}")
        if nsfx:  lines.append(f"2 NSFX {nsfx}")
        if nick:  lines.append(f"2 NICK {nick}")
        return lines

    def _ensure_canvas_sour(self):
        """Crea il record SOUR del canvas corrente se non esiste ancora.
        Ritorna l'ID SOUR (@Sx@) oppure None se non ci sono informazioni utili."""
        if self.curr_source_id:
            return self.curr_source_id
        if not self.curr_source_url and not self.curr_parrocchia and not self.curr_comunita:
            return None
        self.sour_count += 1
        sid = f"@S{self.sour_count}@"
        # TITL: descrizione archivistica del documento, non l'istituzione ecclesiastica.
        # Per registri parrocchiali: "Parrocchia X - Comunità Y"
        # Per atti civili/catasto/militari con solo comunità: "Archivi - Comunità Y"
        # Fallback assoluto: etichetta generica del portale.
        # L'URL Antenati va in _LINK, non nel titolo.
        if self.curr_parrocchia and self.curr_comunita:
            titl = f"{self.curr_parrocchia} - {self.curr_comunita}"
        elif self.curr_parrocchia:
            titl = self.curr_parrocchia
        elif self.curr_comunita:
            titl = f"Archivi - {self.curr_comunita}"
        else:
            titl = "Portale Antenati - Archivi di Stato"
        lines = [
            f"0 {sid} SOUR",
            f"1 TITL {titl}",
            "1 AUTH Archivi di Stato italiani - Portale Antenati",
        ]
        if self.curr_anno:
            lines.append(f"1 DATE {self.curr_anno}")
        note_parts = []
        if self.curr_comunita:   note_parts.append(f"Comunit\u00e0: {self.curr_comunita}")
        if self.curr_parrocchia: note_parts.append(f"Parrocchia: {self.curr_parrocchia}")
        if note_parts:
            lines.append(f"1 NOTE {' | '.join(note_parts)}")
        if self.curr_source_url:
            lines.append(f"1 _LINK {self.curr_source_url}")
        self.sources.append("\n".join(lines))
        self.curr_source_id = sid
        return sid
    def add_individual(self, first, last, sex="U", original_fields=None):
        if not first and not last: return None
        self.indi_count += 1
        iid = f"@I{self.indi_count}@"
        npfx = self._sanitize_value(original_fields.get('prefisso_nome', '')) if original_fields else ''
        nsfx = self._sanitize_value(original_fields.get('suffisso_nome', '')) if original_fields else ''
        nick = self._sanitize_value(original_fields.get('soprannome', original_fields.get('alias', ''))) if original_fields else ''
        lines = [f"0 {iid} INDI"] + self._build_name_lines(first, last, npfx, nsfx, nick) + [f"1 SEX {sex}"]
        
        birth_year = ""
        if original_fields and self.curr_anno:
            eta_raw = str(original_fields.get('6', '')).strip()
            if eta_raw.isdigit() and self.curr_anno.isdigit():
                birth_year = "CAL " + str(int(self.curr_anno) - int(eta_raw))
                lines.append("1 BIRT")
                lines.append(f"2 DATE {birth_year}")
                patria = self._sanitize_value(original_fields.get('15', '')) if original_fields else ''
                if patria and patria not in ('"', '""'):
                    lines.append(f"2 PLAC {patria}")

        if original_fields:
            written_tags = set()  # evita duplicati se più chiavi mappano allo stesso tag
            # Chiavi strutturali già gestite sopra — non rielaborare
            _skip = {'1','2','3','4','5','6','7','8','9','10','11','12','13'}
            # Step 1: eventi strutturati (EMIG/IMMI/NATU/CENS/GRAD/RETI) → GEDCOM 5.5.1 event block
            self._collect_and_write_event_structs(lines, original_fields, written_tags)
            for key, raw_val in original_fields.items():
                k = str(key).strip()
                if k in _skip:
                    continue
                val = self._sanitize_value(raw_val)
                if not val:
                    continue
                tag = self.GEDCOM_TAG_MAP.get(k)
                # Salta: già in written_tags, eventi strutturati (già scritti sopra), o None-special
                if tag in self._EVENT_STRUCT_TAGS:
                    continue
                if tag is None and k in self.GEDCOM_TAG_MAP:
                    # Gestione speciale: Patria/luogo_origine → PLAC/NATI
                    if not birth_year:
                        if 'NATI' not in written_tags:
                            lines.append(f"1 NATI {val}")
                            written_tags.add('NATI')
                    # Se birth_year esiste è già in 2 PLAC sotto BIRT
                elif tag and tag not in written_tags:
                    lines.append(f"1 {tag} {val}")
                    written_tags.add(tag)

        # Citazione fonte: collega ogni INDI al record SOUR del canvas
        sour_id = self._ensure_canvas_sour()
        if sour_id:
            lines.append(f"1 SOUR {sour_id}")
            if self.curr_page_label:
                lines.append(f"2 PAGE {self.curr_page_label}")
            lines.append("2 QUAY 3")
        # Collegamento immagine sorgente (GEDCOM 5.5.1 OBJE)
        if self.curr_canvas_image:
            import os as _os
            lines.append("1 OBJE")
            lines.append(f"2 FILE {self.curr_canvas_image}")
            lines.append(f"2 FORM {_os.path.splitext(self.curr_canvas_image)[1].lstrip('.').lower() or 'jpeg'}")
            if self.curr_page_label:
                lines.append(f"2 TITL {self.curr_page_label}")

        self.individuals.append((iid, lines))
        rec = {'ID': iid, 'COGNOME': last, 'NOME': first, 'SESSO': sex, 'DATA_NASCITA': birth_year, 'LUOGO_NASCITA': original_fields.get('15', '') if original_fields else ''}
        for i in range(1, 20): rec[str(i)] = original_fields.get(str(i), "") if original_fields else ""
        self.unified_records.append(rec)
        return iid

    def add_family(self, h, w, children=None):
        self.fam_count += 1
        fid = f"@F{self.fam_count}@"
        lines = [f"0 {fid} FAM"]
        if h: lines.append(f"1 HUSB {h}")
        if w: lines.append(f"1 WIFE {w}")
        if children:
            for c in children: lines.append(f"1 CHIL {c}")
        self.families.append((fid, lines))
        return fid

    # ──────────────────────────────────────────────────────────────────────────
    # HELPER: aggiunge un individuo da dati semantici ricchi (stato civile, militare)
    # ──────────────────────────────────────────────────────────────────────────

    def _add_individual_civil(self, first, last, sex, data, events=None):
        """Aggiunge un INDI GEDCOM da un dizionario semantico ricco."""
        if not first and not last:
            return None
        self.indi_count += 1
        iid = f"@I{self.indi_count}@"
        sex_tag = sex.upper() if sex.upper() in ('M', 'F') else 'U'
        npfx = self._sanitize_value(data.get('prefisso_nome', ''))
        nsfx = self._sanitize_value(data.get('suffisso_nome', ''))
        nick = self._sanitize_value(data.get('soprannome', data.get('alias', '')))
        lines = [f"0 {iid} INDI"] + self._build_name_lines(first, last, npfx, nsfx, nick) + [f"1 SEX {sex_tag}"]
        if events:
            lines.extend(events)
        # Se non c'è già BIRT negli eventi, stima anno di nascita dall'età
        has_birt = any('1 BIRT' in e for e in (events or []))
        if not has_birt:
            eta = str(data.get('eta', '')).strip()
            if eta.isdigit() and self.curr_anno and self.curr_anno.isdigit():
                lines.append("1 BIRT")
                lines.append(f"2 DATE CAL {int(self.curr_anno) - int(eta)}")
        # Usa GEDCOM_TAG_MAP per scrivere tutti i campi semantici standard
        # NICK/NPFX/NSFX già scritti in _build_name_lines: escludi dal loop flat
        _name_tags = {'NICK', 'NPFX', 'NSFX', 'GIVN', 'SURN'}
        written_tags = set(_name_tags)
        # Step 1: eventi strutturati (EMIG/IMMI/NATU/CENS/GRAD/RETI) → GEDCOM 5.5.1 event block
        self._collect_and_write_event_structs(lines, data, written_tags)
        for key, raw_val in data.items():
            k = str(key).strip()
            val = self._sanitize_value(raw_val)
            if not val:
                continue
            tag = self.GEDCOM_TAG_MAP.get(k)
            # Salta tag evento (già gestiti) e tag nome (già in _build_name_lines)
            if tag in self._EVENT_STRUCT_TAGS:
                continue
            if tag and tag not in written_tags:
                lines.append(f"1 {tag} {val}")
                written_tags.add(tag)
        rec = {
            'ID': iid, 'COGNOME': last, 'NOME': first, 'SESSO': sex_tag,
            'DATA_NASCITA': self._sanitize_value(data.get('data_nascita', '')),
            'LUOGO_NASCITA': self._sanitize_value(data.get('luogo_nascita', '')),
        }
        for i in range(1, 20):
            rec[str(i)] = ''
        rec['4'] = last
        rec['5'] = first
        rec['16'] = self._sanitize_value(data.get('professione', data.get('professione_civile', '')))
        # Citazione fonte: collega ogni INDI al record SOUR del canvas
        sour_id = self._ensure_canvas_sour()
        if sour_id:
            lines.append(f"1 SOUR {sour_id}")
            if self.curr_page_label:
                lines.append(f"2 PAGE {self.curr_page_label}")
            lines.append("2 QUAY 3")
        # Collegamento immagine sorgente (GEDCOM 5.5.1 OBJE)
        if self.curr_canvas_image:
            import os as _os
            lines.append("1 OBJE")
            lines.append(f"2 FILE {self.curr_canvas_image}")
            lines.append(f"2 FORM {_os.path.splitext(self.curr_canvas_image)[1].lstrip('.').lower() or 'jpeg'}")
            if self.curr_page_label:
                lines.append(f"2 TITL {self.curr_page_label}")
        self.individuals.append((iid, lines))
        self.unified_records.append(rec)
        return iid

    # ──────────────────────────────────────────────────────────────────────────
    # HANDLER: atti di stato civile e militare (formato "atti")
    # ──────────────────────────────────────────────────────────────────────────

    def _process_atti(self, atti):
        """Dispatcher per il formato semantico 'atti'."""
        for atto in atti:
            tipo = str(atto.get('tipo', 'generico')).lower()
            if tipo in ('nascita', 'battesimo'):
                self._process_nascita_atto(atto)
            elif tipo == 'matrimonio':
                self._process_matrimonio_atto(atto)
            elif tipo in ('morte', 'sepoltura'):
                self._process_morte_atto(atto)
            elif tipo == 'militare':
                self._process_militare_atto(atto)
            elif tipo in ('cresima', 'confermazione'):
                self._process_cresima_atto(atto)
            elif tipo in ('comunione', 'prima_comunione'):
                self._process_comunione_atto(atto)
            elif tipo == 'adozione':
                self._process_adozione_atto(atto)
            elif tipo in ('ordinazione', 'sacerdozio'):
                self._process_ordinazione_atto(atto)
            else:
                sogg = atto.get('soggetto', atto)
                self._add_individual_civil(
                    self._sanitize_value(sogg.get('nome', '')),
                    self._sanitize_value(sogg.get('cognome', '')),
                    self._sanitize_value(sogg.get('sesso', 'U')),
                    sogg,
                )
        return True

    def _process_nascita_atto(self, atto):
        """Processa un atto di nascita/battesimo."""
        nr = self._sanitize_value(atto.get('numero_atto', ''))
        note_atto = self._sanitize_value(atto.get('note', ''))
        sogg = atto.get('soggetto', {})
        padre = atto.get('padre', {})
        madre = atto.get('madre', {})

        data_n = self._format_date(sogg.get('data_nascita', ''))
        luogo_n = self._sanitize_value(sogg.get('luogo_nascita', ''))
        ora_n = self._sanitize_value(sogg.get('ora_nascita', ''))
        birt_events = []
        if data_n or luogo_n:
            birt_events.append("1 BIRT")
            if data_n:   birt_events.append(f"2 DATE {data_n}")
            if luogo_n:  birt_events.append(f"2 PLAC {luogo_n}")
            if ora_n:    birt_events.append(f"2 NOTE Ora: {ora_n}")
        if nr:
            birt_events.append(f"1 EVEN Atto nr. {nr}")
            birt_events.append("2 TYPE Nascita")
        if note_atto:
            birt_events.append(f"1 NOTE {note_atto}")
        # Battesimo → CHR (aggiuntivo rispetto a BIRT)
        data_batt = self._format_date(sogg.get('data_battesimo', ''))
        luogo_batt = self._sanitize_value(sogg.get('luogo_battesimo', ''))
        if data_batt or luogo_batt:
            birt_events.append("1 CHR")
            if data_batt:  birt_events.append(f"2 DATE {data_batt}")
            if luogo_batt: birt_events.append(f"2 PLAC {luogo_batt}")

        iid_s = self._add_individual_civil(
            self._sanitize_value(sogg.get('nome', '')),
            self._sanitize_value(sogg.get('cognome', '')),
            self._sanitize_value(sogg.get('sesso', 'U')),
            sogg, birt_events,
        )

        p_ev = []
        if padre.get('fu', False):
            p_ev += ["1 DEAT", "2 NOTE defunto al momento dell'atto"]
        iid_p = self._add_individual_civil(
            self._sanitize_value(padre.get('nome', '')),
            self._sanitize_value(padre.get('cognome', '')),
            'M', padre, p_ev,
        ) if (padre.get('nome') or padre.get('cognome')) else None

        iid_m = self._add_individual_civil(
            self._sanitize_value(madre.get('nome', '')),
            self._sanitize_value(madre.get('cognome_nubile', madre.get('cognome', ''))),
            'F', madre,
        ) if (madre.get('nome') or madre.get('cognome_nubile') or madre.get('cognome')) else None

        if iid_p or iid_m:
            self.add_family(iid_p, iid_m, [iid_s] if iid_s else None)

        # Testimoni: INDI autonomi senza legami familiari
        for t in atto.get('testimoni', []):
            self._add_individual_civil(
                self._sanitize_value(t.get('nome', '')),
                self._sanitize_value(t.get('cognome', '')),
                'U', t,
            )

    def _process_matrimonio_atto(self, atto):
        """Processa un atto di matrimonio."""
        nr = self._sanitize_value(atto.get('numero_atto', ''))
        note_atto = self._sanitize_value(atto.get('note', ''))
        data_m = self._format_date(atto.get('data_matrimonio', ''))
        luogo_m = self._sanitize_value(atto.get('luogo_matrimonio', ''))
        sposo = atto.get('sposo', {})
        sposa = atto.get('sposa', {})

        marr_events = []
        if data_m or luogo_m:
            marr_events.append("1 MARR")
            if data_m:  marr_events.append(f"2 DATE {data_m}")
            if luogo_m: marr_events.append(f"2 PLAC {luogo_m}")
        if nr:
            marr_events.append(f"1 EVEN Atto nr. {nr}")
            marr_events.append("2 TYPE Matrimonio")
        if note_atto:
            marr_events.append(f"1 NOTE {note_atto}")

        iid_sposo = self._add_individual_civil(
            self._sanitize_value(sposo.get('nome', '')),
            self._sanitize_value(sposo.get('cognome', '')),
            'M', sposo, marr_events,
        ) if (sposo.get('nome') or sposo.get('cognome')) else None

        iid_sposa = self._add_individual_civil(
            self._sanitize_value(sposa.get('nome', '')),
            self._sanitize_value(sposa.get('cognome', '')),
            'F', sposa,
        ) if (sposa.get('nome') or sposa.get('cognome')) else None

        if iid_sposo or iid_sposa:
            self.add_family(iid_sposo, iid_sposa)

        # Genitori sposo
        fp1 = self._sanitize_value(sposo.get('padre_nome', ''))
        fl1 = self._sanitize_value(sposo.get('padre_cognome', ''))
        fm1 = self._sanitize_value(sposo.get('madre_nome', ''))
        fml1 = self._sanitize_value(sposo.get('madre_cognome', ''))
        if fp1 or fl1 or fm1 or fml1:
            p_ev = (["1 DEAT", "2 NOTE defunto al momento dell'atto"] if sposo.get('padre_fu') else [])
            iid_fp1 = self._add_individual_civil(fp1, fl1, 'M', {}, p_ev) if (fp1 or fl1) else None
            iid_fm1 = self._add_individual_civil(fm1, fml1, 'F', {}) if (fm1 or fml1) else None
            self.add_family(iid_fp1, iid_fm1, [iid_sposo] if iid_sposo else None)

        # Genitori sposa
        fp2 = self._sanitize_value(sposa.get('padre_nome', ''))
        fl2 = self._sanitize_value(sposa.get('padre_cognome', ''))
        fm2 = self._sanitize_value(sposa.get('madre_nome', ''))
        fml2 = self._sanitize_value(sposa.get('madre_cognome', ''))
        if fp2 or fl2 or fm2 or fml2:
            p_ev2 = (["1 DEAT", "2 NOTE defunta al momento dell'atto"] if sposa.get('padre_fu') else [])
            iid_fp2 = self._add_individual_civil(fp2, fl2, 'M', {}, p_ev2) if (fp2 or fl2) else None
            iid_fm2 = self._add_individual_civil(fm2, fml2, 'F', {}) if (fm2 or fml2) else None
            self.add_family(iid_fp2, iid_fm2, [iid_sposa] if iid_sposa else None)

        # Testimoni: INDI autonomi senza legami familiari
        for t in atto.get('testimoni', []):
            self._add_individual_civil(
                self._sanitize_value(t.get('nome', '')),
                self._sanitize_value(t.get('cognome', '')),
                'U', t,
            )

    def _process_morte_atto(self, atto):
        """Processa un atto di morte/sepoltura."""
        nr = self._sanitize_value(atto.get('numero_atto', ''))
        note_atto = self._sanitize_value(atto.get('note', ''))
        def_d = atto.get('defunto', {})
        data_m = self._format_date(def_d.get('data_morte', ''))
        luogo_m = self._sanitize_value(def_d.get('luogo_morte', ''))
        causa = self._sanitize_value(def_d.get('causa_morte', ''))
        sex_d = self._sanitize_value(def_d.get('sesso', 'U'))

        deat_events = []
        if data_m or luogo_m:
            deat_events.append("1 DEAT")
            if data_m:  deat_events.append(f"2 DATE {data_m}")
            if luogo_m: deat_events.append(f"2 PLAC {luogo_m}")
            if causa:   deat_events.append(f"2 CAUS {causa}")
            ora_m = self._sanitize_value(def_d.get('ora_morte', ''))
            if ora_m:   deat_events.append(f"2 NOTE Ora: {ora_m}")
        if nr:
            deat_events.append(f"1 EVEN Atto nr. {nr}")
            deat_events.append("2 TYPE Morte")
        if note_atto:
            deat_events.append(f"1 NOTE {note_atto}")
        # Sepoltura/Cremazione → BURI / CREM
        data_sep = self._format_date(def_d.get('data_sepoltura', ''))
        luogo_sep = self._sanitize_value(def_d.get('luogo_sepoltura', ''))
        tipo_sep = self._sanitize_value(def_d.get('tipo_sepoltura', '')).lower()
        if data_sep or luogo_sep:
            tag_sep = "1 CREM" if tipo_sep == 'cremazione' else "1 BURI"
            deat_events.append(tag_sep)
            if data_sep:  deat_events.append(f"2 DATE {data_sep}")
            if luogo_sep: deat_events.append(f"2 PLAC {luogo_sep}")

        iid_d = self._add_individual_civil(
            self._sanitize_value(def_d.get('nome', '')),
            self._sanitize_value(def_d.get('cognome', '')),
            sex_d, def_d, deat_events,
        ) if (def_d.get('nome') or def_d.get('cognome')) else None

        # Genitori
        fp = self._sanitize_value(def_d.get('padre_nome', ''))
        fl = self._sanitize_value(def_d.get('padre_cognome', ''))
        fm = self._sanitize_value(def_d.get('madre_nome', ''))
        fml = self._sanitize_value(def_d.get('madre_cognome', ''))
        if fp or fl or fm or fml:
            p_ev = (["1 DEAT", "2 NOTE defunto al momento dell'atto"] if def_d.get('padre_fu') else [])
            m_ev = (["1 DEAT", "2 NOTE defunta al momento dell'atto"] if def_d.get('madre_fu') else [])
            iid_fp = self._add_individual_civil(fp, fl, 'M', {}, p_ev) if (fp or fl) else None
            iid_fm = self._add_individual_civil(fm, fml, 'F', {}, m_ev) if (fm or fml) else None
            self.add_family(iid_fp, iid_fm, [iid_d] if iid_d else None)

        # Coniuge superstite
        cn = self._sanitize_value(def_d.get('coniuge_nome', ''))
        cl = self._sanitize_value(def_d.get('coniuge_cognome', ''))
        if cn or cl:
            con_sex = 'F' if sex_d == 'M' else 'M'
            iid_con = self._add_individual_civil(cn, cl, con_sex, {})
            if iid_d:
                if sex_d == 'M':
                    self.add_family(iid_d, iid_con)
                else:
                    self.add_family(iid_con, iid_d)

        # Dichiaranti: INDI autonomi senza legami familiari
        for d in atto.get('dichiaranti', []):
            self._add_individual_civil(
                self._sanitize_value(d.get('nome', '')),
                self._sanitize_value(d.get('cognome', '')),
                'U', d,
            )

    def _process_militare_atto(self, atto):
        """Processa un record militare (foglio matricolare o ruolo di leva)."""
        data_n = self._format_date(atto.get('data_nascita', ''))
        luogo_n = self._sanitize_value(atto.get('luogo_nascita', ''))
        data_arr = self._format_date(atto.get('data_arruolamento', ''))
        data_cong = self._format_date(atto.get('data_congedo', ''))
        grado = self._sanitize_value(atto.get('grado', ''))
        corpo = self._sanitize_value(atto.get('corpo', ''))
        arma = self._sanitize_value(atto.get('arma', ''))
        ferite = self._sanitize_value(atto.get('ferite', ''))
        decorazioni = self._sanitize_value(atto.get('decorazioni', ''))
        causa_cong = self._sanitize_value(atto.get('causa_congedo', ''))

        events = []
        if data_n or luogo_n:
            events.append("1 BIRT")
            if data_n:  events.append(f"2 DATE {data_n}")
            if luogo_n: events.append(f"2 PLAC {luogo_n}")
        if data_arr:
            events.append("1 EVEN Arruolamento")
            events.append("2 TYPE Military Service")
            events.append(f"2 DATE {data_arr}")
            if grado:   events.append(f"2 NOTE Grado: {grado}")
            if corpo:   events.append(f"2 AGNC {corpo}")
            if arma:    events.append(f"2 NOTE Arma: {arma}")
        if data_cong:
            events.append("1 EVEN Congedo")
            events.append("2 TYPE Military Discharge")
            events.append(f"2 DATE {data_cong}")
            if causa_cong: events.append(f"2 NOTE {causa_cong}")
        if ferite:      events.append(f"1 NOTE Ferite: {ferite}")
        if decorazioni: events.append(f"1 NOTE Decorazioni: {decorazioni}")

        iid = self._add_individual_civil(
            self._sanitize_value(atto.get('nome', '')),
            self._sanitize_value(atto.get('cognome', '')),
            'M', atto, events,
        ) if (atto.get('nome') or atto.get('cognome')) else None

        fp = self._sanitize_value(atto.get('padre_nome', ''))
        fl = self._sanitize_value(atto.get('padre_cognome', ''))
        fm = self._sanitize_value(atto.get('madre_nome', ''))
        fml = self._sanitize_value(atto.get('madre_cognome', ''))
        if fp or fl or fm or fml:
            iid_fp = self._add_individual_civil(fp, fl, 'M', {}) if (fp or fl) else None
            iid_fm = self._add_individual_civil(fm, fml, 'F', {}) if (fm or fml) else None
            self.add_family(iid_fp, iid_fm, [iid] if iid else None)

    def _process_cresima_atto(self, atto):
        """Processa un atto di cresima/confermazione → CONF."""
        nr = self._sanitize_value(atto.get('numero_atto', ''))
        note_atto = self._sanitize_value(atto.get('note', ''))
        sogg = atto.get('soggetto', {})
        padre = atto.get('padre', {})
        madre = atto.get('madre', {})
        data_c = self._format_date(atto.get('data_cresima', ''))
        luogo_c = self._sanitize_value(atto.get('luogo_cresima', ''))
        vescovo = self._sanitize_value(atto.get('vescovo', ''))

        conf_events = ["1 CONF"]
        if data_c:    conf_events.append(f"2 DATE {data_c}")
        if luogo_c:   conf_events.append(f"2 PLAC {luogo_c}")
        if vescovo:   conf_events.append(f"2 NOTE Vescovo: {vescovo}")
        if nr:
            conf_events += [f"1 EVEN Atto nr. {nr}", "2 TYPE Cresima"]
        if note_atto: conf_events.append(f"1 NOTE {note_atto}")

        iid_s = self._add_individual_civil(
            self._sanitize_value(sogg.get('nome', '')),
            self._sanitize_value(sogg.get('cognome', '')),
            self._sanitize_value(sogg.get('sesso', 'U')),
            sogg, conf_events,
        ) if (sogg.get('nome') or sogg.get('cognome')) else None

        iid_p = self._add_individual_civil(
            self._sanitize_value(padre.get('nome', '')),
            self._sanitize_value(padre.get('cognome', '')),
            'M', padre,
        ) if (padre.get('nome') or padre.get('cognome')) else None
        iid_m = self._add_individual_civil(
            self._sanitize_value(madre.get('nome', '')),
            self._sanitize_value(madre.get('cognome_nubile', madre.get('cognome', ''))),
            'F', madre,
        ) if (madre.get('nome') or madre.get('cognome_nubile') or madre.get('cognome')) else None
        if iid_p or iid_m:
            self.add_family(iid_p, iid_m, [iid_s] if iid_s else None)

        padrino = atto.get('padrino', {})
        if padrino.get('nome') or padrino.get('cognome'):
            self._add_individual_civil(
                self._sanitize_value(padrino.get('nome', '')),
                self._sanitize_value(padrino.get('cognome', '')),
                'U', padrino,
            )

    def _process_comunione_atto(self, atto):
        """Processa un atto di prima comunione → FCOM."""
        nr = self._sanitize_value(atto.get('numero_atto', ''))
        note_atto = self._sanitize_value(atto.get('note', ''))
        sogg = atto.get('soggetto', {})
        padre = atto.get('padre', {})
        madre = atto.get('madre', {})
        data_c = self._format_date(atto.get('data_comunione', ''))
        luogo_c = self._sanitize_value(atto.get('luogo_comunione', ''))

        fcom_events = ["1 FCOM"]
        if data_c:    fcom_events.append(f"2 DATE {data_c}")
        if luogo_c:   fcom_events.append(f"2 PLAC {luogo_c}")
        if nr:
            fcom_events += [f"1 EVEN Atto nr. {nr}", "2 TYPE Prima Comunione"]
        if note_atto: fcom_events.append(f"1 NOTE {note_atto}")

        iid_s = self._add_individual_civil(
            self._sanitize_value(sogg.get('nome', '')),
            self._sanitize_value(sogg.get('cognome', '')),
            self._sanitize_value(sogg.get('sesso', 'U')),
            sogg, fcom_events,
        ) if (sogg.get('nome') or sogg.get('cognome')) else None

        iid_p = self._add_individual_civil(
            self._sanitize_value(padre.get('nome', '')),
            self._sanitize_value(padre.get('cognome', '')),
            'M', padre,
        ) if (padre.get('nome') or padre.get('cognome')) else None
        iid_m = self._add_individual_civil(
            self._sanitize_value(madre.get('nome', '')),
            self._sanitize_value(madre.get('cognome_nubile', madre.get('cognome', ''))),
            'F', madre,
        ) if (madre.get('nome') or madre.get('cognome_nubile') or madre.get('cognome')) else None
        if iid_p or iid_m:
            self.add_family(iid_p, iid_m, [iid_s] if iid_s else None)

    def _process_adozione_atto(self, atto):
        """Processa un atto di adozione → ADOP."""
        nr = self._sanitize_value(atto.get('numero_atto', ''))
        note_atto = self._sanitize_value(atto.get('note', ''))
        adottato = atto.get('adottato', {})
        p_adott = atto.get('padre_adottivo', {})
        m_adott = atto.get('madre_adottiva', {})
        p_biol  = atto.get('padre_biologico', {})
        m_biol  = atto.get('madre_biologica', {})
        data_a  = self._format_date(atto.get('data_adozione', ''))
        luogo_a = self._sanitize_value(atto.get('luogo_adozione', ''))

        adop_events = ["1 ADOP"]
        if data_a:    adop_events.append(f"2 DATE {data_a}")
        if luogo_a:   adop_events.append(f"2 PLAC {luogo_a}")
        adop_events.append("2 FAMC @UNKNOWN@")  # placeholder aggiornato da software GEDCOM
        if nr:
            adop_events += [f"1 EVEN Atto nr. {nr}", "2 TYPE Adozione"]
        if note_atto: adop_events.append(f"1 NOTE {note_atto}")

        iid_a = self._add_individual_civil(
            self._sanitize_value(adottato.get('nome', '')),
            self._sanitize_value(adottato.get('cognome', '')),
            self._sanitize_value(adottato.get('sesso', 'U')),
            adottato, adop_events,
        ) if (adottato.get('nome') or adottato.get('cognome')) else None

        # Famiglia adottiva
        iid_pa = self._add_individual_civil(
            self._sanitize_value(p_adott.get('nome', '')),
            self._sanitize_value(p_adott.get('cognome', '')),
            'M', p_adott,
        ) if (p_adott.get('nome') or p_adott.get('cognome')) else None
        iid_ma = self._add_individual_civil(
            self._sanitize_value(m_adott.get('nome', '')),
            self._sanitize_value(m_adott.get('cognome_nubile', m_adott.get('cognome', ''))),
            'F', m_adott,
        ) if (m_adott.get('nome') or m_adott.get('cognome_nubile') or m_adott.get('cognome')) else None
        if iid_pa or iid_ma:
            self.add_family(iid_pa, iid_ma, [iid_a] if iid_a else None)

        # Famiglia biologica (se nota)
        iid_pb = self._add_individual_civil(
            self._sanitize_value(p_biol.get('nome', '')),
            self._sanitize_value(p_biol.get('cognome', '')),
            'M', p_biol,
        ) if (p_biol.get('nome') or p_biol.get('cognome')) else None
        iid_mb = self._add_individual_civil(
            self._sanitize_value(m_biol.get('nome', '')),
            self._sanitize_value(m_biol.get('cognome_nubile', m_biol.get('cognome', ''))),
            'F', m_biol,
        ) if (m_biol.get('nome') or m_biol.get('cognome_nubile') or m_biol.get('cognome')) else None
        if iid_pb or iid_mb:
            self.add_family(iid_pb, iid_mb, [iid_a] if iid_a else None)

    def _process_ordinazione_atto(self, atto):
        """Processa un atto di ordinazione sacerdotale → ORDN."""
        nr = self._sanitize_value(atto.get('numero_atto', ''))
        note_atto = self._sanitize_value(atto.get('note', ''))
        sogg = atto.get('soggetto', {})
        padre = atto.get('padre', {})
        madre = atto.get('madre', {})
        data_o  = self._format_date(atto.get('data_ordinazione', ''))
        luogo_o = self._sanitize_value(atto.get('luogo_ordinazione', ''))
        tipo_o  = self._sanitize_value(atto.get('tipo_ordinazione', ''))
        vescovo = self._sanitize_value(atto.get('vescovo', ''))
        diocesi = self._sanitize_value(atto.get('diocesi', ''))

        ordn_events = ["1 ORDN"]
        if data_o:   ordn_events.append(f"2 DATE {data_o}")
        if luogo_o:  ordn_events.append(f"2 PLAC {luogo_o}")
        if tipo_o:   ordn_events.append(f"2 NOTE Tipo: {tipo_o}")
        if vescovo:  ordn_events.append(f"2 NOTE Vescovo: {vescovo}")
        if diocesi:  ordn_events.append(f"2 AGNC {diocesi}")
        if nr:
            ordn_events += [f"1 EVEN Atto nr. {nr}", "2 TYPE Ordinazione"]
        if note_atto: ordn_events.append(f"1 NOTE {note_atto}")

        iid_s = self._add_individual_civil(
            self._sanitize_value(sogg.get('nome', '')),
            self._sanitize_value(sogg.get('cognome', '')),
            'M', sogg, ordn_events,
        ) if (sogg.get('nome') or sogg.get('cognome')) else None

        iid_p = self._add_individual_civil(
            self._sanitize_value(padre.get('nome', '')),
            self._sanitize_value(padre.get('cognome', '')),
            'M', padre,
        ) if (padre.get('nome') or padre.get('cognome')) else None
        iid_m = self._add_individual_civil(
            self._sanitize_value(madre.get('nome', '')),
            self._sanitize_value(madre.get('cognome_nubile', madre.get('cognome', ''))),
            'F', madre,
        ) if (madre.get('nome') or madre.get('cognome_nubile') or madre.get('cognome')) else None
        if iid_p or iid_m:
            self.add_family(iid_p, iid_m, [iid_s] if iid_s else None)

    # ──────────────────────────────────────────────────────────────────────────
    # ENTRY POINT PRINCIPALE
    # ──────────────────────────────────────────────────────────────────────────

    def process_ai_json(self, ai_data):
        meta = ai_data.get('metadata', {})
        if meta:
            # Supporta sia chiavi lowercase (nuovo formato) che capitalizzate (vecchio formato)
            self.curr_comunita  = meta.get('comunita',  meta.get('Comunità',  self.curr_comunita))
            self.curr_parrocchia = meta.get('parrocchia', meta.get('Parrocchia', self.curr_parrocchia))
            self.curr_anno      = meta.get('anno',       meta.get('Anno',       self.curr_anno))
            # Crea il SOUR del canvas (se non gia' creato dal dialog via set_canvas_source)
            # includendo parrocchia/anno ora disponibili dall'AI response.
            self._ensure_canvas_sour()

        # Nuovo formato semantico: atti di stato civile / militari
        if 'atti' in ai_data:
            return self._process_atti(ai_data['atti'])

        righe = ai_data.get('righe', ai_data.get('records', []))
        
        # V23.0 Srotolamento Gerarchico
        if 'famiglie' in ai_data:
            righe = []
            for fam in ai_data['famiglie']:
                c_casa = str(fam.get('casa', '')).strip()
                c_fam = str(fam.get('fam', '')).strip()
                c_cogn = str(fam.get('cognome', '')).strip()
                c_beni = str(fam.get('beni', '')).strip()
                c_fuoco = str(fam.get('numero_fuoco', '')).strip()
                for i_comp, comp in enumerate(fam.get('componenti', [])):
                    comp['1'] = c_casa
                    comp['2'] = c_fam
                    comp['4'] = c_cogn
                    # beni della famiglia → PROP (col 17), se non già presenti nel componente
                    if c_beni and not comp.get('17') and not comp.get('beni'):
                        comp['17'] = c_beni
                    # numero_fuoco → REFN solo per il capofamiglia (primo componente)
                    if c_fuoco and i_comp == 0:
                        comp['numero_fuoco'] = c_fuoco
                    righe.append(comp)

        f_groups = {}; last_fam_nr = ""; last_p_nr = 0; p_ids = set()
        for riga in righe:
            orig = {}
            if isinstance(riga, dict):
                # Aliases per la V21.0 Short Semantic
                aliases = {
                    'CASA_': '1', 'FAM_': '2', 'PER_': '3', 'COGN_': '4', 'NOME_': '5', 'ETA_': '6',
                    'CM_M': '7', 'AM_M': '8', 'VM_M': '9', 'NF_F': '10', 'MF_F': '11', 'VF_F': '12',
                    'REL_': '14', 'PATR_': '15', 'PROF_': '16', 'IND_': '17', 'ISTR_': '18', 'NOTE_': '19'
                }
                for k, v in riga.items():
                    tk = str(k).strip()
                    if tk.upper() in aliases:
                        orig[aliases[tk.upper()]] = self._sanitize_value(v)
                        continue
                    for num, lab in self.TOSCANA_COLUMN_LABELS.items():
                        if lab.upper() == tk.upper() or tk == num: tk = num; break
                    orig[tk] = self._sanitize_value(v)
            elif isinstance(riga, str):
                riga = [x.strip() for x in riga.split('|')]
                
            if isinstance(riga, list):
                expected_keys = ['1','2','3','4','5','6','7','8','9','10','11','12','14','15','16','17','18','19']
                for idx, v in enumerate(riga):
                    if idx < len(expected_keys):
                        orig[expected_keys[idx]] = self._sanitize_value(v)

            p_raw = str(orig.get('3', '')).strip()
            curr_p = 0
            m = re.search(r'\d+', p_raw)
            if m: curr_p = int(m.group())
            if curr_p == 0: curr_p = last_p_nr + 1
            
            fnr = str(orig.get('2', '')).strip()
            if fnr and fnr not in ['', '"', '""'] and fnr != last_fam_nr:
                self.last_record_cognome = ""; last_fam_nr = fnr

            uid = f"{last_fam_nr}_{curr_p}"
            if uid in p_ids: continue
            p_ids.add(uid)

            if not hasattr(self, 'last_records_map'): self.last_records_map = {}
            
            def _f_universal(cid):
                v = str(orig.get(cid, '')).strip()
                # Se è un segno di ripetizione o vuoto, cerca di recuperare dal record precedente
                if v in ['', '"', '""', '//', 'id', 'idem', '\"', '”']:
                    return self.last_records_map.get(cid, "")
                # Altrimenti salva come nuovo valore di riferimento
                self.last_records_map[cid] = v
                return v

            # Colonne ereditabili: solo Casa, Famiglia, Cognome (segni grafici del compilatore)
            # Religione ('14') esclusa: il '"' non è un'affermazione semantica, la cella va lasciata vuota
            colonne_ereditabili = ['1', '2', '4']
            
            for i in range(1, 20):
                cid = str(i)
                if cid in colonne_ereditabili:
                    orig[cid] = _f_universal(cid)
                else:
                    # Per tutte le altre (Nome, Età, Spunte, Patria, Professione, ecc) NON propaghiamo!
                    # Se Gemini ha trascritto un segno di "idem", lo rimuoviamo affinché resti vuoto
                    v = str(orig.get(cid, '')).strip()
                    if v in ['"', '""', '//', 'id', 'idem', '\"', '”']:
                        orig[cid] = ""

            sex = "U"
            if any(str(orig.get(c,'')) in ['1', 'x', 'X'] for c in ['10','11','12']): sex = "F"
            elif any(str(orig.get(c,'')) in ['1', 'x', 'X'] for c in ['7','8','9']): sex = "M"

            fname, lname = str(orig.get('5', 'SCONOSCIUTO')).strip(), str(orig.get('4', '')).strip()
            iid = self.add_individual(fname, lname, sex, original_fields=orig)
            
            if fnr:
                fk = orig.get('2')
                if fk not in f_groups: f_groups[fk] = {'h': iid, 'w': None, 'c': []}
                else:
                    if sex == 'F' and not f_groups[fk]['w']: f_groups[fk]['w'] = iid
                    else: f_groups[fk]['c'].append(iid)
            last_p_nr = curr_p

        for fnr, g in f_groups.items():
            if g['h'] or g['w']: self.add_family(g['h'], g['w'], g['c'])
        return True

    def save_to_file(self, file_path):
        import logging
        logging.info(f"Salvataggio in {file_path}. Individui: {len(self.individuals)}")
        base = os.path.splitext(file_path)[0]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("0 HEAD\n1 SOUR " + self.source_system + "\n1 CHAR UTF-8\n1 GEDC\n2 VERS 5.5.1\n")
            for _, ls in self.individuals: f.write("\n".join(ls) + "\n")
            for _, ls in self.families: f.write("\n".join(ls) + "\n")
            for s in self.sources: f.write(s + "\n")
            f.write("0 TRLR\n")

        rev_p = f"{base}_REVISIONE.csv"; reg_p = f"{base}_REGISTRO_ORIGINALE.csv"
        rev_h = ['ID', 'COGNOME', 'NOME', 'SESSO', 'DATA_NASCITA', 'LUOGO_NASCITA']
        reg_h = ['Comunita', 'Parrocchia', 'Anno', 'ID_Persona']
        
        # Sincronia: escludiamo fisicamente la Colonna 13 (spazio)
        for i in range(1, 20): 
            if i == 13: continue
            reg_h.append(self.TOSCANA_COLUMN_LABELS.get(str(i), f"Col_{i}"))

        with open(rev_p, 'w', encoding='utf-8-sig', newline='') as f_rev, \
             open(reg_p, 'w', encoding='utf-8-sig', newline='') as f_reg:
            f_rev.write("sep=;\r\n" + ";".join(rev_h) + "\r\n")
            f_reg.write("sep=;\r\n" + ";".join(reg_h) + "\r\n")
            for d in self.unified_records:
                f_rev.write(";".join([self._sanitize_value(d.get(k, "")) for k in rev_h]) + "\r\n")
                row = [self._sanitize_value(self.curr_comunita), self._sanitize_value(self.curr_parrocchia), self._sanitize_value(self.curr_anno), d['ID']]
                for i in range(1, 20): 
                    if i == 13: continue
                    row.append(self._sanitize_value(d.get(str(i), "")))
                f_reg.write(";".join(row) + "\r\n")
        return file_path
