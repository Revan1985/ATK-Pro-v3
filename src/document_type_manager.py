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
    # ── Stato Civile Napoleonico (SCN) ─────────────────────────────────────────
    {"label": "SCN — Atto di Nascita (1806-1815)",           "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCN — Atto di Matrimonio (1806-1815)",        "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCN — Atto di Morte (1806-1815)",             "ocr": True, "translation": True, "gedcom": True},
    # ── Stato Civile della Restaurazione (SCR) ────────────────────────────────
    {"label": "SCR — Atto di Nascita (1815-1865)",           "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR — Atto di Matrimonio (1815-1865)",        "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR — Atto di Morte (1815-1865)",             "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR/Toscana — Atto di Nascita (1817-1865)",   "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR/Toscana — Atto di Matrimonio (1817-1865)","ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR/Toscana — Atto di Morte (1817-1865)",     "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR/Due Sicilie — Atto di Nascita (1816-1865)",   "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR/Due Sicilie — Atto di Matrimonio (1816-1865)","ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR/Due Sicilie — Atto di Morte (1816-1865)",     "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR/Piemonte — Atto di Nascita (1837-1865)",  "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR/Piemonte — Atto di Matrimonio (1837-1865)","ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR/Piemonte — Atto di Morte (1837-1865)",    "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR/Veneto — Atto di Nascita (1816-1866)",    "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR/Veneto — Atto di Matrimonio (1816-1866)", "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCR/Veneto — Atto di Morte (1816-1866)",      "ocr": True, "translation": True, "gedcom": True},
    # ── Stato Civile Italiano Unificato (SCI, dal 1866) ───────────────────────
    {"label": "SCI — Atto di Nascita (dal 1866)",            "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCI — Atto di Matrimonio (dal 1866)",         "ocr": True, "translation": True, "gedcom": True},
    {"label": "SCI — Atto di Morte (dal 1866)",              "ocr": True, "translation": True, "gedcom": True},
    # ── Stato Civile Generico ─────────────────────────────────────────────────
    {"label": "Atto di Stato Civile (Nascita / Battesimo)",  "ocr": True, "translation": True, "gedcom": True},
    {"label": "Atto di Stato Civile (Matrimonio)",           "ocr": True, "translation": True, "gedcom": True},
    {"label": "Atto di Stato Civile (Morte / Sepoltura)",    "ocr": True, "translation": True, "gedcom": True},
    {"label": "Processetto / Allegati Matrimoniali",         "ocr": True, "translation": True, "gedcom": True},
    {"label": "Pubblicazioni di Matrimonio (registro bandi)","ocr": True, "translation": True, "gedcom": True},
    # ── Parrocchiali ──────────────────────────────────────────────────────────
    {"label": "Registro Parrocchiale — Battesimi (sec. XVI-XIX)",         "ocr": True, "translation": True, "gedcom": True},
    {"label": "Registro Parrocchiale — Matrimoni (sec. XVI-XIX)",         "ocr": True, "translation": True, "gedcom": True},
    {"label": "Registro Parrocchiale — Morti / Sepolture (sec. XVI-XIX)", "ocr": True, "translation": True, "gedcom": True},
    {"label": "Registro Parrocchiale — Cresimati (sec. XVI-XIX)",         "ocr": True, "translation": True, "gedcom": True},
    {"label": "Registro degli Esposti / Nati Illegittimi",                "ocr": True, "translation": True, "gedcom": True},
    # ── Censimenti / Anime ────────────────────────────────────────────────────
    {"label": "Stati delle Anime Granducato di Toscana",                  "ocr": True, "translation": True, "gedcom": True},
    {"label": "Anagrafe / Censimento Lombardo-Veneto (sec. XIX)",         "ocr": True, "translation": True, "gedcom": True},
    {"label": "Stato delle Anime / Censimento Parrocchiale",              "ocr": True, "translation": True, "gedcom": True},
    {"label": "Censimento Storico (Generico)",                            "ocr": True, "translation": True, "gedcom": True},
    # ── Catasti ───────────────────────────────────────────────────────────────
    {"label": "Catasto Onciario (Due Sicilie, sec. XVIII)",               "ocr": True, "translation": True, "gedcom": True},
    {"label": "Rivele / Numerazione dei Fuochi (Due Sicilie, sec. XVI-XVII)", "ocr": True, "translation": True, "gedcom": True},
    {"label": "Catasto Murattiano (Due Sicilie, 1808-1815)",              "ocr": True, "translation": True, "gedcom": True},
    {"label": "Catasto Gregoriano (Stato Pontificio, 1816-1835)",         "ocr": True, "translation": True, "gedcom": True},
    # ── Anagrafe / Militare ───────────────────────────────────────────────────
    {"label": "Stato di Famiglia / Atto di Notorietà (SC)",               "ocr": True, "translation": True, "gedcom": True},
    {"label": "Ruolo di Matricola / Leva Militare (1865-1940)",           "ocr": True, "translation": True, "gedcom": True},
    {"label": "Foglio Matricolare (scheda individuale, 1865-1940)",       "ocr": True, "translation": True, "gedcom": True},
    # ── Emigrazione / Esteri ──────────────────────────────────────────────────
    {"label": "Passaporto / Permesso di Espatrio (sec. XIX-XX)",          "ocr": True, "translation": True, "gedcom": True},
    {"label": "Atti Consolari Italiani all'Estero",                       "ocr": True, "translation": True, "gedcom": True},
    {"label": "Registro dei Defunti Ospedalieri",                         "ocr": True, "translation": True, "gedcom": True},
    # ── Indici / Atti amministrativi (Gedcom=False) ───────────────────────────
    {"label": "Indice / Registro degli Atti",                             "ocr": True, "translation": True, "gedcom": False},
    {"label": "Protocollo Notarile (registro degli atti)",                "ocr": True, "translation": True, "gedcom": False},
    # ── Notarile / Latino ─────────────────────────────────────────────────────
    {"label": "Documento Notarile",                                        "ocr": True, "translation": True, "gedcom": True},
    {"label": "Atto in Latino Ecclesiastico",                              "ocr": True, "translation": True, "gedcom": True},
    # ── Corrispondenza / Stampa (Gedcom=False) ────────────────────────────────
    {"label": "Lettera / Corrispondenza Privata",                          "ocr": True, "translation": True, "gedcom": False},
    {"label": "Testo a Stampa Antico",                                     "ocr": True, "translation": True, "gedcom": False},
    # ── Generico ──────────────────────────────────────────────────────────────
    {"label": "Documento Generico / Non Classificato",                     "ocr": True, "translation": True, "gedcom": True},
    # ── Anagrafe comunale ─────────────────────────────────────────────────────
    {"label": "Foglio di Famiglia Anagrafe Comunale (post-1864)",          "ocr": True, "translation": True, "gedcom": True},
    # ── Testamento (Gedcom=False) ──────────────────────────────────────────────
    {"label": "Testamento (atto notarile specifico)",                       "ocr": True, "translation": True, "gedcom": False},
    # ── Matrimonio Religioso ──────────────────────────────────────────────────
    {"label": "Matrimonio Religioso post-Concordato (1929+)",              "ocr": True, "translation": True, "gedcom": True},
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
        self._overrides: dict = {}   # {label: {"ocr": str, "translation": str, "gedcom": str}}
        self._load()

    # ------------------------------------------------------------------
    # Lettura / Scrittura file custom
    # ------------------------------------------------------------------

    def _load(self):
        path = _custom_types_path()
        if not os.path.exists(path):
            self._custom = []
            self._overrides = {}
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._custom = data.get("custom_types", [])
            self._overrides = data.get("builtin_overrides", {})
        except Exception as e:
            logging.error(f"[DTM] Errore caricamento document_types.json: {e}")
            self._custom = []
            self._overrides = {}

    def _save(self):
        path = _custom_types_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    {"custom_types": self._custom, "builtin_overrides": self._overrides},
                    f, ensure_ascii=False, indent=2
                )
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
        Cerca prima negli override utente, poi nei custom, poi ritorna None (built-in usa ocr_prompts).
        """
        bare = self.bare_label(label)
        # Override built-in ha precedenza assoluta
        ov = self._overrides.get(bare, {}).get("ocr", "").strip()
        if ov:
            return ov
        if self.is_custom(label):
            custom = self._find_custom(bare)
            if custom:
                return custom.get("ocr_prompt", "").strip() or None
            return None
        # Built-in senza override: delegato a ocr_prompts.compose_ocr_prompt
        return None

    def get_translation_prompt(self, label: str) -> str | None:
        """
        Restituisce la sezione type_specific del prompt di traduzione (override o None).
        """
        bare = self.bare_label(label)
        ov = self._overrides.get(bare, {}).get("translation", "").strip()
        if ov:
            return ov
        if self.is_custom(label):
            custom = self._find_custom(bare)
            if custom:
                return custom.get("translation_prompt", "").strip() or None
            return None
        return None

    def get_gedcom_prompt(self, label: str) -> str | None:
        """
        Restituisce il prompt GEDCOM per la tipologia indicata (override o None).
        """
        bare = self.bare_label(label)
        ov = self._overrides.get(bare, {}).get("gedcom", "").strip()
        if ov:
            return ov
        if self.is_custom(label):
            custom = self._find_custom(bare)
            if custom:
                return custom.get("gedcom_prompt", "").strip() or None
            return None
        return None

    # ------------------------------------------------------------------
    # Override prompt per tipologie built-in
    # ------------------------------------------------------------------

    def has_builtin_override(self, label: str, service: str) -> bool:
        """True se esiste un override utente per il built-in (service: 'ocr'/'translation'/'gedcom')."""
        bare = self.bare_label(label)
        return bool(self._overrides.get(bare, {}).get(service, "").strip())

    def set_builtin_override(self, label: str, service: str, prompt: str) -> None:
        """Salva/aggiorna l'override di un prompt built-in."""
        bare = self.bare_label(label)
        if bare not in self._overrides:
            self._overrides[bare] = {}
        self._overrides[bare][service] = prompt.strip()
        self._save()

    def delete_builtin_override(self, label: str, service: str) -> None:
        """Rimuove l'override di un prompt built-in, ripristinando il default."""
        bare = self.bare_label(label)
        if bare in self._overrides:
            self._overrides[bare].pop(service, None)
            if not self._overrides[bare]:  # voce vuota → rimuovi
                del self._overrides[bare]
            self._save()

    def get_builtin_original_prompt(self, label: str, service: str) -> str:
        """Restituisce il prompt originale built-in (ignora override) come testo leggibile."""
        bare = self.bare_label(label)
        try:
            if service == "ocr":
                from ocr_prompts import compose_ocr_prompt
                return compose_ocr_prompt(bare)
            elif service == "translation":
                from translation_prompts import compose_translation_prompt
                return compose_translation_prompt(bare, source_text="[TESTO_SORGENTE]", target_lang="Italiano")
            elif service == "gedcom":
                from genealogy_prompts import compose_extraction_prompt
                return compose_extraction_prompt(bare)
        except Exception:
            pass
        return ""

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
