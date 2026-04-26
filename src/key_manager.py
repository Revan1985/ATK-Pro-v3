import os
import csv
from PySide6.QtCore import QStandardPaths

class KeyManager:
    def __init__(self, app_name="ATK-Pro"):
        self.app_name = app_name
        self.file_path = self._get_keys_file_path()
        self.keys = {"Gemini": [], "OpenAI": [], "Claude": []}
        self.current_indices = {}
        self.load_keys()

    def _get_keys_file_path(self):
        docs = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        base = os.path.join(docs, self.app_name)
        if not os.path.exists(base):
            try: os.makedirs(base, exist_ok=True)
            except: pass
        return os.path.join(base, "api_keys.csv")

    def load_keys(self):
        # Reset
        self.keys = {"Gemini": [], "OpenAI": [], "Claude": []}
        if not os.path.exists(self.file_path):
            self._create_default_file()
            return

        try:
            with open(self.file_path, mode='r', encoding='utf-8-sig') as f:
                first_line = f.readline()
                # Default delimiter
                delimiter = ';' 
                f.seek(0)
                if 'sep=' in first_line:
                    if 'sep=,' in first_line: delimiter = ','
                    f.readline() # skip sep line
                
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    prov = row.get('Provider', '').strip()
                    key = row.get('Key', '').strip()
                    # Normalizzazione nomi provider per matchare l'interfaccia
                    if "GEMINI" in prov.upper(): prov = "Gemini"
                    elif "OPENAI" in prov.upper(): prov = "OpenAI"
                    elif "CLAUDE" in prov.upper() or "ANTHROPIC" in prov.upper(): prov = "Claude"
                    
                    if prov in self.keys and key:
                        self.keys[prov].append(key)
        except Exception as e:
            print(f"DEBUG: Errore caricamento chiavi: {e}")

    def _create_default_file(self):
        try:
            with open(self.file_path, mode='w', encoding='utf-8-sig', newline='') as f:
                f.write("sep=;\r\n")
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['Provider', 'Key', 'Note'])
                writer.writerow(['Gemini', '', 'Inserisci qui la tua chiave Gemini (Censimento/Genealogia)'])
                writer.writerow(['OpenAI', '', 'Inserisci qui la tua chiave OpenAI (GPT-4o)'])
                writer.writerow(['Claude', '', 'Inserisci qui la tua chiave Claude (Anthropic)'])
        except: pass

    def get_all_keys(self, provider):
        return self.keys.get(provider, [])

    def get_next_key(self, provider, current_key=None):
        """Ritorna (chiave, ha_fatto_il_giro_completo)."""
        keys = self.get_all_keys(provider)
        if not keys: return None, False
        
        if current_key not in keys:
            self.current_indices[provider] = 0
            return keys[0], False
        
        if len(keys) == 1:
            return keys[0], True
            
        idx = keys.index(current_key)
        next_idx = (idx + 1) % len(keys)
        
        # Se siamo tornati alla prima (index 0), abbiamo completato il giro
        wrapped = (next_idx == 0)
        
        self.current_indices[provider] = next_idx
        return keys[next_idx], wrapped

    def has_multiple_keys(self, provider):
        return len(self.get_all_keys(provider)) > 1

    def has_keys(self, provider):
        """Ritorna True se il provider ha almeno una chiave configurata."""
        return len(self.get_all_keys(provider)) > 0
