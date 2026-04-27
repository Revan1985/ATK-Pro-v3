"""
DocumentTypeManager — Registro unificato delle tipologie documentali.

Aggrega i tipi built-in da ocr_prompts, translation_prompts e genealogy_prompts,
e permette all'utente di aggiungere tipi custom (persistiti in document_types.json).
I tipi custom appaiono con il prefisso "★ " nel combo.
"""

import json
import os
import logging


# --- Percorso del file custom ---
def _custom_types_path():
    docs = os.path.join(os.path.expanduser("~"), "OneDrive", "Documenti", "ATK-Pro")
    if not os.path.isdir(docs):
        docs = os.path.join(os.path.expanduser("~"), "Documenti", "ATK-Pro")
    if not os.path.isdir(docs):
        docs = os.path.join(os.path.expanduser("~"), "Documents", "ATK-Pro")
    os.makedirs(docs, exist_ok=True)
    return os.path.join(docs, "document_types.json")


# --- Tipologie built-in (immutabili) ---
# Ogni entry ha: label, applicabilità per servizio (ocr/translation/gedcom),
# e un riferimento al prompt nel modulo corrispondente.
BUILTIN_TYPES = [
    {
        "label": "Atto di Stato Civile (Nascita / Battesimo)",
        "ocr": True,
        "translation": True,
        "gedcom": True,
    },
    {
        "label": "Atto di Stato Civile (Matrimonio)",
        "ocr": True,
        "translation": True,
        "gedcom": True,
    },
    {
        "label": "Atto di Stato Civile (Morte / Sepoltura)",
        "ocr": True,
        "translation": True,
        "gedcom": True,
    },
    {
        "label": "Stato delle Anime / Censimento Parrocchiale",
        "ocr": True,
        "translation": True,
        "gedcom": True,
    },
    {
        "label": "Stati delle Anime Granducato di Toscana",
        "ocr": True,
        "translation": False,
        "gedcom": True,
    },
    {
        "label": "Processetto / Allegati Matrimoniali",
        "ocr": True,
        "translation": True,
        "gedcom": True,
    },
    {
        "label": "Documento Notarile",
        "ocr": True,
        "translation": True,
        "gedcom": False,
    },
    {
        "label": "Lettera / Corrispondenza Privata",
        "ocr": True,
        "translation": True,
        "gedcom": False,
    },
    {
        "label": "Testo a Stampa Antico",
        "ocr": True,
        "translation": True,
        "gedcom": False,
    },
    {
        "label": "Atto in Latino Ecclesiastico",
        "ocr": True,
        "translation": True,
        "gedcom": False,
    },
    {
        "label": "Censimento Storico (Generico)",
        "ocr": True,
        "translation": False,
        "gedcom": True,
    },
    {
        "label": "Indice / Registro degli Atti",
        "ocr": True,
        "translation": False,
        "gedcom": False,
    },
    {
        "label": "Documento Generico / Non Classificato",
        "ocr": True,
        "translation": True,
        "gedcom": True,
    },
]

# Prefisso visivo per i tipi custom nel combo
CUSTOM_PREFIX = "★ "


class DocumentTypeManager:
    """
    Gestione centralizzata delle tipologie documentali per tutti e tre i servizi.
    """

    # Prefisso visivo per i tipi custom nel combo (accessibile come attributo di classe)
    CUSTOM_PREFIX = CUSTOM_PREFIX

    def __init__(self):
        self._custom: list[dict] = []
        self._load()

    # ------------------------------------------------------------------
    # Lettura / Scrittura file custom
    # ------------------------------------------------------------------

    def _load(self):
        path = _custom_types_path()
        if not os.path.exists(path):
            self._custom = []
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._custom = data.get("custom_types", [])
        except Exception as e:
            logging.error(f"[DTM] Errore caricamento document_types.json: {e}")
            self._custom = []

    def _save(self):
        path = _custom_types_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"custom_types": self._custom}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"[DTM] Errore salvataggio document_types.json: {e}")

    def reload(self):
        """Ricarica i tipi custom dal file (utile dopo modifiche esterne)."""
        self._load()

    # ------------------------------------------------------------------
    # Elenchi
    # ------------------------------------------------------------------

    def get_labels(self, service: str) -> list[str]:
        """
        Restituisce la lista delle etichette disponibili per un servizio.
        service: "ocr" | "translation" | "gedcom"
        I tipi custom appaiono con il prefisso '★ '.
        """
        result = [t["label"] for t in BUILTIN_TYPES if t.get(service, False)]
        for c in self._custom:
            if c.get(f"{service}_prompt", "").strip() or service != "gedcom":
                # Per i custom, li mostriamo in tutti i servizi che hanno un prompt definito.
                # Se il prompt è vuoto usiamo il generico — quindi li mostriamo sempre.
                result.append(CUSTOM_PREFIX + c["label"])
        return result

    def is_custom(self, label: str) -> bool:
        return label.startswith(CUSTOM_PREFIX)

    def bare_label(self, label: str) -> str:
        """Rimuove il prefisso ★ se presente."""
        return label[len(CUSTOM_PREFIX):] if label.startswith(CUSTOM_PREFIX) else label

    # ------------------------------------------------------------------
    # Recupero prompt
    # ------------------------------------------------------------------

    def get_ocr_prompt(self, label: str) -> str | None:
        """
        Restituisce il prompt OCR per la tipologia indicata,
        o None se non trovato (usa il fallback generico del chiamante).
        """
        bare = self.bare_label(label)
        if self.is_custom(label):
            custom = self._find_custom(bare)
            if custom:
                return custom.get("ocr_prompt", "").strip() or None
            return None
        # Built-in: delegato a ocr_prompts.compose_ocr_prompt
        return None  # Il chiamante usa compose_ocr_prompt direttamente

    def get_translation_prompt(self, label: str) -> str | None:
        """
        Restituisce il prompt di traduzione per la tipologia indicata.
        """
        bare = self.bare_label(label)
        if self.is_custom(label):
            custom = self._find_custom(bare)
            if custom:
                return custom.get("translation_prompt", "").strip() or None
            return None
        return None

    def get_gedcom_prompt(self, label: str) -> str | None:
        """
        Restituisce il prompt GEDCOM per la tipologia indicata.
        """
        bare = self.bare_label(label)
        if self.is_custom(label):
            custom = self._find_custom(bare)
            if custom:
                return custom.get("gedcom_prompt", "").strip() or None
            return None
        return None

    # ------------------------------------------------------------------
    # Gestione custom
    # ------------------------------------------------------------------

    def add_custom_type(
        self,
        label: str,
        ocr_prompt: str = "",
        translation_prompt: str = "",
        gedcom_prompt: str = "",
    ) -> bool:
        """
        Aggiunge un tipo custom. Ritorna False se il label esiste già.
        """
        label = label.strip()
        if not label:
            return False
        if self._find_custom(label) is not None:
            return False
        # Non permettere nomi uguali ai built-in
        builtin_labels = [t["label"] for t in BUILTIN_TYPES]
        if label in builtin_labels:
            return False
        self._custom.append({
            "label": label,
            "ocr_prompt": ocr_prompt.strip(),
            "translation_prompt": translation_prompt.strip(),
            "gedcom_prompt": gedcom_prompt.strip(),
        })
        self._save()
        return True

    def update_custom_type(
        self,
        label: str,
        ocr_prompt: str = "",
        translation_prompt: str = "",
        gedcom_prompt: str = "",
    ) -> bool:
        """
        Aggiorna i prompt di un tipo custom esistente.
        """
        custom = self._find_custom(label)
        if custom is None:
            return False
        custom["ocr_prompt"] = ocr_prompt.strip()
        custom["translation_prompt"] = translation_prompt.strip()
        custom["gedcom_prompt"] = gedcom_prompt.strip()
        self._save()
        return True

    def delete_custom_type(self, label: str) -> bool:
        """
        Elimina un tipo custom. I built-in non possono essere eliminati.
        """
        bare = self.bare_label(label)
        before = len(self._custom)
        self._custom = [c for c in self._custom if c["label"] != bare]
        if len(self._custom) < before:
            self._save()
            return True
        return False

    def get_custom_data(self, label: str) -> dict | None:
        """
        Restituisce il dizionario completo di un tipo custom (per modifica).
        """
        bare = self.bare_label(label)
        return self._find_custom(bare)

    # ------------------------------------------------------------------
    # Interno
    # ------------------------------------------------------------------

    def _find_custom(self, bare_label: str) -> dict | None:
        for c in self._custom:
            if c["label"] == bare_label:
                return c
        return None
