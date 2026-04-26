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

    def __init__(self, source_system="ATK-Pro"):
        self.source_system = source_system
        self.individuals = [] # (iid, lines)
        self.unified_records = []
        self.families = []
        self.sources = []
        self.indi_count = 0
        self.fam_count = 0
        self.last_record_casa = ""
        self.last_record_famiglia = ""
        self.last_record_cognome = ""
        self.curr_comunita = ""
        self.curr_parrocchia = ""
        self.curr_anno = ""

    def _sanitize_value(self, val):
        if val is None: return ""
        if isinstance(val, (dict, list)): return "[PULIZIA]"
        v = str(val).split("\n")[0].split("\r")[0].strip()
        if v.upper() in ["NONE", "NULL", "N/A", "UNKNOWN"]: return ""
        # Sincro v40.1: Rimozione totale di virgolette e semicolon per integrità Excel
        v = v.replace('"', '').replace("'", "").replace(";", ",")
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

    def add_individual(self, first, last, sex="U", original_fields=None):
        if not first and not last: return None
        self.indi_count += 1
        iid = f"@I{self.indi_count}@"
        lines = [f"0 {iid} INDI", f"1 NAME {first} /{last}/" if last else f"1 NAME {first}", f"1 SEX {sex}"]
        
        birth_year = ""
        if original_fields and self.curr_anno:
            eta_raw = str(original_fields.get('6', '')).strip()
            if eta_raw.isdigit() and self.curr_anno.isdigit():
                # Calcolo anno nascita (Anno doc - età)
                birth_year = "CAL " + str(int(self.curr_anno) - int(eta_raw))
                lines.append("1 BIRT")
                lines.append(f"2 DATE {birth_year}")
                
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

    def process_ai_json(self, ai_data):
        meta = ai_data.get('metadata', {})
        if meta:
            self.curr_comunita = meta.get('Comunità', self.curr_comunita)
            self.curr_parrocchia = meta.get('Parrocchia', self.curr_parrocchia)
            self.curr_anno = meta.get('Anno', self.curr_anno)
            if self.curr_parrocchia:
                self.sources.append(f"0 @S1@ SOUR\n1 TITL {self.curr_parrocchia}\n1 DATE {self.curr_anno}\n1 NOTE Comunità: {self.curr_comunita}")

        righe = ai_data.get('righe', ai_data.get('records', []))
        
        # V23.0 Srotolamento Gerarchico
        if 'famiglie' in ai_data:
            righe = []
            for fam in ai_data['famiglie']:
                c_casa = str(fam.get('casa', '')).strip()
                c_fam = str(fam.get('fam', '')).strip()
                c_cogn = str(fam.get('cognome', '')).strip()
                for comp in fam.get('componenti', []):
                    # Prepariamo un dizionario unificato
                    comp['1'] = c_casa
                    comp['2'] = c_fam
                    comp['4'] = c_cogn
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

            # Colonne genealogicamente ereditabili: Casa, Famiglia, Cognome, Religione
            colonne_ereditabili = ['1', '2', '4', '14']
            
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
