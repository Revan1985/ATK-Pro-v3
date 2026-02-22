from PySide6.QtGui import QBrush, QPalette, QPixmap, QIcon
from asset_cache import get_pixmap_cached, get_text_cached
from PySide6.QtCore import Qt, QFile, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox,
    QMenuBar, QMenu, QDialog, QComboBox, QCheckBox, QSizePolicy, QInputDialog
)

# Versione corrente dell'applicazione
VERSION = "2.0.6"
GITHUB_REPO = "DanielePigoli/ATK-Pro-v2"

# Stato globale
state = {
    "records": [],
    "formats": [],
    "output_folder": None,
    "registri_output": [],
    "current_input_file": None  # Memorizza il percorso del file attualmente caricato
}
# Import standard all'inizio
import sys

def carica_testo_asset(percorso):
    try:
        return get_text_cached(percorso)
    except Exception:
        return ""
    except UnicodeDecodeError:
        try:
            return get_text_cached(percorso)
        except Exception:
            return ""


def show_operation_completed_dialog(parent, glossario_data, lingua, risultati=None):
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit
    from PySide6.QtGui import QIcon, QFont
    from PySide6.QtCore import Qt
    try:
        from .main_gui_qt import get_msg, asset_path
    except ImportError:
        from main_gui_qt import get_msg, asset_path

    dlg = QDialog(parent)
    dlg.setWindowTitle(get_msg(glossario_data, "Operazione completata", lingua.upper()))
    try:
        dlg.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
    except Exception:
        pass
    dlg.setStyleSheet("""
        QDialog {
            background-color: #181818;
            color: #fff;
            border: 2px solid #a67c52;
        }
        QLabel, QPushButton {
            color: #fff;
            font-size: 16px;
        }
        QPushButton {
            background-color: #222;
            border: 1px solid #a67c52;
            padding: 6px 18px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #333;
        }
    """)
    layout = QVBoxLayout()
    layout.setContentsMargins(30, 25, 30, 25)
    layout.setSpacing(18)
    msg = QLabel(get_msg(glossario_data, "Operazione completata", lingua.upper()))
    msg.setAlignment(Qt.AlignCenter)
    msg.setStyleSheet("QLabel { background: transparent; color: #fff; font-size: 20px; font-weight: bold; }")
    # Effetto ombra su QLabel
    from PySide6.QtWidgets import QGraphicsDropShadowEffect
    shadow_msg = QGraphicsDropShadowEffect()
    shadow_msg.setBlurRadius(12)
    shadow_msg.setOffset(2, 2)
    shadow_msg.setColor(Qt.black)
    msg.setGraphicsEffect(shadow_msg)
    layout.addWidget(msg)

    # Se risultati è passato, mostra un report dettagliato dei record incompleti
    if risultati:
        report_lines = []
        for rec in risultati:
            if rec.get("status") == "INCOMPLETE":
                report_lines.append(f"<b>{rec.get('file','?')}</b> - <span style='color:#ffb347;'>IMMAGINI MANCANTI</span>")
                tiles = rec.get("tiles_missing") or []
                for t in tiles[:10]:
                    report_lines.append(f"<span style='font-size:12px;'>{t}</span>")
                if len(tiles) > 10:
                    report_lines.append(f"...({len(tiles)-10} altri tile non mostrati)")
        if report_lines:
            report_text = "<br>".join(report_lines)
            report_box = QTextEdit()
            report_box.setReadOnly(True)
            report_box.setHtml(f"<div style='color:#fff;'>{report_text}</div>")
            report_box.setStyleSheet("background-color: #222; color: #fff; font-size: 14px; border: 1px solid #a67c52; border-radius: 6px; padding: 8px;")
            layout.addWidget(report_box)

    ok_btn = QPushButton(get_msg(glossario_data, "Chiudi", lingua.upper()))
    ok_btn.clicked.connect(dlg.accept)
    # Effetto ombra su QPushButton
    shadow_btn = QGraphicsDropShadowEffect()
    shadow_btn.setBlurRadius(16)
    shadow_btn.setOffset(3, 3)
    shadow_btn.setColor(Qt.black)
    ok_btn.setGraphicsEffect(shadow_btn)
    layout.addWidget(ok_btn, alignment=Qt.AlignCenter)
    dlg.setLayout(layout)
    dlg.adjustSize()
    dlg.setFixedSize(dlg.sizeHint())
    dlg.exec()
def get_language_from_registry():
    """Legge la lingua selezionata durante l'installazione dal registro Windows."""
    try:
        import winreg
        reg_path = r"Software\\ATK-Pro"
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
            lang, _ = winreg.QueryValueEx(reg_key, "Language")
            winreg.CloseKey(reg_key)
            logging.debug(f"Lingua letta dal registro: {lang}")
            lingue_valide = ["it", "en", "es", "de", "fr", "pt", "nl", "ar", "he", "ru",
                             "da", "el", "ja", "no", "pl", "ro", "sv", "tr", "vi", "zh"]
            return lang if lang in lingue_valide else "en"
        except FileNotFoundError:
            logging.debug("Chiave registro ATK-Pro non trovata")
            return "en"
    except (ImportError, OSError) as e:
        logging.debug(f"Impossibile leggere registro: {e}")
        return "en"
def asset_path(rel_path):
    return os.path.join(BASE_DIR, rel_path)
from PySide6.QtGui import QBrush, QPalette, QPixmap, QIcon
from asset_cache import get_pixmap_cached, get_text_cached
from PySide6.QtCore import Qt, QFile, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox,
    QMenuBar, QMenu, QDialog, QComboBox, QCheckBox, QSizePolicy, QInputDialog
)
# Stato globale
state = {
    "records": [],
    "formats": [],
    "output_folder": None,
    "registri_output": [],
    "current_input_file": None  # Memorizza il percorso del file attualmente caricato
}
# Import standard all'inizio
import sys

def scegli_lingua(glossario_data=None, lingua="it"):
    dlg = QDialog()
    dlg.resize(460, 180)
    dlg.setWindowTitle(get_msg(glossario_data, "Seleziona lingua", lingua.upper()) if glossario_data else "Seleziona lingua")
    dlg.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
    try:
        _setup_dialog_pergamena(dlg, 460, 180)
    except Exception:
        pass

    layout = QVBoxLayout(dlg)
    label = QLabel(get_msg(glossario_data, "Scegli la lingua dell'interfaccia", lingua.upper()) if glossario_data else "Scegli la lingua dell'interfaccia")

    combo = QComboBox()
    import os
    import locale
    asset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    lingue_supportate = [d for d in os.listdir(asset_dir) if os.path.isdir(os.path.join(asset_dir, d)) and d != "common"]
    nomi_lingue = {
        "it": "Italiano",
        "en": "English",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "pt": "Português",
        "ru": "Русский",
        "ar": "العربية",
        "nl": "Nederlands",
        "he": "עברית",
        "ja": "日本語",
        "zh": "中文",
        "pl": "Polski",
        "tr": "Türkçe",
        "uk": "Українська",
        "cs": "Čeština",
        "el": "Ελληνικά",
        "hu": "Magyar",
        "ro": "Română",
        "sv": "Svenska",
        "vi": "Tiếng Việt",
        "da": "Dansk"
    }
    import locale
    try:
        locale.setlocale(locale.LC_ALL, "")
        sys_locale = locale.getlocale()[0]
    except Exception:
        sys_locale = None
    sys_lang = None
    if sys_locale:
        mapping = {
            'italian': 'it', 'english': 'en', 'german': 'de', 'french': 'fr', 'spanish': 'es',
            'portuguese': 'pt', 'russian': 'ru', 'arabic': 'ar', 'dutch': 'nl', 'hebrew': 'he',
            'japanese': 'ja', 'chinese': 'zh', 'polish': 'pl', 'turkish': 'tr', 'ukrainian': 'uk',
            'czech': 'cs', 'greek': 'el', 'hungarian': 'hu', 'romanian': 'ro', 'swedish': 'sv',
            'vietnamese': 'vi', 'danish': 'da', 'norwegian': 'no'
        }
        if '_' in sys_locale:
            sys_lang = sys_locale.split('_')[0].lower()
        elif '-' in sys_locale:
            sys_lang = sys_locale.split('-')[0].lower()
        elif ' ' in sys_locale:
            sys_lang = sys_locale.split(' ')[0].lower()
        else:
            sys_lang = sys_locale.lower()
        # Normalizza sempre tramite mapping
        sys_lang = mapping.get(sys_lang, sys_lang)
    import logging
    logging.debug(f"[DEBUG LINGUA] sys_locale={sys_locale}, sys_lang={sys_lang}, lingue_supportate={lingue_supportate}")
    # Log dettagliato per selezione
    idx = 0
    if sys_lang and sys_lang in lingue_supportate:
        idx = lingue_supportate.index(sys_lang)
        logging.debug(f"[DEBUG LINGUA] Seleziono sys_lang: {sys_lang} (idx={idx})")
    elif 'en' in lingue_supportate:
        idx = lingue_supportate.index('en')
        logging.debug(f"[DEBUG LINGUA] sys_lang non trovata, seleziono 'en' (idx={idx})")
    else:
        logging.debug(f"[DEBUG LINGUA] sys_lang e 'en' non trovate, seleziono idx=0")
    import logging
    logging.debug(f"[DEBUG LINGUA] sys_locale={sys_locale}, sys_lang={sys_lang}, lingue_supportate={lingue_supportate}")
    for codice in lingue_supportate:
        nome = nomi_lingue.get(codice, codice)
        if codice == "no":
            nome = "Norsk"  # Autonimo norvegese
        combo.addItem(nome, codice)

    # Imposta come default la lingua di sistema se presente, altrimenti su 'en' se esiste
    idx = 0  # Default: prima voce
    if sys_lang and sys_lang in lingue_supportate:
        idx = lingue_supportate.index(sys_lang)
    elif 'en' in lingue_supportate:
        idx = lingue_supportate.index('en')
    combo.setCurrentIndex(idx)

    btns = QHBoxLayout()
    ok_btn = QPushButton(get_msg(glossario_data, "Conferma", lingua.upper()) if glossario_data else "Conferma")
    cancel_btn = QPushButton(get_msg(glossario_data, "Annulla", lingua.upper()) if glossario_data else "Annulla")
    ok_btn.clicked.connect(dlg.accept)
    cancel_btn.clicked.connect(dlg.reject)
    btns.addWidget(ok_btn)
    btns.addWidget(cancel_btn)

    layout.addWidget(label)
    layout.addWidget(combo)
    layout.addLayout(btns)

    if dlg.exec() == QDialog.Accepted:
        return combo.currentData()
    return "en"
import os
import json
import sys
SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import logging
import logging
import elaborazione as elaborazione_mod

from input_loader import load_input_file
from input_parser import parse_input_text

# Inizializzazione BASE_DIR subito dopo gli import
_is_frozen = getattr(sys, 'frozen', False)
if _is_frozen:
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Inizializzazione ASSET_LANG e ASSET_COMMON subito dopo BASE_DIR
ASSET_COMMON = os.path.join(BASE_DIR, "assets", "common")
ASSET_LANG = os.path.join(BASE_DIR, "assets")
# Funzioni di utilità definite subito dopo gli import

def carica_file_esempio(lingua: str) -> str:
    path = os.path.join(ASSET_LANG, lingua, "testuali", "input_link_base_v2.0.txt")
    if not os.path.exists(path):
        path = os.path.join(ASSET_LANG, "en", "testuali", "input_link_base_v2.0.txt")
    return path

def carica_glossario(lang):
    path = os.path.join(BASE_DIR, "docs_generali", "glossario_multilingua_ATK-Pro.json")
    logger = logging.getLogger(__name__)
    try:
        text = get_text_cached(path)
        return json.loads(text)
    except FileNotFoundError:
        show_error(f"Glossario non trovato: {path}", level="warning")
        return {}
    except json.JSONDecodeError as e:
        show_error(f"Errore decodifica JSON nel glossario '{path}': {e}", level="warning")
        return {}
    except Exception as e:
        show_error(f"Errore imprevisto caricando il glossario '{path}': {e}", level="error")
        return {}

def get_msg(glossario, chiave, lingua):
    lingua = lingua.upper()
    if lingua == "DK":
        lingua = "DA"
    if lingua == "VN":
        lingua = "VI"
    # Cerca in tutte le sezioni del glossario
    for section in glossario.values():
        if isinstance(section, list):
            for voce in section:
                if voce.get("messaggio") == chiave:
                    return voce.get(lingua, voce.get("IT", None))
    # Fallback: None se non trovata
    return None
def style_msgbox_pergamena(msgbox, w=820, h=200):
    """Applica lo stile nero/bianco a un QMessageBox, come per i QDialog personalizzati."""
    msgbox.setMinimumSize(w, h)
    msgbox.setStyleSheet("""
        QMessageBox {
            background-color: #181818;
            color: #fff;
            border: 2px solid #a67c52;
        }
        QLabel, QPushButton {
            color: #fff;
            font-size: 15px;
        }
        QPushButton {
            background-color: #222;
            border: 1px solid #a67c52;
            padding: 6px 18px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #333;
        }
    """)
    # Sfondo come _setup_dialog_pergamena
    bg_pixmap = get_pixmap_cached(asset_path("assets/common/grafici/Sfondo.png"))
    if bg_pixmap.isNull():
        bg_pixmap = get_pixmap_cached(asset_path("assets/common/grafici/Sfondo.webp"))
    if not bg_pixmap.isNull():
        scaled_bg = bg_pixmap.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(scaled_bg))
        msgbox.setPalette(palette)


def show_msgbox_localized(parent, glossario_data, lingua, title, text, icon=QMessageBox.Information, buttons=("Conferma",), default="Conferma"):
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
    dlg = QDialog(parent) if parent is not None else QDialog()
    dlg.setWindowTitle(title)
    dlg.setStyleSheet("""
        QDialog {
            background-color: #181818;
            color: #fff;
            border: 2px solid #a67c52;
        }
        QLabel, QPushButton {
            color: #fff;
            font-size: 15px;
        }
        QPushButton {
            background-color: #222;
            border: 1px solid #a67c52;
            padding: 6px 18px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #333;
        }
    """)
    layout = QVBoxLayout(dlg)
    label = QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    label.setWordWrap(True)
    label.setStyleSheet("color: #fff; font-size: 15px;")
    layout.addWidget(label)
    btn_layout = QHBoxLayout()
    btns = []
    for b in buttons:
        btn = QPushButton(b)
        btns.append(btn)
        btn_layout.addWidget(btn)
    layout.addLayout(btn_layout)
    dlg.setLayout(layout)
    # Connessione pulsanti
    result = default
    for i, btn in enumerate(btns):
        def handler(idx=i):
            nonlocal result
            result = buttons[idx]
            dlg.accept()
        btn.clicked.connect(handler)
    dlg.exec()
    return result

# Import standard all'inizio
import sys
import os
import json
import logging
from logging.handlers import RotatingFileHandler
# Configurazione logging IMMEDIATA
_is_frozen = getattr(sys, 'frozen', False)
ATKPRO_ENV = os.environ.get("ATKPRO_ENV", "development").lower()
_log_level = logging.WARNING if _is_frozen or ATKPRO_ENV == "production" else logging.DEBUG
_log_format = "%(levelname)s: %(message)s" if _is_frozen or ATKPRO_ENV == "production" else "DEBUG: %(message)s"
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'atkpro_debug.log')
handlers = [logging.StreamHandler(sys.stdout)]
if ATKPRO_ENV != "production":
    handlers.append(RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'))
logging.basicConfig(level=_log_level, format=_log_format, handlers=handlers)
logging.info('TEST LOG INIZIO FILE')

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox,
    QMenuBar, QMenu, QDialog, QComboBox, QCheckBox, QSizePolicy
)
from PySide6.QtGui import QFontDatabase

class MainWindow(QMainWindow):
    def cambia_lingua(self):
        nuova_lingua = scegli_lingua(self.glossario_data, self.lingua)
        if nuova_lingua and nuova_lingua != self.lingua:
            self.lingua = nuova_lingua
            # Salva la lingua nel registro di Windows
            try:
                import winreg
                reg_path = r"Software\\ATK-Pro"
                reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                winreg.SetValueEx(reg_key, "Language", 0, winreg.REG_SZ, self.lingua)
                winreg.CloseKey(reg_key)
            except Exception as e:
                import logging
                logging.warning(f"Impossibile salvare la lingua nel registro: {e}")
            show_operation_completed_dialog(self, self.glossario_data, self.lingua)
            # Dialog stile "Funzione in sviluppo"
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
            dlg = QDialog(self)
            dlg.setWindowTitle(get_msg(self.glossario_data, "Riavvio richiesto", self.lingua) or "Riavvio richiesto")
            _setup_dialog_pergamena(dlg, 600, 250)
            layout = QVBoxLayout(dlg)
            msg = get_msg(self.glossario_data, "Riavvio richiesto", self.lingua)
            if not msg or msg == "Riavvio richiesto":
                msg = "Per applicare la modifica della lingua è necessario riavviare l'applicazione."
            label = QLabel(msg)
            label.setStyleSheet("color: #fff; font-size: 16px;")
            layout.addWidget(label)
            ok_btn = QPushButton(get_msg(self.glossario_data, "Chiudi", self.lingua) or "Chiudi")
            ok_btn.clicked.connect(dlg.accept)
            layout.addWidget(ok_btn)
            dlg.setLayout(layout)
            dlg.exec()

    def verifica_aggiornamenti(self):
        """Controlla se è disponibile una nuova versione su GitHub"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        from PySide6.QtCore import QTimer
        import urllib.request
        import json
        
        # Esegui la verifica prima di mostrare il dialogo
        result_msg = ""
        result_color = "#FFFFFF"
        show_download_btn = False
        release_url = ""
        
        try:
            # Richiesta all'API di GitHub
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'ATK-Pro')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get('tag_name', '').lstrip('v')
                release_name = data.get('name', '')
                release_url = data.get('html_url', '')
                
                # Confronta versioni
                current = VERSION.split('.')
                latest = latest_version.split('.')
                
                is_newer = False
                for i in range(max(len(current), len(latest))):
                    c = int(current[i]) if i < len(current) else 0
                    l = int(latest[i]) if i < len(latest) else 0
                    if l > c:
                        is_newer = True
                        break
                    elif l < c:
                        break
                
                if is_newer:
                    result_msg = (f"{get_msg(self.glossario_data, 'Nuova versione disponibile', self.lingua) or 'Nuova versione disponibile'}!\n\n"
                                 f"{get_msg(self.glossario_data, 'Versione corrente', self.lingua) or 'Versione corrente'}: {VERSION}\n"
                                 f"{get_msg(self.glossario_data, 'Ultima versione', self.lingua) or 'Ultima versione'}: {latest_version}")
                    if release_name:
                        result_msg += f"\n\n{release_name}"
                    show_download_btn = True
                else:
                    result_msg = (f"{get_msg(self.glossario_data, 'Nessun aggiornamento disponibile', self.lingua) or 'Nessun aggiornamento disponibile'}\n\n"
                                 f"{get_msg(self.glossario_data, 'Versione corrente', self.lingua) or 'Versione corrente'}: {VERSION}")
                    
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Nessuna release pubblicata su GitHub
                result_msg = (f"{get_msg(self.glossario_data, 'Nessun aggiornamento disponibile', self.lingua) or 'Nessun aggiornamento disponibile'}\n\n"
                             f"{get_msg(self.glossario_data, 'Versione corrente', self.lingua) or 'Versione corrente'}: {VERSION}\n\n"
                             f"({get_msg(self.glossario_data, 'Nessuna release pubblicata', self.lingua) or 'Nessuna release pubblicata su GitHub'})")
            else:
                result_msg = f"{get_msg(self.glossario_data, 'Errore verifica aggiornamenti', self.lingua) or 'Errore durante la verifica degli aggiornamenti'}\n\nHTTP {e.code}"
                result_color = "#FFB347"
                    
        except Exception as e:
            result_msg = f"{get_msg(self.glossario_data, 'Errore verifica aggiornamenti', self.lingua) or 'Errore durante la verifica degli aggiornamenti'}\n\n{str(e)}"
            result_color = "#FFB347"
        
        # Mostra il dialogo con il risultato
        dlg = QDialog(self)
        dlg.setWindowTitle(get_msg(self.glossario_data, "Verifica aggiornamenti", self.lingua) or "Verifica aggiornamenti")
        dlg.setStyleSheet("""
            QDialog {
                background-color: #181818;
                color: #fff;
                border: 2px solid #a67c52;
            }
            QLabel, QPushButton {
                color: #fff;
                font-size: 16px;
            }
            QPushButton {
                background-color: #222;
                border: 1px solid #a67c52;
                padding: 6px 18px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(18)
        
        msg_label = QLabel(result_msg)
        msg_label.setStyleSheet(f"QLabel {{ background: transparent; color: {result_color}; font-size: 16px; }}")
        msg_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(msg_label)
        
        if show_download_btn:
            download_btn = QPushButton(get_msg(self.glossario_data, "Scarica aggiornamento", self.lingua) or "Scarica aggiornamento")
            download_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(release_url)))
            layout.addWidget(download_btn, alignment=Qt.AlignCenter)
        
        close_btn = QPushButton(get_msg(self.glossario_data, "Chiudi", self.lingua) or "Chiudi")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        
        dlg.setLayout(layout)
        dlg.exec()
    
    def __init__(self, glossario_data, lingua):
        super().__init__()
        self.glossario_data = glossario_data
        self.lingua = lingua

        # Ripristina titlebar nativa
        self.setWindowTitle("ATK-Pro")

        # Riga marrone sopra il motto e motto in fondo (widget assoluti)
        self.motto_separator = QLabel(self)
        self.motto_separator.setFixedHeight(4)
        self.motto_separator.setStyleSheet("background: #a67c52;")
        self.motto_separator.raise_()

        motto_path = asset_path("assets/common/testuali/Motto_latino.txt")
        try:
            with open(motto_path, "r", encoding="utf-8") as f:
                motto = f.read().strip()
        except Exception:
            motto = ""
        self.motto_label = QLabel(motto, self)
        self.motto_label.setObjectName("motto_label")
        self.motto_label.setAlignment(Qt.AlignCenter)
        # Stile motto originale: sfondo bianco, testo marrone
        self.motto_label.setStyleSheet(
            "background: #fff; color: #482e1a; font-weight: bold; padding: 4px 0; border-top: 2px solid #a67c52; "
            "font-size: 18px; font-family: 'Segoe UI', 'Arial', sans-serif; border-bottom: none; opacity: 1;"
        )
        self.motto_label.raise_()

        self.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
        self.resize(960, 700)
        # Rollback: nessuno stile trasparente su QMainWindow


        # MENU COMPLETO secondo guida.html (localizzato)
        menubar = self.menuBar()
        gm = lambda chiave: get_msg(self.glossario_data, chiave, self.lingua) or chiave

        # --- File input ---
        file_menu = QMenu(gm("File input"), self)
        file_menu.addAction(gm("Esempio input"), self.mostra_esempio_input)
        file_menu.addAction(gm("Apri input"), self.apri_input)
        file_menu.addAction(gm("Modifica input"), self.modifica_input)
        menubar.addMenu(file_menu)

        # --- Output ---
        output_menu = QMenu(gm("Output"), self)
        output_menu.addAction(gm("Elabora"), self.elabora_output)
        output_menu.addAction(gm("Apri cartella output"), self.apri_cartella_output)
        output_menu.addAction(gm("Visualizza elaborazioni precedenti"), self.visualizza_elaborazioni_precedenti)
        menubar.addMenu(output_menu)

        # --- Servizi ---
        servizi_menu = QMenu(gm("Servizi"), self)
        servizi_menu.addAction(gm("Integrazione API Portale Antenati"), self.funzione_in_sviluppo)
        servizi_menu.addAction(gm("Visualizzazione Immagini"), self.funzione_in_sviluppo)
        servizi_menu.addAction(gm("Visualizzazione Metadati JSON"), self.funzione_in_sviluppo)
        servizi_menu.addAction(gm("OCR Avanzato"), self.funzione_in_sviluppo)
        servizi_menu.addAction(gm("Traduzione OCR"), self.funzione_in_sviluppo)
        servizi_menu.addAction(gm("Esportazione GEDCOM"), self.funzione_in_sviluppo)
        menubar.addMenu(servizi_menu)

        # --- Documenti ---
        documenti_menu = QMenu(gm("Documenti"), self)
        documenti_menu.addAction(gm("Disclaimer"), self.mostra_disclaimer)
        documenti_menu.addAction(gm("Presentazione autore"), self.mostra_autore)
        documenti_menu.addAction(gm("Presentazione progetto"), self.mostra_progetto)
        documenti_menu.addAction(gm("Guida"), self.mostra_guida)
        documenti_menu.addAction(gm("Informazioni"), self.mostra_info)
        menubar.addMenu(documenti_menu)

        # --- Impostazioni ---
        impostazioni_menu = QMenu(gm("Impostazioni"), self)
        impostazioni_menu.addAction(gm("Cambia lingua"), self.cambia_lingua)
        impostazioni_menu.addAction(gm("Seleziona formati immagine"), self.seleziona_formati_immagine)
        impostazioni_menu.addAction(gm("Seleziona cartella output"), self.seleziona_cartella_output)
        impostazioni_menu.addAction(gm("Esporta configurazione"), self.esporta_configurazione)
        impostazioni_menu.addAction(gm("Importa configurazione"), self.importa_configurazione)
        impostazioni_menu.addAction(gm("Verifica aggiornamenti"), self.verifica_aggiornamenti)
        impostazioni_menu.addAction(gm("Chiudi"), self.close)
        menubar.addMenu(impostazioni_menu)

        # Stile menubar originale (nessuna forzatura colore bianco sulle voci)
        menubar.setStyleSheet("QMenuBar { background: #d2bb8a; color: #222; font-weight: bold; border: none; } "
                  "QMenuBar::item:selected { background: #e5d3b3; color: #222; } "
                  "QMenu { background: #f5e6c3; color: #222; } ")

        # Riga marrone sotto il menu (widget separato, non nel layout centrale)
        self.menu_separator = QLabel(self)
        self.menu_separator.setFixedHeight(4)
        self.menu_separator.setStyleSheet("background: #a67c52;")
        self.menu_separator.setGeometry(0, menubar.height(), self.width(), 4)
        self.menu_separator.raise_()
        self.menuBar().installEventFilter(self)

        # LAYOUT CENTRALE
        central = QWidget()
        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(0)
        central.setLayout(vlayout)
        self.setCentralWidget(central)

        # Sfondo pergamena responsivo
        self.bg_label = QLabel(self)
        bg_pixmap = get_pixmap_cached(asset_path("assets/common/grafici/Sfondo.png"))
        if bg_pixmap.isNull():
            bg_pixmap = get_pixmap_cached(asset_path("assets/common/grafici/Sfondo.webp"))
        self.bg_pixmap = bg_pixmap
        self.bg_label.setPixmap(self.bg_pixmap)
        self.bg_label.setScaledContents(True)
        self.bg_label.lower()
        self.bg_label.setGeometry(0, 0, self.width(), self.height())

        # Logo centrale proporzionato
        self.logo_label = QLabel(central)
        logo_pixmap = get_pixmap_cached(asset_path("assets/common/grafici/Logo.webp"))
        if logo_pixmap.isNull():
            logo_pixmap = get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro-logo.png"))
        self.logo_pixmap = logo_pixmap
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setScaledContents(True)
        self.logo_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.logo_label.setStyleSheet("background: transparent;")
        vlayout.addStretch(1)
        vlayout.addWidget(self.logo_label, alignment=Qt.AlignCenter)
        vlayout.addStretch(1)

        # Applica stile bianco a tutti i QPushButton della finestra principale
        self.setStyleSheet(self.styleSheet() + "\nQPushButton { background-color: #222; color: #fff; border: 1px solid #a67c52; padding: 6px 18px; border-radius: 6px; font-size: 15px; font-weight: bold; } QPushButton:hover { background-color: #333; }")
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Sfondo
        if hasattr(self, 'bg_label') and hasattr(self, 'bg_pixmap'):
            self.bg_label.setGeometry(0, 0, self.width(), self.height())
            self.bg_label.setPixmap(self.bg_pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        # Logo proporzionato (max 40% larghezza, max 30% altezza)
        if hasattr(self, 'logo_label') and hasattr(self, 'logo_pixmap'):
            w = int(self.width() * 0.4)
            h = int(self.height() * 0.3)
            scaled = self.logo_pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
        # Aggiorna larghezza separatore menu
        if hasattr(self, 'menu_separator'):
            self.menu_separator.setGeometry(0, self.menuBar().height(), self.width(), 4)
        # Motto e separatore in fondo (senza riga in calce)
        if hasattr(self, 'motto_separator') and hasattr(self, 'motto_label'):
            motto_h = self.motto_label.sizeHint().height()
            sep_h = self.motto_separator.height()
            self.motto_separator.setGeometry(0, self.height() - motto_h - sep_h, self.width(), sep_h)
            self.motto_label.setGeometry(0, self.height() - motto_h, self.width(), motto_h)

    # --- Placeholder per azioni menu ---

    def mostra_esempio_input(self):
        # Collega al flusso reale
        action_show_example_input(self.glossario_data, self.lingua, self)


    def apri_input(self):
        action_open_input(self.glossario_data, self.lingua, self)


    def modifica_input(self):
        action_modify_input(self.glossario_data, self.lingua, self)

    def elabora_output(self):

        records = state.get("records") or []
        formats = state.get("formats") or []
        glossario = self.glossario_data
        lingua = self.lingua
        output_folders_doc = state.get('output_folders_doc', [])
        output_folders_reg = state.get('output_folders_reg', [])

        # Blocca se nessuna cartella valida
        if not (output_folders_doc and len(output_folders_doc) > 0) and not (output_folders_reg and len(output_folders_reg) > 0):
            show_msgbox_localized(
                self,
                glossario,
                lingua,
                "Cartella output",
                "Devi selezionare almeno una cartella di output valida per documenti o registri. Nessun file verrà salvato.",
                icon=QMessageBox.Warning
            )
            return

        # Conta i record per modalità
        doc_indices = [i for i, r in enumerate(records) if str(r.get('modalita', '')).strip().upper() == 'D']
        reg_indices = [i for i, r in enumerate(records) if str(r.get('modalita', '')).strip().upper() == 'R']
        if len(output_folders_doc) != len(doc_indices):
            show_msgbox_localized(self, glossario, lingua, "ATK-Pro", f"Numero di cartelle documento selezionate ({len(output_folders_doc)}) diverso dal numero di record documento ({len(doc_indices)}).", QMessageBox.Critical, buttons=("Conferma",), default="Conferma")
            return
        if len(output_folders_reg) != len(reg_indices):
            show_msgbox_localized(self, glossario, lingua, "ATK-Pro", f"Numero di cartelle registro selezionate ({len(output_folders_reg)}) diverso dal numero di record registro ({len(reg_indices)}).", QMessageBox.Critical, buttons=("Conferma",), default="Conferma")
            return

        doc_counter = 0
        reg_counter = 0
        for rec in records:
            try:
                modalita = str(rec.get('modalita', '')).strip().upper()
            except Exception:
                modalita = ''
            out_dir = None
            if modalita == 'D':
                out_dir = output_folders_doc[doc_counter]
                doc_counter += 1
            elif modalita == 'R':
                out_dir = output_folders_reg[reg_counter]
                reg_counter += 1
            else:
                show_msgbox_localized(self, glossario, lingua, "ATK-Pro", f"Modalità record non riconosciuta: {modalita}", QMessageBox.Critical, buttons=("Conferma",), default="Conferma")
                return
            try:
                rec['output'] = out_dir
            except Exception:
                pass

        import traceback
        try:
            if not records:
                return
            if not formats:
                return

            # Import dinamico per evitare problemi di import circolare
            import elaborazione
            from user_prompts import ProgressDialog
            from qt_worker import ElaborazioneWorker
            from PySide6.QtCore import QCoreApplication

            records = state["records"]
            formats = state["formats"]
            glossario = self.glossario_data
            lingua = self.lingua

            progress_dialog = ProgressDialog(glossario, lingua, total=len(records), parent=self)
            worker = ElaborazioneWorker(records, formats, glossario, lingua)

            def on_progress(cur, tot, name, page, page_total):
                import re
                if name:
                    name = re.sub(r'—?\s*pag\.\s*\d+\s*$', '', name).strip()
                progress_dialog.update(cur, name, page, page_total)
                QCoreApplication.processEvents()

            def on_cancel():
                worker.cancel()
                progress_dialog.close()

            progress_dialog.cancel_btn.clicked.disconnect()
            progress_dialog.cancel_btn.clicked.connect(on_cancel)
            worker.signals.progress.connect(on_progress)

            def on_need_pdf(idx, name):
                from user_prompts import ask_generate_pdf
                import logging
                from PySide6.QtCore import QTimer
                logger = logging.getLogger("pdf_prompt")
                logger.info(f"[PDF_PROMPT] Richiesta conferma PDF per idx={idx} name={name}")
                result_holder = {"res": None}
                def show_prompt():
                    logger.info(f"[PDF_PROMPT] Mostro dialog PDF per idx={idx} name={name}")
                    progress_dialog.close()
                    try:
                        # Forza stile scuro nella dialog PDF
                        res = ask_generate_pdf(glossario, lingua, parent=self, dark_mode=True)
                        logger.info(f"[PDF_PROMPT] Dialog PDF risposta: {res}")
                    except Exception as e:
                        logger.error(f"[PDF_PROMPT] Errore dialog PDF: {e}")
                        res = False
                    result_holder["res"] = res
                    progress_dialog.show()
                QTimer.singleShot(0, show_prompt)
                import time
                start = time.time()
                while result_holder["res"] is None and (time.time() - start) < 120:
                    from PySide6.QtWidgets import QApplication
                    QApplication.processEvents()
                    time.sleep(0.05)
                logger.info(f"[PDF_PROMPT] Risposta PDF idx={idx}: {result_holder['res']}")
                records[idx]["gen_pdf"] = bool(result_holder["res"])
                # RIMOSSA la chiamata a show_operation_completed_dialog qui

            worker.signals.need_pdf_confirmation.connect(on_need_pdf)

            progress_dialog.show()
            worker.start()
            operazione_completata = True
            while worker.isRunning():
                QCoreApplication.processEvents()
                if progress_dialog.cancelled:
                    worker.cancel()
                    worker.terminate()
                    progress_dialog.close()
                    operazione_completata = False
                    break
            # Chiudi subito la dialog di progresso appena il worker termina
            progress_dialog.close()
            # Mostra la finestra "Operazione completata" SOLO qui, dopo tutto (PDF incluso)
            if operazione_completata:
                try:
                    # Recupera risultati batch
                    risultati = None
                    try:
                        risultati = worker.results if hasattr(worker, 'results') else None
                    except Exception:
                        risultati = None
                    # Se non disponibili dal worker, prova a ricaricare da stato globale
                    if not risultati and hasattr(elaborazione, 'esegui_elaborazione'):
                        try:
                            risultati = elaborazione.esegui_elaborazione(state, glossario, lingua, records, formats)
                        except Exception:
                            risultati = None
                    show_operation_completed_dialog(self, self.glossario_data, self.lingua, risultati=risultati)
                except Exception as e:
                    logging.warning(f"Impossibile mostrare dialog operazione completata: {e}")
        except Exception as e:
            logging.error(f"Errore durante l'elaborazione: {e}\n{traceback.format_exc()}")
            try:
                show_operation_completed_dialog(self, self.glossario_data, self.lingua)
            except Exception as ex:
                logging.warning(f"Impossibile mostrare dialog operazione completata dopo errore: {ex}")
            show_msgbox_localized(self, self.glossario_data, self.lingua, "Errore", f'{get_msg(self.glossario_data, "Errore durante l'elaborazione", self.lingua)}: {str(e)}', icon=QMessageBox.Critical)


    def apri_cartella_output(self):
        folder = state.get("output_folder")
        if not folder or not os.path.isdir(folder):
            show_msgbox_localized(self, self.glossario_data, self.lingua, "Cartella output", "Nessuna cartella output selezionata o non esistente.", icon=QMessageBox.Warning)
            return
        import platform
        if platform.system() == "Windows":
            os.startfile(folder)
        elif platform.system() == "Darwin":
            os.system(f"open '{folder}'")
        else:
            os.system(f"xdg-open '{folder}'")
        # Usa dialogo stile "Operazione completata"
        show_operation_completed_dialog(self, self.glossario_data, self.lingua)

    def visualizza_elaborazioni_precedenti(self):
        import os
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem
        from PySide6.QtCore import Qt, QUrl
        from PySide6.QtGui import QCursor
        from PySide6.QtGui import QDesktopServices
        folder = state.get("output_folder")
        if not folder or not os.path.isdir(folder):
            show_operation_completed_dialog(self, self.glossario_data, self.lingua)
            return
        # Ricerca ricorsiva di file rilevanti
        estensioni = ('.json', '.pdf', '.png', '.jpg', '.jpeg', '.txt')
        files = []
        for root, _, filenames in os.walk(folder):
            for f in filenames:
                if f.lower().endswith(estensioni):
                    rel_path = os.path.relpath(os.path.join(root, f), folder)
                    files.append(rel_path)
        # Finestra riepilogativa stile scuro, omogenea alle altre
        dlg = QDialog(self)
        dlg.setWindowTitle(get_msg(self.glossario_data, "Visualizza elaborazioni precedenti", self.lingua) or "Elaborazioni precedenti")
        dlg.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        dlg.resize(700, 500)
        dlg.setStyleSheet("""
            QDialog {
                background-color: #181818;
                color: #fff;
                border: 2px solid #a67c52;
            }
            QTextEdit {
                background-color: #222;
                color: #fff;
                font-size: 15px;
                border: 1px solid #a67c52;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton {
                background-color: #222;
                color: #fff;
                border: 1px solid #a67c52;
                padding: 6px 18px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        layout = QVBoxLayout(dlg)
        if files:
            list_widget = QListWidget()
            list_widget.setStyleSheet("background-color: #222; color: #fff; font-size: 15px; border: 1px solid #a67c52; border-radius: 6px; padding: 8px;")
            for rel_path in files:
                item = QListWidgetItem(rel_path)
                item.setToolTip(rel_path)
                list_widget.addItem(item)
            def open_file(item):
                abs_path = os.path.abspath(os.path.join(folder, item.text()))
                QDesktopServices.openUrl(QUrl.fromLocalFile(abs_path))
            list_widget.itemClicked.connect(open_file)
            layout.addWidget(list_widget)
        else:
            from PySide6.QtWidgets import QLabel
            msg = get_msg(self.glossario_data, "Nessuna elaborazione trovata", self.lingua)
            if not msg or msg == "Nessuna elaborazione trovata":
                msg = "Nessuna elaborazione precedente trovata nella cartella selezionata."
            label = QLabel(msg)
            label.setStyleSheet("color: #fff; font-size: 15px;")
            layout.addWidget(label)
        ok_btn = QPushButton(get_msg(self.glossario_data, "Chiudi", self.lingua) or "Chiudi")
        ok_btn.clicked.connect(dlg.accept)
        layout.addWidget(ok_btn, alignment=Qt.AlignCenter)
        dlg.setLayout(layout)
        dlg.exec()

    def funzione_in_sviluppo(self):
        # Messaggio placeholder localizzato per tutte le voci Servizi
        msg = get_msg(self.glossario_data, "Funzione in sviluppo", self.lingua)
        if not msg or msg == "Funzione in sviluppo":
            msg = "Questa funzione è in sviluppo."
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        dlg = QDialog(self)
        dlg.setWindowTitle(get_msg(self.glossario_data, "Funzione in sviluppo", self.lingua) or "Funzione in sviluppo")
        dlg.setStyleSheet("""
            QDialog {
                background-color: #181818;
                color: #fff;
                border: 2px solid #a67c52;
            }
            QLabel, QPushButton {
                color: #fff;
                font-size: 16px;
            }
            QPushButton {
                background-color: #222;
                border: 1px solid #a67c52;
                padding: 6px 18px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        layout = QVBoxLayout(dlg)
        label = QLabel(msg)
        label.setStyleSheet("color: #fff; font-size: 16px;")
        layout.addWidget(label)
        ok_btn = QPushButton(get_msg(self.glossario_data, "Chiudi", self.lingua) or "Chiudi")
        ok_btn.clicked.connect(dlg.accept)
        layout.addWidget(ok_btn, alignment=Qt.AlignCenter)
        dlg.setLayout(layout)
        dlg.exec()

    def mostra_disclaimer(self):
        percorso_html = asset_path(f"assets/{self.lingua}/testuali/disclaimer_legale_ATK-Pro.html")
        percorso_txt = asset_path(f"assets/{self.lingua}/testuali/disclaimer_legale_ATK-Pro.txt")
        try:
            if os.path.exists(percorso_html):
                self._mostra_html("Disclaimer", percorso_html)
            else:
                msg = get_msg(self.glossario_data, "Disclaimer non disponibile", self.lingua)
                testo = carica_testo_asset(percorso_txt) or msg or "Disclaimer non disponibile."
                self._mostra_testo_lungo("Disclaimer", testo)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            msg = get_msg(self.glossario_data, "Impossibile aprire il disclaimer", self.lingua)
            QMessageBox.critical(self, get_msg(self.glossario_data, "Errore", self.lingua) or "Errore", msg or f"Impossibile aprire il disclaimer: {e}")

    def mostra_autore(self):
        percorso_html = asset_path(f"assets/{self.lingua}/testuali/presentazione_autore.html")
        percorso_txt = asset_path(f"assets/{self.lingua}/testuali/presentazione_autore.txt")
        if os.path.exists(percorso_html):
            self._mostra_html("Presentazione autore", percorso_html)
        else:
            msg = get_msg(self.glossario_data, "Presentazione autore non disponibile", self.lingua)
            testo = carica_testo_asset(percorso_txt) or msg or "Presentazione autore non disponibile."
            self._mostra_testo_lungo("Presentazione autore", testo)

    def mostra_progetto(self):
        percorso_html = asset_path(f"assets/{self.lingua}/testuali/presentazione_progetto_ATK-Pro.html")
        percorso_md = asset_path(f"assets/{self.lingua}/testuali/presentazione_progetto_ATK-Pro.md")
        if os.path.exists(percorso_html):
            self._mostra_html("Presentazione progetto", percorso_html)
        else:
            msg = get_msg(self.glossario_data, "Presentazione progetto non disponibile", self.lingua)
            testo = carica_testo_asset(percorso_md) or msg or "Presentazione progetto non disponibile."
            self._mostra_testo_lungo("Presentazione progetto", testo)

    def mostra_guida(self):
        percorso_html = asset_path(f"assets/{self.lingua}/testuali/guida.html")
        percorso_txt = asset_path(f"assets/{self.lingua}/testuali/guida.txt")
        if os.path.exists(percorso_html):
            self._mostra_html("Guida", percorso_html)
        else:
            msg = get_msg(self.glossario_data, "Guida non disponibile", self.lingua)
            testo = carica_testo_asset(percorso_txt) or msg or "Guida non disponibile."
            self._mostra_testo_lungo("Guida", testo)

    def mostra_info(self):
        # Mostra tre righe testuali come richiesto, stile "Operazione completata"
        email_path = asset_path("assets/common/testuali/email.txt")
        try:
            with open(email_path, "r", encoding="utf-8") as f:
                email = f.read().strip()
        except Exception:
            email = "info@atk-pro.org"
        righe = [f"ATK-Pro v{VERSION}", "©2026 Daniele Pigoli", email]
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        dlg = QDialog(self)
        dlg.setWindowTitle(get_msg(self.glossario_data, "Informazioni", self.lingua) or "Informazioni")
        dlg.setStyleSheet("""
            QDialog {
                background-color: #181818;
                color: #fff;
                border: 2px solid #a67c52;
            }
            QLabel, QPushButton {
                color: #fff;
                font-size: 16px;
            }
            QPushButton {
                background-color: #222;
                border: 1px solid #a67c52;
                padding: 6px 18px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        layout = QVBoxLayout(dlg)
        for riga in righe:
            lbl = QLabel(riga)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("QLabel { background: transparent; color: #FFFFFF; font-size: 16px; }")
            layout.addWidget(lbl)
        btn = QPushButton(get_msg(self.glossario_data, "Chiudi", self.lingua) or "Chiudi")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        dlg.setLayout(layout)
        dlg.exec()

    def _mostra_html(self, titolo, percorso_html):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtCore import QUrl, Qt
        from PySide6.QtGui import QIcon
        dlg = QDialog(self)
        dlg.setWindowTitle(titolo)
        dlg.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
        dlg.resize(900, 700)
        dlg.setMinimumSize(600, 400)
        dlg.setSizeGripEnabled(True)
        # Aggiungi pulsanti di sistema (max/min/close)
        dlg.setWindowFlags(dlg.windowFlags() | Qt.Window | Qt.WindowMinMaxButtonsHint)
        layout = QVBoxLayout(dlg)
        try:
            web = QWebEngineView()
            url = QUrl.fromLocalFile(os.path.abspath(percorso_html))
            web.load(url)
            layout.addWidget(web)
        except Exception as e:
            from PySide6.QtWidgets import QLabel
            layout.addWidget(QLabel(f"Errore caricamento HTML: {e}"))
        # Pulsanti di controllo in basso
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_close = QPushButton(get_msg(self.glossario_data, "Chiudi", self.lingua) or "Chiudi")
        btn_close.clicked.connect(dlg.accept)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        dlg.setLayout(layout)
        dlg.exec()

    def _mostra_info_centrata(self, info_html=None):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
        dlg = QDialog(self)
        dlg.setWindowTitle(get_msg(self.glossario_data, "Informazioni", self.lingua) or "Informazioni")
        dlg.setMinimumSize(500, 250)
        layout = QVBoxLayout(dlg)
        label = QLabel(info_html or "")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        dlg.exec()
    def _mostra_testo_lungo(self, titolo, testo):
        dlg = QDialog(self)
        dlg.setWindowTitle(titolo)
        dlg.resize(700, 500)
        dlg.setStyleSheet("QDialog { background: #fff; } QTextEdit { background: #fff; color: #222; font-size: 15px; }")
        layout = QVBoxLayout(dlg)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(testo)
        layout.addWidget(text)
        btn = QPushButton(get_msg(self.glossario_data, "Chiudi", self.lingua) or "Chiudi")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)

    def seleziona_formati_immagine(self):
        scelti = ask_image_formats(self.glossario_data, self.lingua)
        if scelti:
            state["formats"] = scelti

    def seleziona_cartella_output(self):
        # Attiva la selezione multipla per documenti e registri
        action_select_output(self.glossario_data, self.lingua)

    def esporta_configurazione(self):
        import os
        documents_dir = os.path.join(os.path.expanduser("~"), "Documents", "ATK-Pro")
        os.makedirs(documents_dir, exist_ok=True)
        default_path = os.path.join(documents_dir, "configurazione.json")
        path, _ = QFileDialog.getSaveFileName(self, get_msg(self.glossario_data, "Esporta configurazione", self.lingua.upper()), default_path, "JSON Files (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            # Mostra contenuto file salvato
            with open(path, "r", encoding="utf-8") as f:
                contenuto = f.read()
            dlg = QDialog(self)
            dlg.setWindowTitle(get_msg(self.glossario_data, "Operazione completata", self.lingua) or "Configurazione esportata")
            _setup_dialog_pergamena(dlg, 700, 500)
            layout = QVBoxLayout(dlg)
            text = QTextEdit()
            text.setReadOnly(True)
            text.setPlainText(contenuto)
            layout.addWidget(text)
            ok_btn = QPushButton(get_msg(self.glossario_data, "Chiudi", self.lingua) or "Chiudi")
            ok_btn.clicked.connect(dlg.accept)
            layout.addWidget(ok_btn, alignment=Qt.AlignCenter)
            dlg.setLayout(layout)
            dlg.exec()

    def importa_configurazione(self):
        import os
        documents_dir = os.path.join(os.path.expanduser("~"), "Documents", "ATK-Pro")
        os.makedirs(documents_dir, exist_ok=True)
        default_path = os.path.join(documents_dir, "configurazione.json")
        path, _ = QFileDialog.getOpenFileName(self, get_msg(self.glossario_data, "Importa configurazione", self.lingua.upper()), default_path, "JSON Files (*.json)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                dati = json.load(f)
                state.update(dati)
                contenuto = json.dumps(dati, ensure_ascii=False, indent=2)
            # Aggiorna la UI dopo l'import
            if hasattr(self, "aggiorna_ui_da_state"):
                self.aggiorna_ui_da_state()
            # Mostra contenuto file importato con stile SCURO
            dlg = QDialog(self)
            dlg.setWindowTitle(get_msg(self.glossario_data, "Operazione completata", self.lingua) or "Configurazione importata")
            _setup_dialog_pergamena(dlg, 700, 500)
            # Forza stile SCURO anche sulla dialog
            dlg.setStyleSheet("QDialog { background-color: #181818; }")
            layout = QVBoxLayout(dlg)
            text = QTextEdit()
            text.setReadOnly(True)
            text.setPlainText(contenuto)
            text.setStyleSheet("background-color: #181818; color: #fff; font-size: 15px; border: 1px solid #a67c52;")
            layout.addWidget(text)
            ok_btn = QPushButton(get_msg(self.glossario_data, "Chiudi", self.lingua) or "Chiudi")
            ok_btn.setStyleSheet("background-color: #222; color: #fff; border: 1px solid #a67c52; padding: 8px 24px; border-radius: 8px; font-size: 15px; font-weight: bold;")
            ok_btn.clicked.connect(dlg.accept)
            layout.addWidget(ok_btn, alignment=Qt.AlignCenter)
            dlg.setLayout(layout)
            dlg.exec()


def _setup_dialog_pergamena(dlg, w=900, h=650, use_old_bg=False):
    dlg.resize(w, h)
    dlg.setStyleSheet("QDialog { background: transparent; }")
    dlg.setAutoFillBackground(True)

    bg_pixmap = QPixmap(asset_path("assets/common/grafici/Sfondo.webp"))
    if not bg_pixmap.isNull():
        scaled_bg = bg_pixmap.scaled(dlg.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(scaled_bg))
        dlg.setPalette(palette)


def _styled_text_edit(read_only=True, initial_text=""):
    text = QTextEdit()
    text.setReadOnly(read_only)
    if initial_text:
        text.setPlainText(initial_text)
    text.setStyleSheet("""
        QTextEdit {
            background-color: rgba(255, 255, 255, 220);  /* overlay chiaro */
            color: #000000;
            border: none;
            font-size: 14px;
        }
    """)
    return text


def mostra_disclaimer(glossario_data, lingua):
    disclaimer_path = os.path.join(ASSET_LANG, lingua, "testuali", "disclaimer_legale_ATK-Pro.txt")
    msg = get_msg(glossario_data, "Disclaimer non disponibile", lingua.upper())
    disclaimer_text = carica_testo_asset(disclaimer_path) or msg or "Disclaimer non disponibile"

    dlg = QDialog()
    dlg.setWindowTitle(get_msg(glossario_data, "Disclaimer", lingua.upper()))
    dlg.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
    dlg.setStyleSheet("""
        QDialog {
            background-color: #181818;
            color: #fff;
            border: 2px solid #a67c52;
        }
        QLabel, QPushButton {
            color: #fff;
            font-size: 15px;
        }
        QPushButton {
            background-color: #222;
            border: 1px solid #a67c52;
            padding: 6px 18px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #333;
        }
    """)
    dlg.resize(900, 650)

    layout = QVBoxLayout(dlg)
    text = _styled_text_edit(read_only=True, initial_text=disclaimer_text)
    layout.addWidget(text)

    domanda = QLabel(get_msg(glossario_data, "Accetti", lingua.upper()))
    layout.addWidget(domanda)

    btns = QHBoxLayout()
    si_btn = QPushButton(get_msg(glossario_data, "Si", lingua.upper()))
    no_btn = QPushButton(get_msg(glossario_data, "No", lingua.upper()))
    si_btn.clicked.connect(dlg.accept)
    no_btn.clicked.connect(dlg.reject)
    btns.addWidget(si_btn)
    btns.addWidget(no_btn)
    layout.addLayout(btns)

    return dlg.exec() == QDialog.Accepted


def action_show_example_input(glossario_data, lingua, parent=None):
    example_path = os.path.join(ASSET_LANG, lingua.lower(), "testuali", "input_link_base_v2.0.txt")
    try:
        raw_text = load_input_file(example_path)
        records = parse_input_text(raw_text)
        state["records"] = records
        logging.info(f"{len(records)} record di esempio caricati")

        # Mostra contenuto in una dialog coerente con 'modifica input'
        dialog = QDialog(parent)
        dialog.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
        dialog.setWindowTitle(get_msg(glossario_data, "Esempio input", lingua.upper()))
        dialog.setMinimumSize(820, 600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #111216;
                color: #fff;
                border: 2px solid #a67c52;
            }
            QLabel, QPushButton, QTextEdit {
                color: #fff;
                font-size: 15px;
            }
            QTextEdit {
                background-color: #181818;
                color: #fff;
                border: 1px solid #a67c52;
            }
            QPushButton {
                background-color: #222;
                border: 1px solid #a67c52;
                padding: 6px 18px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        layout = QVBoxLayout(dialog)

        # Area testo per mostrare il file (sola lettura)
        text_edit = QTextEdit(dialog)
        text_edit.setPlainText(raw_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        # Pulsante Chiudi
        btn_layout = QHBoxLayout()
        btn_close = QPushButton(get_msg(glossario_data, "Chiudi", lingua.upper()), dialog)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        btn_close.clicked.connect(dialog.accept)

        dialog.setLayout(layout)
        dialog.exec()
    except Exception as e:
        show_msgbox_localized(parent, glossario_data, lingua, get_msg(glossario_data, "Attenzione", lingua.upper()), f"{get_msg(glossario_data, 'Errore caricamento esempio input', lingua.upper())}: {str(e)}", icon=QMessageBox.Critical)


def action_modify_input(glossario_data, lingua, parent=None):
    try:
        # Prova prima il file memorizzato in stato (da "Apri input")
        modified_path = state.get("current_input_file")
        # Se non trovato nello stato, prova la cartella input/ (modalità sviluppo)
        if not modified_path or not os.path.exists(modified_path):
            modified_path = os.path.join(BASE_DIR, "input", "input_link.txt")
        # Se ancora non esiste, chiedi all'utente di selezionare il file
        if not os.path.exists(modified_path):
            modified_path, _ = QFileDialog.getOpenFileName(
                parent,
                get_msg(glossario_data, "Seleziona file input da modificare", lingua.upper())
            )

        raw_text = load_input_file(modified_path)
        records = parse_input_text(raw_text)
        state["records"] = records
        logging.info(f"{len(state.get('records', []))} record modificati caricati (pre-edit)")

        # Dialog editor con titolo corretto e dimensioni adeguate
        dialog = QDialog(parent)
        dialog.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
        dialog.setWindowTitle(get_msg(glossario_data, "Modifica input", lingua.upper()))
        dialog.setMinimumSize(820, 600)
        # Sfondo più scuro, simile a "Esempio input"
        dialog.setStyleSheet("""
            QDialog {
                background-color: #181818;
                color: #fff;
                border: 2px solid #a67c52;
            }
            QLabel, QPushButton, QTextEdit {
                color: #fff;
                font-size: 15px;
            }
            QTextEdit {
                background-color: #181818;
                color: #fff;
                border: 1px solid #a67c52;
            }
            QPushButton {
                background-color: #222;
                border: 1px solid #a67c52;
                padding: 6px 18px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        layout = QVBoxLayout(dialog)

        # Area testo per mostrare e modificare il file
        text_edit = QTextEdit(dialog)
        text_edit.setPlainText(raw_text)
        layout.addWidget(text_edit)

        # Pulsanti localizzati
        btn_layout = QHBoxLayout()
        btn_save = QPushButton(get_msg(glossario_data, "Salva", lingua.upper()), dialog)
        btn_cancel = QPushButton(get_msg(glossario_data, "Annulla", lingua.upper()), dialog)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        # Funzione di salvataggio
        def save_changes():
            new_text = text_edit.toPlainText()
            try:
                with open(modified_path, "w", encoding="utf-8") as f:
                    f.write(new_text)
                # Aggiorna lo stato con i record modificati
                state["records"] = parse_input_text(new_text)
                logging.info(f"{len(state['records'])} record modificati caricati (post-save)")
                dialog.accept()
            except Exception as e:
                show_msgbox_localized(parent, glossario_data, lingua, get_msg(glossario_data, "Attenzione", lingua.upper()), f"{get_msg(glossario_data, 'Errore salvataggio input', lingua.upper())}: {str(e)}", QMessageBox.Critical, buttons=("Conferma",), default="Conferma")

        btn_save.clicked.connect(save_changes)
        btn_cancel.clicked.connect(dialog.reject)

        dialog.setLayout(layout)
        dialog.exec()

    except FileNotFoundError:
        show_msgbox_localized(parent, glossario_data, lingua, get_msg(glossario_data, "Attenzione", lingua.upper()), get_msg(glossario_data, "File da modificare non trovato", lingua.upper()), QMessageBox.Critical, buttons=("Conferma",), default="Conferma")
    except Exception as e:
        show_msgbox_localized(parent, glossario_data, lingua, get_msg(glossario_data, "Attenzione", lingua.upper()), f"{get_msg(glossario_data, 'Errore caricamento input modificato', lingua.upper())}: {str(e)}", QMessageBox.Critical, buttons=("Conferma",), default="Conferma")


def ask_language(glossario_data, lingua_attuale, parent):
    """Permette all'utente di cambiare la lingua dell'interfaccia."""
    lingue_disponibili = [
        "IT", "EN", "ES", "FR", "DE", "PT", "RU", "AR", "NL", "HE",
        "JA", "ZH", "PL", "TR", "DA", "NO", "VI", "EL", "RO", "SV"
    ]
    nomi_lingue = {
        "IT": "Italiano",
        "EN": "English",
        "ES": "Español",
        "FR": "Français",
        "DE": "Deutsch",
        "PT": "Português",
        "RU": "Русский",
        "AR": "العربية",
        "NL": "Nederlands",
        "HE": "עברית",
        "JA": "日本語",
        "ZH": "中文",
        "PL": "Polski",
        "TR": "Türkçe",
        "UK": "Українська",
        "CS": "Čeština",
        "EL": "Ελληνικά",
        "HU": "Magyar",
        "RO": "Română",
        "SV": "Svenska",
        "VI": "Tiếng Việt",
        "DA": "Dansk"
    }
    
    # Dialog per selezionare lingua
    dlg = QDialog(parent)
    dlg.setWindowTitle(get_msg(glossario_data, "Cambia lingua", lingua_attuale.upper()))
    dlg.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
    dlg.setStyleSheet("""
        QDialog {
            background-color: #181818;
            color: #fff;
            border: 2px solid #a67c52;
        }
        QLabel {
            color: #fff;
            font-size: 17px;
            background: transparent;
        }
        QComboBox {
            background-color: #222;
            color: #fff;
            border: 1px solid #a67c52;
            font-size: 16px;
            padding: 4px 8px;
            border-radius: 6px;
        }
        QComboBox QAbstractItemView {
            background: #222;
            color: #fff;
            selection-background-color: #a67c52;
            selection-color: #222;
        }
        QPushButton {
            background-color: #222;
            color: #fff;
            border: 1px solid #a67c52;
            padding: 8px 24px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:disabled {
            background-color: #444;
            color: #aaa;
            border: 1px solid #555;
        }
        QPushButton:hover {
            background-color: #333;
        }
    """)
    dlg.setGeometry(100, 100, 400, 220)

    layout = QVBoxLayout(dlg)
    # Titolo descrittivo
    label = QLabel(get_msg(glossario_data, "Scegli la lingua dell'interfaccia", lingua_attuale.upper()) if glossario_data else "Scegli la lingua dell'interfaccia")

    combo = QComboBox()

    # Solo lingue effettivamente supportate (cartelle assets)
    import os
    asset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    lingue_supportate = [d for d in os.listdir(asset_dir) if os.path.isdir(os.path.join(asset_dir, d)) and d != "common"]
    # Mappa sigla → nome localizzato
    nomi_lingue = {
        "it": "Italiano",
        "en": "English",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "pt": "Português",
        "ru": "Русский",
        "ar": "العربية",
        "nl": "Nederlands",
        "he": "עברית",
        "ja": "日本語",
        "zh": "中文",
        "pl": "Polski",
        "tr": "Türkçe",
        "uk": "Українська",
        "cs": "Čeština",
        "el": "Ελληνικά",
        "hu": "Magyar",
        "ro": "Română",
        "sv": "Svenska",
        "vi": "Tiếng Việt",
        "da": "Dansk"
    }
    import locale
    import locale
    try:
        locale.setlocale(locale.LC_ALL, "")
        sys_locale = locale.getlocale()[0]
    except Exception:
        sys_locale = None
    sys_lang = None
    if sys_locale:
        sys_lang = sys_locale.split('_')[0]
    # Forza sempre l'autonimo per norvegese
    for codice in lingue_supportate:
        nome = nomi_lingue.get(codice, codice)
        if codice == "no":
            nome = "Norsk"  # Autonimo norvegese
        combo.addItem(nome, codice)
    # Imposta come default la lingua di sistema se presente
    if sys_lang and sys_lang in lingue_supportate:
        idx = lingue_supportate.index(sys_lang)
        combo.setCurrentIndex(idx)

    btns = QHBoxLayout()
    ok_btn = QPushButton(get_msg(glossario_data, "Conferma", lingua_attuale.upper()) if glossario_data else "Conferma")
    cancel_btn = QPushButton(get_msg(glossario_data, "Annulla", lingua_attuale.upper()) if glossario_data else "Annulla")
    ok_btn.clicked.connect(dlg.accept)
    cancel_btn.clicked.connect(dlg.reject)
    btns.addWidget(ok_btn)
    btns.addWidget(cancel_btn)

    layout.addWidget(label)
    layout.addWidget(combo)
    layout.addLayout(btns)

    if dlg.exec() == QDialog.Accepted:
        # Restituisce la sigla associata al nome scelto
        return combo.currentData()
    return "en"


def ask_image_formats(glossario_data, lingua):
    dlg = QDialog()
    dlg.resize(270, 260)  # finestra compatta, sufficiente per le etichette localizzate
    dlg.setWindowTitle(get_msg(glossario_data, "Seleziona formati immagine", lingua.upper()))
    dlg.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
    _setup_dialog_pergamena(dlg, 270, 260)

    layout = QVBoxLayout(dlg)
    checks_layout = QHBoxLayout()

    png = QCheckBox("PNG")
    jpg = QCheckBox("JPG")
    tiff = QCheckBox("TIFF")

    checks_layout.addWidget(png)
    checks_layout.addWidget(jpg)
    checks_layout.addWidget(tiff)
    layout.addLayout(checks_layout)

    btns = QHBoxLayout()
    ok_btn = QPushButton(get_msg(glossario_data, "Conferma", lingua.upper()))
    cancel_btn = QPushButton(get_msg(glossario_data, "Annulla", lingua.upper()))
    ok_btn.clicked.connect(dlg.accept)
    cancel_btn.clicked.connect(dlg.reject)
    btns.addWidget(ok_btn)
    btns.addWidget(cancel_btn)
    layout.addLayout(btns)

    if dlg.exec() == QDialog.Accepted:
        scelti = []
        if png.isChecked(): scelti.append("PNG")
        if jpg.isChecked(): scelti.append("JPG")
        if tiff.isChecked(): scelti.append("TIF")

        if scelti:
            state["formats"] = scelti
            logging.info(f"Formati selezionati: {scelti}")
            # Usa una label di fallback se la chiave non esiste o è None
            label = get_msg(glossario_data, 'Formati selezionati', lingua.upper())
            if not label or label == 'None':
                label = "Formati selezionati"
            # Finestra di conferma con stile "Operazione completata"
            conferma = QDialog(dlg)
            conferma.setWindowTitle("ATK-Pro")
            _setup_dialog_pergamena(conferma, 500, 200)
            layout = QVBoxLayout(conferma)
            label_widget = QLabel(f"{label}: {', '.join(scelti)}")
            label_widget.setAlignment(Qt.AlignCenter)
            label_widget.setStyleSheet("color: #fff; font-size: 16px;")
            layout.addWidget(label_widget)
            ok_btn = QPushButton(get_msg(glossario_data, "Conferma", lingua.upper()) or "Conferma")
            ok_btn.clicked.connect(conferma.accept)
            layout.addWidget(ok_btn, alignment=Qt.AlignCenter)
            conferma.setLayout(layout)
            conferma.exec()
        return scelti
    return []


def action_open_input(glossario_data, lingua, parent=None):
    path = QFileDialog.getOpenFileName(
        parent,
        get_msg(glossario_data, "Apri input", lingua.upper()),
        os.path.join(BASE_DIR, "input"),
        "Text (*.txt);;All (*.*)"
    )[0]
    if not path:
        return
    try:
        raw_text = load_input_file(path)
        records = parse_input_text(raw_text)
        state["records"] = records
        state["current_input_file"] = path  # Memorizza il percorso
        logging.info(f"{len(records)} record caricati")

        # Conferma con solo il path, stile uniforme
        msg = QMessageBox(parent)
        msg.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
        msg.setWindowTitle(get_msg(glossario_data, "File aperto", lingua.upper()))
        msg.setText(path)
        style_msgbox_pergamena(msg)
        msg.exec()
    except Exception as e:
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
        msg.setWindowTitle(get_msg(glossario_data, "Attenzione", lingua.upper()))
        msg.setText(f"{get_msg(glossario_data, 'Errore caricamento input', lingua.upper())}: {str(e)}")
        style_msgbox_pergamena(msg)
        msg.exec()


def parse_record_types_from_file(path: str):
    num_doc, num_reg = 0, 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("D ") or line.startswith("d "):
                    num_doc += 1
                elif line.startswith("R ") or line.startswith("r "):
                    num_reg += 1
    except Exception:
        pass
    if num_doc == 0 and num_reg == 0:
        num_doc = 1
    return num_doc, num_reg


def action_select_output(glossario_data, lingua):
    records = state.get("records") or []
    if not records:
        show_msgbox_localized(None, glossario_data, lingua, get_msg(glossario_data, "Attenzione", lingua.upper()), get_msg(glossario_data, "Nessun input caricato", lingua.upper()), QMessageBox.Warning, buttons=("Conferma",), default="Conferma")
        return

    num_doc = sum(1 for r in records if r.get("modalita", "").strip().upper() == "D")
    num_reg = sum(1 for r in records if r.get("modalita", "").strip().upper() == "R")

    folders_doc, folders_reg = [], []

    # Obbliga la selezione di tutte le cartelle richieste
    for i in range(num_doc):
        folder = None
        while not folder:
            folder = QFileDialog.getExistingDirectory(
                None,
                f"{get_msg(glossario_data, 'Documento', lingua.upper())} {i+1}/{num_doc}"
            )
            if not folder:
                show_msgbox_localized(None, glossario_data, lingua, get_msg(glossario_data, "Attenzione", lingua.upper()), get_msg(glossario_data, "Selezione cartella obbligatoria", lingua.upper()), QMessageBox.Warning, buttons=(get_msg(glossario_data, "Conferma", lingua.upper()),), default=get_msg(glossario_data, "Conferma", lingua.upper()))
        folders_doc.append(folder)

    for i in range(num_reg):
        folder = None
        while not folder:
            folder = QFileDialog.getExistingDirectory(
                None,
                f"{get_msg(glossario_data, 'Registro', lingua.upper())} {i+1}/{num_reg}"
            )
            if not folder:
                show_msgbox_localized(None, glossario_data, lingua, get_msg(glossario_data, "Attenzione", lingua.upper()), get_msg(glossario_data, "Selezione cartella obbligatoria", lingua.upper()), QMessageBox.Warning, buttons=(get_msg(glossario_data, "Conferma", lingua.upper()),), default=get_msg(glossario_data, "Conferma", lingua.upper()))
        folders_reg.append(folder)

    # Aggiorna lo stato globale
    state["output_folders_doc"] = folders_doc
    state["output_folders_reg"] = folders_reg
    state["registri_output"] = folders_doc + folders_reg  # compatibilità
    if folders_doc:
        state["output_folder"] = folders_doc[0]
    elif folders_reg:
        state["output_folder"] = folders_reg[0]

    # Finestra di conferma riepilogativa dopo tutte le selezioni
    riepilogo = []
    if folders_doc:
        riepilogo.append(f"<b>{get_msg(glossario_data, 'Documenti', lingua.upper()) or 'Documenti'}:</b>")
        for idx, folder in enumerate(folders_doc):
            riepilogo.append(f"{get_msg(glossario_data, 'Documento', lingua.upper()) or 'Documento'} {idx+1}: {folder}")
    if folders_reg:
        riepilogo.append(f"<b>{get_msg(glossario_data, 'Registri', lingua.upper()) or 'Registri'}:</b>")
        for idx, folder in enumerate(folders_reg):
            riepilogo.append(f"{get_msg(glossario_data, 'Registro', lingua.upper()) or 'Registro'} {idx+1}: {folder}")
    conferma = QDialog()
    conferma.setWindowTitle("ATK-Pro")
    _setup_dialog_pergamena(conferma, 600, 300)
    layout = QVBoxLayout(conferma)
    label_widget = QLabel("<br>".join(riepilogo))
    label_widget.setAlignment(Qt.AlignLeft)
    label_widget.setStyleSheet("color: #fff; font-size: 15px;")
    label_widget.setTextFormat(Qt.RichText)
    layout.addWidget(label_widget)
    ok_btn = QPushButton(get_msg(glossario_data, "Conferma", lingua.upper()) or "Conferma")
    ok_btn.clicked.connect(conferma.accept)
    layout.addWidget(ok_btn, alignment=Qt.AlignCenter)
    conferma.setLayout(layout)
    conferma.exec()

    # Eliminato: dialogo di conferma cartelle selezionate


def action_process(glossario_data, lingua, parent=None):
    records = state.get("records") or []
    if not records:
        show_msgbox_localized(parent, glossario_data, lingua, "ATK-Pro", get_msg(glossario_data, "Nessun record caricato", lingua.upper()), QMessageBox.Warning, buttons=("Conferma",), default="Conferma")
        logging.warning("Tentativo di elaborazione senza record")
        return

    selected_formats = state.get("formats") or []
    if not selected_formats:
        show_msgbox_localized(parent, glossario_data, lingua, "ATK-Pro", get_msg(glossario_data, "Nessun formato selezionato", lingua.upper()), QMessageBox.Warning, buttons=("Conferma",), default="Conferma")
        logging.warning("Elaborazione bloccata: nessun formato selezionato")
        return

    logging.info(f"Formati da elaborare: {selected_formats}")

    try:
        # Prima di avviare il worker: risolvi cartelle di output per ciascun record
        output_folder = state.get('output_folder')
        output_folders_doc = state.get('output_folders_doc', [])
        output_folders_reg = state.get('output_folders_reg', [])
        # Blocca se nessuna cartella valida
        if not output_folder and not (output_folders_doc and len(output_folders_doc) > 0) and not (output_folders_reg and len(output_folders_reg) > 0):
            show_msgbox_localized(parent, glossario_data, lingua, "ATK-Pro", "Nessuna cartella di output valida selezionata!", QMessageBox.Critical, buttons=("Conferma",), default="Conferma")
            return
        # Conta i record per modalità
        doc_indices = [i for i, r in enumerate(records) if str(r.get('modalita', '')).strip().upper() == 'D']
        reg_indices = [i for i, r in enumerate(records) if str(r.get('modalita', '')).strip().upper() == 'R']
        if len(output_folders_doc) != len(doc_indices):
            show_msgbox_localized(parent, glossario_data, lingua, "ATK-Pro", f"Numero di cartelle documento selezionate ({len(output_folders_doc)}) diverso dal numero di record documento ({len(doc_indices)}).", QMessageBox.Critical, buttons=("Conferma",), default="Conferma")
            return
        if len(output_folders_reg) != len(reg_indices):
            show_msgbox_localized(parent, glossario_data, lingua, "ATK-Pro", f"Numero di cartelle registro selezionate ({len(output_folders_reg)}) diverso dal numero di record registro ({len(reg_indices)}).", QMessageBox.Critical, buttons=("Conferma",), default="Conferma")
            return
        doc_counter = 0
        reg_counter = 0
        for idx, rec in enumerate(records):
            try:
                modalita = str(rec.get('modalita', '')).strip().upper()
            except Exception:
                modalita = ''
            out_dir = None
            if modalita == 'D':
                out_dir = output_folders_doc[doc_counter]
                doc_counter += 1
            elif modalita == 'R':
                out_dir = output_folders_reg[reg_counter]
                reg_counter += 1
                # Prompt PDF PRIMA di avviare il worker, sempre
                from src.user_prompts import ask_generate_pdf
                resp = ask_generate_pdf(glossario_data, lingua, parent)
                rec['gen_pdf'] = bool(resp)
            else:
                show_msgbox_localized(parent, glossario_data, lingua, "ATK-Pro", f"Modalità record non riconosciuta: {modalita}", QMessageBox.Critical, buttons=("Conferma",), default="Conferma")
                return
            try:
                rec['output'] = out_dir
            except Exception:
                pass

        # Non chiedere qui le conferme PDF (eviterebbe che compaiano tutte
        # insieme all'avvio). La richiesta verrà fatta dal worker per ogni
        # registro 'R' al momento dell'elaborazione: il worker emette un
        # segnale che il main thread gestisce mostrando il dialog.
        from src.user_prompts import ask_generate_pdf, ProgressDialog

        # Tentativo: eseguire l'elaborazione in background usando il worker Qt
        try:
            from src.qt_worker import ElaborazioneWorker
            from PySide6.QtCore import QCoreApplication
        except Exception:
            pass

            pd = ProgressDialog(glossario_data, lingua, total=len(records), parent=parent)
            pd.show()
            # Forza colore bianco sulla barra di avanzamento e aggiungi label n/N accanto
            try:
                pd.pbar.setStyleSheet("QProgressBar { color: #fff; font-weight: bold; font-size: 15px; text-align: center; } QProgressBar::chunk { background: #a67c52; }")
                from PySide6.QtWidgets import QLabel
                if not hasattr(pd, 'count_label'):
                    pd.count_label = QLabel()
                    pd.count_label.setStyleSheet("color: #fff; font-size: 15px; font-weight: bold; background: transparent;")
                    pd.layout().addWidget(pd.count_label)
            except Exception:
                pass

            # Worker: useremo i record già arricchiti (output, gen_pdf)
            worker = ElaborazioneWorker(records, formats=selected_formats, glossario_data=glossario_data, lingua=lingua)

            def on_progress(current, total, name, page=None, page_total=None):
                try:
                    pd.update(current=current, name=name, page=page, page_total=page_total)
                    # Aggiorna la label n/N accanto alla barra
                    if hasattr(pd, 'count_label'):
                        pd.count_label.setText(f"{current}/{total}")
                    logging.debug(f"[GUI] on_progress: current={current} total={total} name={name} page={page} page_total={page_total}")
                except Exception:
                    pass

            def on_finished(results):
                try:
                    pd.close()
                except Exception:
                    pass
                # Eliminato: dialogo ridondante
                logging.info("Elaborazione completata (worker)")
                # Pulizia finale: assicurati che il worker sia terminato e rimosso
                try:
                    # se disponibile, chiedi cancellazione e attendi brevemente
                    worker.cancel()
                except Exception:
                    pass
                try:
                    worker.wait(3000)
                except Exception:
                    pass
                try:
                    # deleteLater per sicurezza nella loop Qt
                    worker.deleteLater()
                except Exception:
                    pass

            dlg = QDialog(parent)
            dlg.setWindowTitle(get_msg(glossario_data, "Informazioni", lingua.upper()))
            dlg.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
            dlg.setStyleSheet("QDialog { background: #fff; border: 2px solid #a67c52; } QLabel, QPushButton { color: #482e1a; font-size: 16px; } QPushButton { background-color: #d2bb8a; border: 1px solid #a67c52; padding: 6px 18px; border-radius: 6px; font-weight: bold; } QPushButton:hover { background-color: #e5d3b3; }")
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 15, 20, 15)
            layout.setSpacing(2)
            email_path = os.path.join(ASSET_COMMON, "testuali", "email.txt")
            email = (carica_testo_asset(email_path) or "").strip()
            r1 = QLabel(f"ATK-Pro v{VERSION}")
            r2 = QLabel("©2026 Daniele Pigoli")
            msg = get_msg(self.glossario_data, "email non disponibile", self.lingua)
            r3 = QLabel(email if email else msg or "email non disponibile")
            for lbl in (r1, r2, r3):
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setStyleSheet("QLabel { background: transparent; color: #482e1a; font-size: 16px; }")
                layout.addWidget(lbl)
            ok_btn = QPushButton(get_msg(glossario_data, "Chiudi", lingua.upper()))
            ok_btn.clicked.connect(dlg.accept)
            layout.addWidget(ok_btn, alignment=Qt.AlignCenter)
            dlg.setLayout(layout)
            dlg.adjustSize()
            dlg.setFixedSize(dlg.sizeHint())
            dlg.exec()

            

            # Pulizia: rimuovi il riferimento quando finisce
            def _cleanup_worker(results=None):
                # Helper per fermare il worker in modo robusto
                def _ensure_worker_stopped(w, timeout_ms=5000):
                    try:
                        # indica al lavoro di terminare
                        try:
                            w.cancel()
                        except Exception:
                            pass
                        # Se il thread supporta quit(), usalo
                        try:
                            w.quit()
                        except Exception:
                            pass
                        # Attendi che termini
                        try:
                            w.wait(timeout_ms)
                        except Exception:
                            pass
                        # Se ancora in esecuzione, forza la terminazione (ultima risorsa)
                        try:
                            if getattr(w, 'isRunning', lambda: False)():
                                try:
                                    w.terminate()
                                except Exception:
                                    pass
                                try:
                                    w.wait(2000)
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        # deleteLater per pulire l'oggetto Qt
                        try:
                            w.deleteLater()
                        except Exception:
                            pass
                    except Exception:
                        pass

                try:
                    if parent is not None and getattr(parent, '_active_worker', None) is worker:
                        _ensure_worker_stopped(worker, timeout_ms=5000)
                        parent._active_worker = None
                except Exception:
                    pass
                # Rimosso: gestione legacy di elaborazione.state
                # Ora non serve più, lo stato è solo in main_gui_qt.py
                pass

            try:
                worker.signals.finished.connect(_cleanup_worker)
            except Exception:
                pass
                try:
                    # ...existing code...
                    try:
                        from src.qt_worker import ElaborazioneWorker
                        from PySide6.QtCore import QCoreApplication
                        pd = ProgressDialog(glossario_data, lingua, total=len(records), parent=parent)
                    except Exception:
                        pass
                        pd.show()
                        worker = ElaborazioneWorker(records, formats=selected_formats, glossario_data=glossario_data, lingua=lingua)
                        def on_progress(current, total, name):
                            try:
                                pd.update(current=current, name=name)
                                logging.debug(f"[GUI] on_progress: current={current} total={total} name={name}")
                            except Exception:
                                pass
                        def on_finished(results):
                            try:
                                pd.close()
                            except Exception:
                                pass
                            # Verifica se tutti i risultati sono SUCCESS
                            all_success = all(r.get('status') == 'SUCCESS' for r in (results or []))
                            if all_success:
                                show_operation_completed_dialog(parent, glossario_data, lingua)
                                logging.info("Elaborazione completata (worker)")
                            else:
                                show_msgbox_localized(parent, glossario_data, lingua, "ATK-Pro", "Operazione terminata con errori. Alcuni record non sono stati elaborati correttamente.", QMessageBox.Critical, buttons=("Chiudi",), default="Chiudi")
                                logging.warning("Elaborazione terminata con errori (worker)")
                            try:
                                worker.cancel()
                            except Exception:
                                pass
                            try:
                                worker.wait(3000)
                            except Exception:
                                pass
                            try:
                                worker.deleteLater()
                            except Exception:
                                pass
                        def on_error(err):
                            logging.error(f"Errore worker: {err}")
                            QMessageBox.critical(parent, get_msg(glossario_data, "Attenzione", lingua.upper()), f"{get_msg(glossario_data, 'Errore durante l\'elaborazione (worker)', lingua.upper())}: {err}")
                        worker.signals.progress.connect(on_progress)
                        def _handle_need_pdf_confirmation(idx, nome_file):
                            try:
                                resp = ask_generate_pdf(glossario_data, lingua, parent)
                                try:
                                    records[idx]['gen_pdf'] = bool(resp)
                                except Exception:
                                    pass
                            except Exception as e:
                                logging.debug(f"Errore mostrare richiesta PDF per {nome_file}: {e}")
                        try:
                            worker.signals.need_pdf_confirmation.connect(_handle_need_pdf_confirmation)
                        except Exception:
                            pass
                        worker.signals.finished.connect(on_finished)
                        worker.signals.error.connect(on_error)
                        try:
                            worker._ref = worker
                        except Exception:
                            pass
                        worker.start()
                        return
                    except Exception as e:
                        msg = get_msg(self.glossario_data, "Worker Qt non disponibile", self.lingua)
                        logging.debug(msg or f"Worker Qt non disponibile o inizializzazione fallita: {e}")
                    risultati = elaborazione_mod.esegui_elaborazione(
                        state,
                        glossario_data=glossario_data,
                        lingua=lingua,
                        records=records,
                        formats=selected_formats
                    )
                    # Mostra dialog coerente con esito
                    all_success = all(r.get('status') == 'SUCCESS' for r in (risultati or []))
                    if all_success:
                        show_operation_completed_dialog(parent, glossario_data, lingua)
                        logging.info("Elaborazione completata (no worker)")
                    else:
                        show_msgbox_localized(parent, glossario_data, lingua, "ATK-Pro", "Operazione terminata con errori. Alcuni record non sono stati elaborati correttamente.", QMessageBox.Critical, buttons=("Chiudi",), default="Chiudi")
                        logging.warning("Elaborazione terminata con errori (no worker)")
                except Exception as e:
                    QMessageBox.critical(parent, get_msg(glossario_data, "Attenzione", lingua.upper()), f"{get_msg(glossario_data, 'Errore durante l\'elaborazione', lingua.upper())}: {str(e)}")
                    logging.exception("Errore durante l'elaborazione")
        
        # Blocco legacy per visualizzazione elaborazioni precedenti rimosso (manifest_files non definito)

    except Exception:
        pass
        # Fine blocco riscritto


def action_placeholder(glossario_data, lingua, voce):
    from pathlib import Path
    documents_dir = str(Path.home() / 'Documents' / 'ATK-Pro')
    if voce == "Esporta configurazione":
        default_path = os.path.join(documents_dir, "ATK-Pro-config.json")
        path, _ = QFileDialog.getSaveFileName(None, "Esporta configurazione", default_path, "File JSON (*.json)")
        if not path:
            return
        # Aggiorna lo stato prima di salvare: prendi i dati reali dai widget/variabili
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        for w in app.topLevelWidgets():
            if isinstance(w, MainWindow):
                w.aggiorna_state_da_ui()
                w.mostra_valori_configurazione()
                w.resizeEvent(None)
                w.esporta_configurazione()
                break
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(asset_path("assets/common/grafici/ATK-Pro.ico")))
        msg.setMinimumSize(700, 200)
        msg.setWindowTitle(get_msg(glossario_data, voce, lingua.upper()))
        msg.setText(get_msg(glossario_data, "Operazione completata", lingua.upper()) or "Configurazione esportata correttamente.")
        msg.exec()
    elif voce == "Importa configurazione":
        default_path = os.path.join(documents_dir, "ATK-Pro-config.json")
        path, _ = QFileDialog.getOpenFileName(None, "Importa configurazione", default_path, "File JSON (*.json)")
        if not path:
            return
        for w in app.topLevelWidgets():
            if isinstance(w, MainWindow):
                w.importa_configurazione()
                break
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        for w in app.topLevelWidgets():
            if isinstance(w, MainWindow):
                w.aggiorna_ui_da_state()
                w.mostra_valori_configurazione()
                w.resizeEvent(None)
                break
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(asset_path("assets/common/grafici/ATK-Pro.ico")))
        msg.setMinimumSize(700, 200)
        msg.setWindowTitle(get_msg(glossario_data, voce, lingua.upper()))
        msg.setText(get_msg(glossario_data, "Operazione completata", lingua.upper()) or "Configurazione importata correttamente.")
        msg.exec()
    else:
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(asset_path("assets/common/grafici/ATK-Pro.ico")))
        msg.setMinimumSize(700, 200)
        msg.setWindowTitle(get_msg(glossario_data, voce, lingua.upper()))
        msg.setText(get_msg(glossario_data, "Funzione in sviluppo", lingua.upper()))
        msg.exec()


def mostra_banner_chiusura(glossario_data, lingua, banner_path, paypal_url_path):
    dlg = QDialog()
    dlg.setWindowTitle(get_msg(glossario_data, "Sostieni il progetto", lingua.upper()))
    dlg.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
    dlg.setStyleSheet("QDialog { background: transparent; }")
    dlg.setAutoFillBackground(True)

    layout = QVBoxLayout()

    if banner_path and os.path.exists(banner_path):
        try:
            pixmap = QPixmap(banner_path)
            if not pixmap.isNull():
                # Dimensione stretta attorno al banner
                max_w, max_h = 560, 360
                scaled = pixmap.scaled(max_w, max_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl = QLabel()
                lbl.setPixmap(scaled)
                lbl.setAlignment(Qt.AlignCenter)

                # Ridimensiona dialog in modo aderente all'immagine + margine minimo
                pad_w, pad_h = 32, 24
                dlg.resize(min(scaled.width() + pad_w, max_w + pad_w),
                           min(scaled.height() + pad_h, max_h + pad_h))

                def apri_paypal(event):
                    if os.path.exists(paypal_url_path):
                        raw = carica_testo_asset(paypal_url_path).strip()
                        url = raw if raw.startswith("http") else None
                        if url:
                            logging.debug(f"Apro PayPal URL: {url}")
                            QDesktopServices.openUrl(QUrl(url))

                lbl.mousePressEvent = apri_paypal
                layout.addWidget(lbl)
        except Exception as e:
            logging.debug(f"Errore caricamento banner: {e}")
            layout.addWidget(QLabel(get_msg(glossario_data, "Banner non disponibile", lingua.upper())))
    else:
        layout.addWidget(QLabel(get_msg(glossario_data, "Banner non disponibile", lingua.upper())))

    chiudi_btn = QPushButton(get_msg(glossario_data, "Chiudi", lingua.upper()))
    chiudi_btn.clicked.connect(dlg.accept)
    layout.addWidget(chiudi_btn)

    dlg.setLayout(layout)
    dlg.exec()


def main():
    logging.info("Test log avvio")
    logging.debug("Avvio main_gui_qt.py")

    # Su Linux, disabilita il sandbox Chromium solo in ambienti CI/headless
    # (dove il kernel non supporta user namespaces per il renderer QtWebEngine).
    # Su desktop reale (con DISPLAY o WAYLAND_DISPLAY) il sandbox rimane attivo.
    if sys.platform.startswith("linux"):
        in_ci = os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS")
        has_display = os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
        if in_ci or not has_display:
            os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")
            os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--no-sandbox")

    app = QApplication(sys.argv)

    # Font custom (usa asset_path per supportare bundle macOS/Windows)
    font1_path = asset_path("assets/common/fonts/Aref_Ruqaa/ArefRuqaa-Regular.ttf")
    font2_path = asset_path("assets/common/fonts/Crimson_Text/CrimsonText-Regular.ttf")
    QFontDatabase.addApplicationFont(font1_path)
    QFontDatabase.addApplicationFont(font2_path)
    logging.debug(f"Font custom caricati: {font1_path}, {font2_path}")

    # Stile ATK da QSS
    file = QFile(asset_path("assets/common/testuali/atk_style.qss"))
    if file.open(QFile.ReadOnly | QFile.Text):
        app.setStyleSheet(str(file.readAll(), encoding="utf-8"))
        logging.debug("Stile ATK applicato da atk_style.qss")
    else:
        logging.debug("Errore: impossibile caricare atk_style.qss")

    # Selezione lingua: leggi dal registro se exe, altrimenti mostra dialog di selezione
    _is_frozen = getattr(sys, 'frozen', False)
    if _is_frozen:
        # EXE: leggi dalla lingua dal registro (settata dall'installer)
        lingua = get_language_from_registry()
        logging.debug(f"EXE rilevato, lingua dal registro: {lingua}")
    else:
        # Sviluppo: mostra dialog di selezione
        lingua = scegli_lingua()
        logging.debug(f"Modalità sviluppo, lingua scelta: {lingua}")
    
    glossario_data = carica_glossario(lingua)

    # Carica file di esempio localizzato
    example_path = carica_file_esempio(lingua)
    state["records"].append(example_path)
    logging.debug(f"File di esempio caricato: {example_path}")

    # Creazione finestra principale (senza mostrare disclaimer al primo avvio)
    window = MainWindow(glossario_data, lingua)
    window.show()

    # Gestione chiusura con banner
    def on_close():
        logging.debug("Chiusura applicazione")
        lingua_norm = lingua.strip().lower()
        lingua_alt = lingua.strip().upper() if lingua_norm != lingua.strip().upper() else lingua.strip().lower()
        # Prova prima in minuscolo, poi maiuscolo
        paths = [
            os.path.join(ASSET_LANG, lingua_norm, "grafici", "sostieni_banner_qr.png"),
            os.path.join(ASSET_LANG, lingua_norm, "grafici", "sostieni_banner_qr.webp"),
            os.path.join(ASSET_LANG, lingua_alt, "grafici", "sostieni_banner_qr.png"),
            os.path.join(ASSET_LANG, lingua_alt, "grafici", "sostieni_banner_qr.webp")
        ]
        banner_path = None
        for p in paths:
            logging.debug(f"Verifica banner: {p} -> {'OK' if os.path.exists(p) else 'MANCANTE'}")
            if os.path.exists(p):
                banner_path = p
                break
        if not banner_path:
            logging.error(f"Nessun banner trovato nei path: {paths}")
        else:
            logging.info(f"Banner path selezionato: {banner_path}")
        paypal_url_path = os.path.join(ASSET_COMMON, "testuali", "PayPal.me.url")
        mostra_banner_chiusura(glossario_data, lingua_norm, banner_path, paypal_url_path)

    app.aboutToQuit.connect(on_close)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

