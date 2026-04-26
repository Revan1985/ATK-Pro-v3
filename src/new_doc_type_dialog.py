"""
NewDocTypeDialog — Finestra per creare o modificare tipologie documentali custom.
Aperto dal pulsante [＋] / [✎] accanto al combo nei dialoghi OCR, Traduzione, GEDCOM.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QMessageBox, QTabWidget, QWidget,
)
from PySide6.QtCore import Qt


def get_msg(glossario, chiave, lingua):
    """Cerca chiave nel glossario e restituisce la traduzione nella lingua richiesta."""
    if not glossario:
        return None
    for sezione in glossario.values():
        if not isinstance(sezione, list):
            continue
        for voce in sezione:
            if voce.get("messaggio") == chiave:
                return voce.get(lingua) or voce.get("IT") or chiave
    return None


class NewDocTypeDialog(QDialog):
    """
    Dialogo per aggiungere o modificare una tipologia documentale custom.

    Parametri:
        existing_data (dict | None): se fornito, si apre in modalità modifica.
            Atteso: {"label": str, "ocr_prompt": str,
                     "translation_prompt": str, "gedcom_prompt": str}
    """

    STYLE = """
        QDialog { background-color: #181818; color: #fff; border: 2px solid #a67c52; }
        QLabel { color: #fff; }
        QLineEdit, QTextEdit {
            background-color: #2a2a2a;
            color: #f5f0e8;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 4px;
        }
        QTabWidget::pane { border: 1px solid #a67c52; }
        QTabBar::tab {
            background: #2a2a2a; color: #aaa;
            padding: 6px 14px; border-radius: 3px;
        }
        QTabBar::tab:selected { background: #333; color: #fff; }
        QPushButton {
            background-color: #222; color: #fff;
            border: 1px solid #a67c52; padding: 5px 14px; border-radius: 4px;
        }
        QPushButton:hover { background-color: #333; }
        QPushButton#btn_save {
            background-color: #a67c52; border: none; color: #fff; font-weight: bold;
        }
        QPushButton#btn_save:hover { background-color: #c09060; }
    """

    # Placeholder per ciascun tab (aiuta l'utente a capire cosa scrivere)
    PLACEHOLDERS = {
        "ocr": (
            "Es: Sei un paleografo esperto in catasti napoleonici.\n"
            "Trascrivi esattamente ogni riga della tabella, colonna per colonna.\n"
            "Mantieni i valori numerici originali senza arrotondare."
        ),
        "translation": (
            "Es: Contesto: catasto napoleonico, Italia settentrionale, 1810-1815 ca.\n"
            "Traduci i termini burocratici arcaici in italiano moderno.\n"
            "Conserva i nomi propri nella forma originale."
        ),
        "gedcom": (
            "Es: Estrai i dati anagrafici in formato JSON.\n"
            "Ogni intestatario di particella è il soggetto principale.\n"
            "Mappa: Proprietario → name, Comune → birth.place."
        ),
    }

    def gm(self, chiave: str) -> str:
        """Restituisce la traduzione di chiave nella lingua del dialog."""
        result = get_msg(self.glossario_data, chiave, self.lingua)
        return result if result else chiave

    def __init__(self, parent=None, existing_data: dict | None = None,
                 lingua: str = "it", glossario_data: dict | None = None):
        super().__init__(parent)
        self.existing_data = existing_data
        self.result_data: dict | None = None  # popolato al salvataggio
        self.lingua = lingua.upper()
        self.glossario_data = glossario_data or {}

        is_edit = existing_data is not None
        self.setWindowTitle(self.gm("Modifica Tipologia") if is_edit else self.gm("Nuova Tipologia Documentale"))
        self.setMinimumWidth(560)
        self.setStyleSheet(self.STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # --- Nome ---
        lbl_name = QLabel(self.gm("Nome della tipologia: *"))
        lbl_name.setStyleSheet("font-weight: bold;")
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Es: Catasto Napoleonico, Estimo Comunale, ...")
        if is_edit:
            self.txt_name.setText(existing_data.get("label", ""))
            self.txt_name.setReadOnly(True)  # non si può rinominare (chiave logica)
            self.txt_name.setStyleSheet("color: #aaa; background-color: #222;")

        layout.addWidget(lbl_name)
        layout.addWidget(self.txt_name)

        # --- Tab con i 3 prompt ---
        tabs = QTabWidget()

        self.txt_ocr = self._make_prompt_editor(
            existing_data.get("ocr_prompt", "") if is_edit else "",
            self.PLACEHOLDERS["ocr"],
        )
        self.txt_translation = self._make_prompt_editor(
            existing_data.get("translation_prompt", "") if is_edit else "",
            self.PLACEHOLDERS["translation"],
        )
        self.txt_gedcom = self._make_prompt_editor(
            existing_data.get("gedcom_prompt", "") if is_edit else "",
            self.PLACEHOLDERS["gedcom"],
        )

        tabs.addTab(self._wrap(self.txt_ocr), "📄 OCR")
        tabs.addTab(self._wrap(self.txt_translation), "🌐 Traduzione")
        tabs.addTab(self._wrap(self.txt_gedcom), "🌳 GEDCOM")
        layout.addWidget(tabs)

        # Nota esplicativa
        note = QLabel(self.gm(
            "I campi prompt sono opzionali. Se lasciati vuoti, il servizio userà "
            "automaticamente il template \"Manoscritto Generico\"."
        ))
        note.setWordWrap(True)
        note.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(note)

        # --- Pulsanti ---
        btns = QHBoxLayout()
        btn_cancel = QPushButton(self.gm("Annulla"))
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton(self.gm("✔ Salva Tipo") if not is_edit else self.gm("✔ Salva Modifiche"))
        btn_save.setObjectName("btn_save")
        btn_save.clicked.connect(self._save)

        btns.addStretch()
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)
        layout.addLayout(btns)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_prompt_editor(self, text: str, placeholder: str) -> QTextEdit:
        editor = QTextEdit()
        editor.setAcceptRichText(False)
        editor.setPlaceholderText(placeholder)
        editor.setMinimumHeight(140)
        if text:
            editor.setPlainText(text)
        return editor

    def _wrap(self, widget) -> QWidget:
        """Avvolge il widget in un QWidget con margini."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(6, 8, 6, 6)
        lay.addWidget(widget)
        return w

    # ------------------------------------------------------------------
    # Salvataggio
    # ------------------------------------------------------------------

    def _save(self):
        label = self.txt_name.text().strip()
        if not label:
            QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Il nome della tipologia è obbligatorio."))
            return

        self.result_data = {
            "label": label,
            "ocr_prompt": self.txt_ocr.toPlainText().strip(),
            "translation_prompt": self.txt_translation.toPlainText().strip(),
            "gedcom_prompt": self.txt_gedcom.toPlainText().strip(),
        }
        self.accept()
