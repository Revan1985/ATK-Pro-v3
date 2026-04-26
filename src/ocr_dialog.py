import os
import threading
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QCheckBox, QLineEdit, QFileDialog, QProgressBar, QMessageBox, QApplication, QTextEdit, QScrollArea, QGraphicsView
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont, QPixmap

from asset_cache import get_pixmap_cached
from ocr_processor import AdvancedOCRWorker

def get_msg(glossario, chiave, lingua):
    try:
        from main_gui_qt import get_msg as _get_msg
        return _get_msg(glossario, chiave, lingua)
    except:
        return chiave

def asset_path(rel_path):
    try:
        from main_gui_qt import asset_path as _asset_path
        return _asset_path(rel_path)
    except:
        return rel_path

class ZoomableView(QGraphicsView):
    def __init__(self, pixmap, parent=None):
        from PySide6.QtWidgets import QGraphicsScene
        from PySide6.QtGui import QPainter
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.item = self.scene.addPixmap(pixmap)
        self.setScene(self.scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.fitInView(self.item, Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)

class OCRReviewDialog(QDialog):
    def __init__(self, img_path, raw_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Revisione Interattiva OCR")
        from PySide6.QtCore import Qt
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setMinimumSize(900, 600)
        self.resize(1100, 750)
        
        self.setStyleSheet("""
            QDialog { background-color: #181818; color: #fff; border: 2px solid #a67c52; }
            QLabel { color: #fff; font-size: 14px; }
            QPushButton { background-color: #222; border: 1px solid #a67c52; padding: 6px 18px; border-radius: 6px; font-weight: bold; color: #fff; }
            QPushButton:hover { background-color: #333; }
            QTextEdit { background-color: #2a2a2a; color: #ccc; border: 1px solid #555; border-radius: 4px; font-size: 14px; }
        """)
        
        layout = QHBoxLayout(self)
        
        # Left side: Image Viewer
        pix = QPixmap(img_path)
        if not pix.isNull():
            self.zoom_view = ZoomableView(pix)
            self.zoom_view.setStyleSheet("background-color: #2a2a2a; border: 1px solid #555;")
            layout.addWidget(self.zoom_view, 1)
        else:
            lbl = QLabel("Immagine non disponibile")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl, 1)
        
        # Right side: Editor + Buttons
        right_ly = QVBoxLayout()
        lbl_info = QLabel("Correggi il testo a destra e clicca 'Approva' per salvare i file:")
        lbl_info.setStyleSheet("color: #e6c891; font-weight: bold;")
        self.txt_editor = QTextEdit()
        self.txt_editor.setPlainText(raw_text)
        
        btn_ly = QHBoxLayout()
        btn_skip = QPushButton("Salta Pagina")
        btn_skip.clicked.connect(self.reject)
        btn_ok = QPushButton("Approva e Genera File")
        btn_ok.setStyleSheet("background-color: #a67c52; color: #fff; padding: 8px;")
        btn_ok.clicked.connect(self.accept)
        
        btn_ly.addWidget(btn_skip)
        btn_ly.addWidget(btn_ok)
        
        right_ly.addWidget(lbl_info)
        right_ly.addWidget(self.txt_editor)
        right_ly.addLayout(btn_ly)
        
        layout.addLayout(right_ly, 1)

class OCRThread(QThread):
    progress = Signal(int, int, str)
    finished = Signal(bool, str)
    review_requested = Signal(str, str)

    def __init__(self, file_paths, provider, api_key, formats, output_dir, prefix_elab="Elaborazione: ", custom_prompt="", example_text="", interactive=False):
        super().__init__()
        self.file_paths = file_paths
        self.provider = provider
        self.api_key = api_key
        self.formats = formats
        self.output_dir = output_dir
        self.prefix_elab = prefix_elab
        self.custom_prompt = custom_prompt
        self.example_text = example_text
        self.interactive = interactive
        self.review_event = threading.Event()
        self.reviewed_text = None

    def run(self):
        try:
            worker = AdvancedOCRWorker(self.provider, self.api_key, self.formats, self.output_dir, self.custom_prompt, self.example_text)
            
            def interceptor(img_path, raw_text):
                if not self.interactive:
                    return raw_text
                self.reviewed_text = None
                self.review_requested.emit(img_path, raw_text)
                self.review_event.wait()
                self.review_event.clear()
                return self.reviewed_text
                
            total = len(self.file_paths)
            for i, f_path in enumerate(self.file_paths):
                self.progress.emit(i, total, f"{self.prefix_elab}{os.path.basename(f_path)}")
                worker.process_file(f_path, review_callback=interceptor)
            self.progress.emit(total, total, "Completato")
            self.finished.emit(True, "Estrazione OCR completata con successo.")
        except Exception as e:
            self.finished.emit(False, str(e))

class AdvancedOCRDialog(QDialog):
    def __init__(self, parent=None, glossario_data=None, lingua="it"):
        super().__init__(parent)
        self.glossario_data = glossario_data
        self.lingua = lingua
        self.file_paths = []
        self.saved_instructions_list = []
        self.setup_ui()
        self.load_settings()

    def gm(self, text):
        res = get_msg(self.glossario_data, text, self.lingua)
        if res and res != text: return res
        
        # Override per lingua inglese per chiavi nuove non nel glossario
        if self.lingua.lower() == 'en':
            en_dict = {
                "OCR Avanzato (Trascrizione Diplomatica)": "Advanced OCR (Diplomatic Transcription)",
                "File Selezionati:": "Selected Files:",
                "Nessun file selezionato": "No file selected",
                "Seleziona File (Immagini/PDF)": "Select Files (Images/PDF)",
                "Seleziona Provider IA:": "Select AI Provider:",
                "Google Gemini (Free/Consigliato)": "Google Gemini (Free/Recommended)",
                "API Key per il provider scelto:": "API Key for chosen provider:",
                "Formati di Output:": "Output Formats:",
                "Testo Semplice (.txt)": "Plain Text (.txt)",
                "Documento Word (.docx)": "Word Document (.docx)",
                "XML TEI per Trascrizione (.xml)": "TEI XML Transcription (.xml)",
                "Avvia OCR": "Start OCR",
                "Chiudi": "Close",
                "Seleziona Immagini o PDF": "Select Images or PDF",
                "file selezionati": "files selected",
                "Seleziona cartella di destinazione": "Select destination folder",
                "Attenzione": "Warning",
                "Errore": "Error",
                "Completato": "Completed",
                "Estrazione OCR completata con successo.": "OCR extraction completed successfully.",
                "Seleziona almeno un file.": "Please select at least one file.",
                "Inserisci la API Key valida.": "Please enter a valid API Key.",
                "Seleziona almeno un formato di output.": "Please check at least one output format.",
                "Istruzioni Aggiuntive per l'IA (Opzionale):": "Additional AI Instructions (Optional):",
                "Es: I nomi dei mesi sono in dialetto, ometti i timbri a margine...": "Ex: Month names are in dialect, ignore stamps on the margins...",
                "Trascrizione di Riferimento (Opzionale, migliora la lettura):": "Reference Transcription (Optional, improves reading accuracy):",
                "Copia qui la trascrizione esatta della primissima pagina. L'IA imparerà la calligrafia incrociandola con le tue parole.": "Paste the exact transcription of the very first page here. The AI will learn the handwriting by cross-referencing it with your words.",
                "Salva": "Save",
                "-- Istruzioni Salvate --": "-- Saved Instructions --",
                "Istruzione salvata nell'archivio.": "Instruction saved in the archive.",
                "Cassaforte": "Key Safe"
            }
            return en_dict.get(text, text)
            
        return text

    def setup_ui(self):
        self.setWindowTitle(self.gm("OCR Avanzato (Trascrizione Diplomatica)"))
        self.setMinimumSize(700, 600)
        self.resize(850, 650)
        self.setStyleSheet("""
            QDialog { background-color: #181818; color: #fff; border: 2px solid #a67c52; }
            QLabel { color: #fff; font-size: 14px; }
            QPushButton { background-color: #222; border: 1px solid #a67c52; padding: 6px 18px; border-radius: 6px; font-weight: bold; color: #fff; }
            QPushButton:hover { background-color: #333; }
            QComboBox, QLineEdit, QCheckBox { background-color: #2a2a2a; color: #fff; padding: 4px; border: 1px solid #555; border-radius: 4px; }
            QTextEdit { background-color: #2a2a2a; color: #ccc; border: 1px solid #555; border-radius: 4px; }
        """)

        layout = QVBoxLayout(self)

        # File Selection
        lbl_file = QLabel(self.gm("File Selezionati:"))
        self.lbl_file_path = QLabel(self.gm("Nessun file selezionato"))
        self.lbl_file_path.setWordWrap(True)
        btn_sel = QPushButton(self.gm("Seleziona File (Immagini/PDF)"))
        btn_sel.clicked.connect(self.select_files)
        
        file_layout = QHBoxLayout()
        file_layout.addWidget(lbl_file)
        file_layout.addWidget(self.lbl_file_path)
        file_layout.addWidget(btn_sel)
        layout.addLayout(file_layout)

        # Tipologia Documentale
        from document_type_manager import DocumentTypeManager
        self._dtm = DocumentTypeManager()
        type_layout = QHBoxLayout()
        lbl_type = QLabel(self.gm("Tipologia Documento:"))
        lbl_type.setStyleSheet("color: #f5f0e8; font-weight: bold;")
        self.combo_type = QComboBox()
        self.combo_type.addItems(self._dtm.get_labels(service="ocr"))
        self.combo_type.currentIndexChanged.connect(self._on_type_changed_ocr)
        btn_add_type = QPushButton("+")
        btn_add_type.setToolTip("Aggiungi tipologia personalizzata")
        btn_add_type.setFixedWidth(30)
        btn_add_type.setStyleSheet("background-color: #3a8a3a; color: #ffffff; border-radius: 4px; font-weight: bold; font-family: Arial, sans-serif; font-size: 14px;")
        btn_add_type.clicked.connect(self._add_custom_type)
        self.btn_edit_type = QPushButton("✏")
        self.btn_edit_type.setToolTip("Modifica tipologia personalizzata selezionata")
        self.btn_edit_type.setFixedWidth(30)
        self.btn_edit_type.setStyleSheet("background-color: #3a5a8a; color: #ffffff; border-radius: 4px; font-family: Arial, sans-serif; font-size: 13px;")
        self.btn_edit_type.clicked.connect(self._edit_custom_type)
        self.btn_edit_type.setVisible(False)
        type_layout.addWidget(lbl_type)
        type_layout.addWidget(self.combo_type, 1)
        type_layout.addWidget(btn_add_type)
        type_layout.addWidget(self.btn_edit_type)
        layout.addLayout(type_layout)

        # Provider Selection
        lbl_prov = QLabel(self.gm("Seleziona Provider IA:"))
        self.combo_prov = QComboBox()
        self.combo_prov.addItems([
            self.gm("Google Gemini (Free/Consigliato)"), 
            "OpenAI (GPT-4o)", 
            "Anthropic (Claude 3.5)"
        ])
        self.combo_prov.currentIndexChanged.connect(self.provider_changed)
        layout.addWidget(lbl_prov)
        layout.addWidget(self.combo_prov)

        # API Key
        self.lbl_api = QLabel(self.gm("API Key per il provider scelto:"))
        api_ly = QHBoxLayout()
        self.txt_api = QLineEdit()
        self.txt_api.setEchoMode(QLineEdit.Password)
        
        btn_key_safe = QPushButton("🔑 " + self.gm("Cassaforte"))
        btn_key_safe.setStyleSheet("background-color: #2a2a2a; color: #f5f0e8; border: 1px solid #888; padding: 2px 10px; border-radius: 4px; font-size: 11px;")
        btn_key_safe.clicked.connect(self.open_key_manager)
        
        api_ly.addWidget(self.txt_api)
        api_ly.addWidget(btn_key_safe)
        
        layout.addWidget(self.lbl_api)
        layout.addLayout(api_ly)

        # Formats
        lbl_fmt = QLabel(self.gm("Formati di Output:"))
        self.chk_txt = QCheckBox(self.gm("Testo Semplice (.txt)"))
        self.chk_docx = QCheckBox(self.gm("Documento Word (.docx)"))
        self.chk_xml = QCheckBox(self.gm("XML TEI per Trascrizione (.xml)"))
        self.chk_txt.setChecked(True)
        self.chk_docx.setChecked(True)
        self.chk_xml.setChecked(True)
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(self.chk_txt)
        fmt_layout.addWidget(self.chk_docx)
        fmt_layout.addWidget(self.chk_xml)
        layout.addWidget(lbl_fmt)
        layout.addLayout(fmt_layout)

        # Revisione Interattiva Checkbox
        self.chk_interactive = QCheckBox("Abilita Finestra di Revisione Interattiva prima di salvare l'OCR")
        self.chk_interactive.setStyleSheet("color: #f5f0e8; font-weight: bold; margin-top: 5px; margin-bottom: 5px;")
        layout.addWidget(self.chk_interactive)

        # Istruzioni extra con Archiviazione
        istr_header_ly = QHBoxLayout()
        lbl_istruzioni = QLabel(self.gm("Istruzioni Aggiuntive per l'IA (Opzionale):"))
        lbl_istruzioni.setStyleSheet("margin-top: 10px; color: #f5f0e8; font-weight: bold;")
        
        self.combo_istruzioni = QComboBox()
        self.combo_istruzioni.addItem(self.gm("-- Istruzioni Salvate --"), "")
        self.combo_istruzioni.currentIndexChanged.connect(self.load_saved_instruction)
        
        self.btn_save_istruzione = QPushButton(self.gm("Salva"))
        self.btn_save_istruzione.setStyleSheet("background-color: #2a2a2a; color: #f5f0e8; border: 1px solid #888; padding: 2px 10px; border-radius: 4px; font-size: 11px;")
        self.btn_save_istruzione.clicked.connect(self.save_current_instruction)
        
        istr_header_ly.addWidget(lbl_istruzioni)
        istr_header_ly.addStretch()
        istr_header_ly.addWidget(self.combo_istruzioni)
        istr_header_ly.addWidget(self.btn_save_istruzione)
        
        layout.addLayout(istr_header_ly)
        
        self.txt_istruzioni = QTextEdit()
        self.txt_istruzioni.setAcceptRichText(False)
        self.txt_istruzioni.setPlaceholderText(self.gm("Es: I nomi dei mesi sono in dialetto, ometti i timbri a margine..."))
        self.txt_istruzioni.setMaximumHeight(60)
        layout.addWidget(lbl_istruzioni)
        layout.addWidget(self.txt_istruzioni)

        # Trascrizione di Esempio (Few-Shot)
        es_header_ly = QHBoxLayout()
        lbl_esempio = QLabel(self.gm("Trascrizione di Riferimento (Opzionale):"))
        lbl_esempio.setStyleSheet("margin-top: 5px; color: #f5f0e8; font-weight: bold;")
        
        self.btn_clear_esempio = QPushButton("✖ Cancella Testo")
        self.btn_clear_esempio.setStyleSheet("background-color: #5a1a1a; color: #fff; padding: 2px 10px; border-radius: 4px; font-size: 11px;")
        self.btn_clear_esempio.clicked.connect(lambda: self.txt_esempio.clear())
        
        es_header_ly.addWidget(lbl_esempio)
        es_header_ly.addStretch()
        es_header_ly.addWidget(self.btn_clear_esempio)
        
        self.txt_esempio = QTextEdit()
        self.txt_esempio.setAcceptRichText(False)
        self.txt_esempio.setPlaceholderText(self.gm("Copia qui la trascrizione esatta della primissima pagina per addestrare l'IA."))
        self.txt_esempio.setMaximumHeight(80)
        
        layout.addLayout(es_header_ly)
        layout.addWidget(self.txt_esempio)

        # Progress
        self.progress_lbl = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_lbl)
        layout.addWidget(self.progress_bar)

        # Start/Close
        btns = QHBoxLayout()
        self.btn_start = QPushButton(self.gm("Avvia OCR"))
        self.btn_start.clicked.connect(self.start_ocr)
        self.btn_close = QPushButton(self.gm("Chiudi"))
        self.btn_close.clicked.connect(self.reject)
        btns.addWidget(self.btn_start)
        btns.addWidget(self.btn_close)
        layout.addLayout(btns)

    def _on_type_changed_ocr(self):
        """Mostra/nasconde il pulsante Modifica in base al tipo selezionato."""
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

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, self.gm("Seleziona Immagini o PDF"), "",
            "Documenti ( *.pdf *.png *.jpg *.jpeg *.tiff *.tif )"
        )
        if files:
            self.file_paths = files
            self.lbl_file_path.setText(f"{len(files)} " + self.gm("file selezionati"))

    def provider_changed(self):
        prov = self.combo_prov.currentText()
        if "Gemini" in prov: self.lbl_api.setText(self.gm("Google Gemini API Key:"))
        elif "OpenAI" in prov: self.lbl_api.setText(self.gm("OpenAI API Key:"))
        else: self.lbl_api.setText(self.gm("Anthropic API Key:"))

    def load_settings(self):
        try:
            from config_utils import _config_file_path
            import json, os
            cfg = _config_file_path()
            if os.path.exists(cfg):
                with open(cfg, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                prov_idx = prefs.get('ocr_provider', 0)
                self.combo_prov.setCurrentIndex(prov_idx)
                # Ripristina tipologia documentale
                saved_type = prefs.get('ocr_doc_type', '')
                if saved_type:
                    idx = self.combo_type.findText(saved_type)
                    if idx >= 0: self.combo_type.setCurrentIndex(idx)

                # Restore memory for textboxes
                self.txt_istruzioni.setText(prefs.get('ocr_custom_prompt', ''))
                self.txt_esempio.setText(prefs.get('ocr_example_text', ''))

                # Restore saved prompts history
                self.saved_instructions_list = prefs.get('ocr_saved_prompts', [])
                for txt in self.saved_instructions_list:
                    trunc = txt.replace('\n', ' ')
                    if len(trunc) > 40: trunc = trunc[:37] + "..."
                    self.combo_istruzioni.addItem(trunc, txt)

            # Pre-carica la prima chiave disponibile dalla Cassaforte (KeyManager)
            prov_str = "Gemini"
            if "OpenAI" in self.combo_prov.currentText(): prov_str = "OpenAI"
            elif "Anthropic" in self.combo_prov.currentText(): prov_str = "Claude"
            try:
                from key_manager import KeyManager
                km = KeyManager()
                keys = km.get_all_keys(prov_str)
                if keys:
                    self.txt_api.setText(keys[0])
                    import logging
                    logging.info(f"[OCR] Chiave pre-caricata da Cassaforte ({prov_str}): {keys[0][:6]}...")
                elif os.path.exists(_config_file_path()):
                    # Fallback: leggi dal config.json
                    with open(_config_file_path(), 'r', encoding='utf-8') as f:
                        self.txt_api.setText(json.load(f).get('ocr_api_key', ''))
            except Exception as km_e:
                import logging
                logging.warning(f"[OCR] Impossibile caricare chiave da Cassaforte: {km_e}")

        except Exception as e:
            import logging
            logging.error(f"Errore caricamento OCR settings: {e}")

    def save_settings(self):
        try:
            from config_utils import _write_config_prefs
            api_testo = self.txt_api.text().strip()
            _write_config_prefs('ocr_api_key', api_testo)
            _write_config_prefs('ocr_provider', self.combo_prov.currentIndex())
            _write_config_prefs('ocr_doc_type', self.combo_type.currentText())
            _write_config_prefs('ocr_custom_prompt', self.txt_istruzioni.toPlainText().strip())
            _write_config_prefs('ocr_example_text', self.txt_esempio.toPlainText().strip())
            
            import logging
            logging.info(f"API Key saved. Length: {len(api_testo)}")
        except Exception as e:
            import logging
            logging.error(f"Errore salvataggio OCR settings: {e}")

    def start_ocr(self):
        if not self.file_paths:
            QMessageBox.warning(self, "Attenzione", self.gm("Seleziona almeno un file."))
            return
        # La chiave può venire dalla Cassaforte (rotazione automatica nel worker)
        # ma se non c'è nemmeno quella nel campo, avvertiamo
        prov_str_check = "Gemini"
        if "OpenAI" in self.combo_prov.currentText(): prov_str_check = "OpenAI"
        elif "Anthropic" in self.combo_prov.currentText(): prov_str_check = "Claude"
        from key_manager import KeyManager
        from config_utils import _config_file_path
        if not os.path.exists(_config_file_path()) and not KeyManager().has_keys(prov_str_check):
            QMessageBox.warning(self, "Attenzione", self.gm("Inserisci la API Key valida."))
            return
        if not self.txt_api.text().strip() and not KeyManager().has_keys(prov_str_check):
            QMessageBox.warning(self, "Attenzione", self.gm("Inserisci la API Key valida."))
            return

        fmt = []
        if self.chk_txt.isChecked(): fmt.append("txt")
        if self.chk_docx.isChecked(): fmt.append("docx")
        if self.chk_xml.isChecked(): fmt.append("xml")

        if not fmt:
            QMessageBox.warning(self, "Attenzione", self.gm("Seleziona almeno un formato di output."))
            return

        self.save_settings()

        out_dir = QFileDialog.getExistingDirectory(self, self.gm("Seleziona cartella di destinazione"))
        if not out_dir: return

        prov_str = "Gemini"
        if "OpenAI" in self.combo_prov.currentText(): prov_str = "OpenAI"
        elif "Anthropic" in self.combo_prov.currentText(): prov_str = "Claude"

        # Costruisce il prompt dalla tipologia documentale selezionata
        doc_type = self.combo_type.currentText()
        custom_p = self.txt_istruzioni.toPlainText().strip()
        ex_text = self.txt_esempio.toPlainText().strip()
        try:
            if self._dtm.is_custom(doc_type):
                # Tipo custom: usa il prompt utente, con fallback al generico
                custom_ocr = self._dtm.get_ocr_prompt(doc_type) or ""
                from ocr_prompts import compose_ocr_prompt
                final_prompt = compose_ocr_prompt("Manoscritto Generico / Altro", custom_ocr + ("\n" + custom_p if custom_p else ""), ex_text)
            else:
                from ocr_prompts import compose_ocr_prompt
                final_prompt = compose_ocr_prompt(doc_type, custom_p, ex_text)
        except Exception as e:
            import logging, traceback
            logging.error(f"[OCR] Errore composizione prompt: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Errore Prompt", f"Impossibile costruire il prompt OCR:\n{e}")
            return

        self.btn_start.setEnabled(False)
        self.progress_bar.setValue(0)

        interact = self.chk_interactive.isChecked()
        self.thread = OCRThread(
            self.file_paths, prov_str, self.txt_api.text(),
            fmt, out_dir, self.gm("Elaborazione: "),
            final_prompt, "", interact  # prompt già composto, example_text incluso
        )
        self.thread.review_requested.connect(self.show_review_dialog)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.ocr_finished)
        self.thread.start()

    def load_saved_instruction(self, index):
        if index > 0:
            txt = self.combo_istruzioni.itemData(index)
            self.txt_istruzioni.setText(txt)

    def save_current_instruction(self):
        txt = self.txt_istruzioni.toPlainText().strip()
        if not txt: return
        if txt not in self.saved_instructions_list:
            self.saved_instructions_list.append(txt)
            trunc = txt.replace('\n', ' ')
            if len(trunc) > 40: trunc = trunc[:37] + "..."
            self.combo_istruzioni.addItem(trunc, txt)
            self.combo_istruzioni.setCurrentIndex(self.combo_istruzioni.count() - 1)
            
            try:
                from main_gui_qt import _write_config_prefs
                _write_config_prefs('ocr_saved_prompts', self.saved_instructions_list)
                QMessageBox.information(self, self.gm("Completato"), self.gm("Istruzione salvata nell'archivio."))
            except Exception as e:
                import logging
                logging.error(f"Errore salvataggio prompt archive: {e}")

    def show_review_dialog(self, img_path, raw_text):
        dlg = OCRReviewDialog(img_path, raw_text, self)
        if dlg.exec():
            # Approva -> salviamo il testo modificato
            self.thread.reviewed_text = dlg.txt_editor.toPlainText().strip()
        else:
            # Salta -> restituiamo None
            self.thread.reviewed_text = None
        self.thread.review_event.set()

    def update_progress(self, val, total, msg):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(val)
        self.progress_lbl.setText(msg)

    def ocr_finished(self, success, msg):
        self.btn_start.setEnabled(True)
        if success:
            QMessageBox.information(self, self.gm("Completato"), self.gm(msg))
        else:
            QMessageBox.critical(self, self.gm("Errore"), self.gm(msg))
