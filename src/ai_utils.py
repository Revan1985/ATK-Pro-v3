import os
import logging
import google.generativeai as genai
from key_manager import KeyManager

def get_best_gemini_model(api_key, preferred="flash"):
    """
    Scansiona i modelli disponibili per l'API key fornita e ritorna il migliore 
    del tipo richiesto (flash o pro), evitando versioni sperimentali o deprecate.
    """
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        valid = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                # Evitiamo modelli sperimentali o troppo vecchi se possibile
                if 'exp' not in m.name and 'vision' not in m.name and 'preview' not in m.name:
                    valid.append(m.name.replace('models/', ''))
        
        if not valid:
            return "gemini-1.5-flash" # Fallback estremo
            
        # Filtra per preferenza
        matches = [v for v in valid if preferred in v.lower()]
        if matches:
            # Ordina per trovare l'ultimo (es. 1.5 > 1.0, 2.0 > 1.5)
            matches.sort(reverse=True)
            return matches[0]
            
        valid.sort(reverse=True)
        return valid[0]
    except Exception as e:
        logging.warning(f"[AI-UTILS] Impossibile scansionare modelli: {e}. Uso fallback.")
        return "gemini-1.5-flash"

def rotate_key_on_error(provider, current_key, km=None):
    """
    Tenta di ottenere la prossima chiave disponibile per un provider.
    Ritorna (nuova_chiave, ha_fatto_giro_completo).
    """
    if km is None:
        km = KeyManager()
    return km.get_next_key(provider, current_key)
