import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QTextEdit, QFileDialog, QSplitter, QWidget, QProgressBar, QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt

from translation_processor import TranslationWorker

def get_msg(glossario, chiave, lingua):
    try:
        from main_gui_qt import get_msg as _get_msg
        res = _get_msg(glossario, chiave, lingua)
        return res if res is not None else chiave
    except:
        return chiave

class TranslationDialog(QDialog):
    def __init__(self, parent, glossario_data, lingua_corrente):
        super().__init__(parent)
        self.glossario = glossario_data
        self.lingua = lingua_corrente
        self.setWindowTitle(self.gm("Traduzione Paleografica Assistita (LLM)"))
        self.resize(1200, 800)
        self.setup_ui()
        self.load_settings()

    def gm(self, chiave):
        return get_msg(self.glossario, chiave, self.lingua)

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #1a1a1a; color: #fff; }
            QLabel { color: #e6c891; font-weight: bold; font-size: 13px; }
            QPushButton { background-color: #333; border: 1px solid #a67c52; padding: 6px 12px; border-radius: 4px; font-weight: bold; color: #fff; }
            QPushButton:hover { background-color: #444; }
            #btn_traduci { background-color: #a67c52; color: #fff; padding: 10px; font-size: 14px; }
            QTextEdit { background-color: #262626; color: #ddd; border: 1px solid #555; border-radius: 3px; font-size: 14px; padding: 5px; }
            QComboBox, QLineEdit { background-color: #333; color: #fff; border: 1px solid #555; border-radius: 3px; padding: 4px; }
        """)

        main_layout = QVBoxLayout(self)
        
        # Header (Top Settings)
        top_layout = QHBoxLayout()
        
        lbl_prov = QLabel(self.gm("Provider IA:"))
        self.combo_prov = QComboBox()
        self.combo_prov.addItems(["Google Gemini (Free/Consigliato)", "OpenAI (GPT-4o)", "Anthropic (Claude 3.5)"])

        # Tipologia Documentale
        from document_type_manager import DocumentTypeManager
        self._dtm = DocumentTypeManager()
        lbl_type = QLabel(self.gm("Tipologia Documento:"))
        lbl_type.setStyleSheet("color: #f5f0e8; font-weight: bold;")
        self.combo_type = QComboBox()
        self.combo_type.addItems(self._dtm.get_labels(service="translation"))
        self.combo_type.currentIndexChanged.connect(self._on_type_changed_tr)

        self.lbl_api = QLabel(self.gm("API Key:"))
        api_inner_ly = QHBoxLayout()
        self.txt_api = QLineEdit()
        self.txt_api.setEchoMode(QLineEdit.Password)
        self.txt_api.setFixedWidth(200)
        
        btn_key_safe = QPushButton("🔑 " + self.gm("Cassaforte"))
        btn_key_safe.setStyleSheet("background-color: #2a2a2a; color: #f5f0e8; border: 1px solid #888; padding: 2px 10px; border-radius: 4px; font-size: 11px;")
        btn_key_safe.clicked.connect(self.open_key_manager)
        
        api_inner_ly.addWidget(self.txt_api)
        api_inner_ly.addWidget(btn_key_safe)

        lbl_target = QLabel(self.gm("Lingua di Destinazione:"))
        self.combo_lingua = QComboBox()
        # Le 20 lingue supportate sotto forma di autonimi
        lingue = [
            "Italiano", "English", "Deutsch", "Français", "Español", "Português",
            "Русский", "中文", "日本語", "韓国語", "العربية", "हिन्दी", "Türkçe",
            "Polski", "Nederlands", "Ελληνικά", "Čeština", "Svenska", "Dansk", "Suomi"
        ]
        self.combo_lingua.addItems(lingue)

        top_layout.addWidget(lbl_prov)
        top_layout.addWidget(self.combo_prov)
        top_layout.addSpacing(20)
        btn_add_type_tr = QPushButton("+")
        btn_add_type_tr.setToolTip("Aggiungi tipologia personalizzata")
        btn_add_type_tr.setFixedWidth(30)
        btn_add_type_tr.setStyleSheet("background-color: #3a8a3a; color: #ffffff; border-radius: 4px; font-weight: bold; font-family: Arial, sans-serif; font-size: 14px;")
        btn_add_type_tr.clicked.connect(self._add_custom_type)
        self.btn_edit_type = QPushButton("✏")
        self.btn_edit_type.setToolTip("Modifica tipologia personalizzata selezionata")
        self.btn_edit_type.setFixedWidth(30)
        self.btn_edit_type.setStyleSheet("background-color: #3a5a8a; color: #ffffff; border-radius: 4px; font-family: Arial, sans-serif; font-size: 13px;")
        self.btn_edit_type.clicked.connect(self._edit_custom_type)
        self.btn_edit_type.setVisible(False)
        top_layout.addWidget(lbl_type)
        top_layout.addWidget(self.combo_type)
        top_layout.addWidget(btn_add_type_tr)
        top_layout.addWidget(self.btn_edit_type)
        top_layout.addSpacing(20)
        top_layout.addWidget(self.lbl_api)
        top_layout.addLayout(api_inner_ly)
        top_layout.addStretch()
        top_layout.addWidget(lbl_target)
        top_layout.addWidget(self.combo_lingua)
        
        main_layout.addLayout(top_layout)

        # Splitter main content
        splitter = QSplitter(Qt.Horizontal)
        
        # --- LEFT PANE ---
        left_widget = QWidget()
        left_ly = QVBoxLayout(left_widget)
        left_ly.setContentsMargins(0, 10, 5, 0)
        
        # Origine
        header_orig = QHBoxLayout()
        lbl_orig = QLabel(self.gm("Testo Sorgente (Antico/Gregoriano/Dialetto):"))
        btn_load = QPushButton(self.gm("Carica File TXT"))
        btn_load.clicked.connect(self.carica_file)
        header_orig.addWidget(lbl_orig)
        header_orig.addStretch()
        header_orig.addWidget(btn_load)
        
        self.txt_orig = QTextEdit()
        self.txt_orig.setPlaceholderText(self.gm("Incolla qui la trascrizione cruda o carica un file .txt generato prima..."))
        
        # Contesto
        lbl_ctx = QLabel(self.gm("Glossario & Contesto (Opzionale, istruzioni alla IA):"))
        self.txt_ctx = QTextEdit()
        self.txt_ctx.setMaximumHeight(80)
        self.txt_ctx.setPlaceholderText(self.gm("Es. Traduci mantenendo arcaico. Cabella = dazio. Tassano = Nome proprio."))
        
        left_ly.addLayout(header_orig)
        left_ly.addWidget(self.txt_orig)
        left_ly.addWidget(lbl_ctx)
        left_ly.addWidget(self.txt_ctx)
        
        # --- RIGHT PANE ---
        right_widget = QWidget()
        right_ly = QVBoxLayout(right_widget)
        right_ly.setContentsMargins(5, 10, 0, 0)
        
        lbl_dest = QLabel(self.gm("Risultato Tradotto:"))
        self.txt_dest = QTextEdit()
        self.txt_dest.setPlaceholderText(self.gm("La traduzione moderna apparirà qui e potrà essere revisionata..."))
        
        # Export
        export_ly = QHBoxLayout()
        btn_save_txt = QPushButton(self.gm("Salva Traduzione (TXT)"))
        btn_save_txt.clicked.connect(lambda: self.esporta_risultato("txt"))
        btn_save_docx = QPushButton(self.gm("Esporta in Word (DOCX)"))
        btn_save_docx.clicked.connect(lambda: self.esporta_risultato("docx"))
        export_ly.addWidget(btn_save_txt)
        export_ly.addWidget(btn_save_docx)
        
        right_ly.addWidget(lbl_dest)
        right_ly.addWidget(self.txt_dest)
        right_ly.addLayout(export_ly)
        
        # Add to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Give them 50/50 ratio
        splitter.setSizes([500, 500])
        main_layout.addWidget(splitter, 1) # stretch 1
        
        # Bottom Bar
        bottom_ly = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0) # Indeterminate spinning
        
        self.btn_traduci = QPushButton("✨ " + self.gm("Traduci Testo ORA"))
        self.btn_traduci.setObjectName("btn_traduci")
        self.btn_traduci.clicked.connect(self.avvia_traduzione)
        
        bottom_ly.addWidget(self.progress_bar, 1)
        bottom_ly.addWidget(self.btn_traduci)
        
        main_layout.addLayout(bottom_ly)

    def _on_type_changed_tr(self):
        is_custom = self._dtm.is_custom(self.combo_type.currentText())
        self.btn_edit_type.setVisible(is_custom)

    def _add_custom_type(self):
        from new_doc_type_dialog import NewDocTypeDialog
        dlg = NewDocTypeDialog(self)
        if dlg.exec() and dlg.result_data:
            ok = self._dtm.add_custom_type(**dlg.result_data)
            if ok:
                label = self._dtm.CUSTOM_PREFIX + dlg.result_data["label"]
                self.combo_type.addItem(label)
                self.combo_type.setCurrentText(label)
            else:
                QMessageBox.warning(self, "Attenzione", "Una tipologia con questo nome esiste già.")

    def _edit_custom_type(self):
        label = self.combo_type.currentText()
        data = self._dtm.get_custom_data(label)
        if not data:
            return
        from new_doc_type_dialog import NewDocTypeDialog
        dlg = NewDocTypeDialog(self, existing_data=data)
        if dlg.exec() and dlg.result_data:
            self._dtm.update_custom_type(**dlg.result_data)

    def load_settings(self):
        try:
            from config_utils import _config_file_path
            import json, os
            cfg = _config_file_path()
            if os.path.exists(cfg):
                with open(cfg, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                
                # API and Provider (Same as OCR)
                self.txt_api.setText(prefs.get('ocr_api_key', ''))
                prov = prefs.get('ocr_provider', 0)
                self.combo_prov.setCurrentIndex(prov)
                # Ripristina tipologia documentale
                saved_type = prefs.get('translation_doc_type', '')
                if saved_type:
                    idx = self.combo_type.findText(saved_type)
                    if idx >= 0: self.combo_type.setCurrentIndex(idx)
                # Translation specific
                self.txt_ctx.setText(prefs.get('translation_context', ''))
            
            # Default Language logic based on self.lingua (e.g. "it" -> Italiano)
            lang_map = {"it": "Italiano", "en": "English", "fr": "Français", "es": "Español", "de": "Deutsch"}
            default_autonym = lang_map.get(self.lingua, "English")
            idx = self.combo_lingua.findText(default_autonym)
            if idx >= 0:
                self.combo_lingua.setCurrentIndex(idx)
                    
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        try:
            from config_utils import _write_config_prefs
            _write_config_prefs('ocr_api_key', self.txt_api.text().strip())
            _write_config_prefs('ocr_provider', self.combo_prov.currentIndex())
            _write_config_prefs('translation_doc_type', self.combo_type.currentText())
            _write_config_prefs('translation_context', self.txt_ctx.toPlainText().strip())
        except:
            pass

    def carica_file(self):
        path, _ = QFileDialog.getOpenFileName(self, self.gm("Seleziona file di testo"), "", "Text Files (*.txt);;All Files (*.*)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.txt_orig.setPlainText(f.read())
            except Exception as e:
                QMessageBox.warning(self, "Errore", f"Impossibile leggere il file: {e}")

    def avvia_traduzione(self):
        src_text = self.txt_orig.toPlainText().strip()
        if not src_text:
            QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Immettere o caricare del testo sorgente prima di tradurre."))
            return

        api_key = self.txt_api.text().strip()
        if not api_key:
            QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Inserire la API Key per il provider scelto."))
            return

        self.save_settings()

        prov_str = self.combo_prov.currentText().split()[0]  # "Google" → "Gemini"
        if prov_str == "Google": prov_str = "Gemini"
        elif prov_str == "Anthropic": prov_str = "Claude"

        # Costruisce il prompt dalla tipologia documentale selezionata
        doc_type = self.combo_type.currentText()
        if self._dtm.is_custom(doc_type):
            custom_tr = self._dtm.get_translation_prompt(doc_type) or ""
            from translation_prompts import compose_translation_prompt
            final_prompt_text = compose_translation_prompt(
                doc_type="Traduzione Libera (Nessun Contesto Specifico)",
                source_text=src_text,
                target_lang=self.combo_lingua.currentText(),
                context_info=(custom_tr + "\n" + self.txt_ctx.toPlainText().strip()).strip()
            )
        else:
            from translation_prompts import compose_translation_prompt
            final_prompt_text = compose_translation_prompt(
                doc_type=doc_type,
                source_text=src_text,
                target_lang=self.combo_lingua.currentText(),
                context_info=self.txt_ctx.toPlainText().strip()
            )

        self.btn_traduci.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.txt_dest.setPlainText(self.gm("Elaborazione della traduzione in corso. Potrebbe richiedere alcune decine di secondi..."))

        self.worker = TranslationWorker(
            provider=prov_str,
            api_key=api_key,
            source_text=final_prompt_text,  # il prompt già include il testo sorgente
            target_lang_autonym=self.combo_lingua.currentText(),
            context_info=""  # già incluso nel prompt composto
        )
        self.worker.finished.connect(self.on_traduzione_completata)
        self.worker.start()

    def on_traduzione_completata(self, success, text):
        self.btn_traduci.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.txt_dest.setPlainText(text)
        else:
            self.txt_dest.setPlainText("")
            QMessageBox.critical(self, self.gm("Errore API"), text)

    def esporta_risultato(self, format_ext):
        content = self.txt_dest.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Non ci sono risultati da esportare."))
            return

        filter_str = "Documento testo (*.txt)" if format_ext == "txt" else "Microsoft Word (*.docx)"
        # Disabilito momentaneamente il DontUseNativeDialog che causa glitch stilistici sui Windows moderni, reintroduco il parent nullo per evitare i break e i crash alla memory release.
        filename, _ = QFileDialog.getSaveFileName(None, self.gm("Salva File"), f"Traduzione.{format_ext}", filter_str)
        if filename:
            try:
                if format_ext == "txt":
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                elif format_ext == "docx":
                    import docx
                    doc = docx.Document()
                    doc.add_paragraph(content)
                    doc.save(filename)
                QMessageBox.information(self, self.gm("Successo"), self.gm("File salvato in:\n") + filename)
            except Exception as e:
                QMessageBox.critical(self, self.gm("Errore"), f"{self.gm('Impossibile salvare il file:')}\n{e}")

    def open_key_manager(self):
        from key_manager import KeyManager
        km = KeyManager()
        import platform, subprocess
        if os.path.exists(km.file_path):
            try:
                if platform.system() == 'Windows': os.startfile(km.file_path)
                elif platform.system() == 'Darwin': subprocess.run(['open', km.file_path])
                else: subprocess.run(['xdg-open', km.file_path])
            except: QMessageBox.warning(self, "Errore", "Impossibile aprire il file CSV.")
        else:
            QMessageBox.warning(self, "Errore", "File chiavi non trovato.")
