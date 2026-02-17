import logging
import sys
import os

# Aggiungi la root del progetto al PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT_DIR)

# Importa il modulo da src
from src import main_gui

# Config log dedicato ai test
logging.basicConfig(
    filename="atkpro_test.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)
logger.info("Avvio test automatico main_gui.py")

# Stato simulato
state = {"records": ["record1", "record2"], "formats": ["PDF"], "output_folder": "C:\\Temp"}

def fake_action_open_input():
    logger.info("Simulazione: apertura input")
    print("DEBUG: Input caricati (2 record)")

def fake_action_select_output():
    logger.info("Simulazione: selezione cartella output")
    print("DEBUG: Cartella selezionata:", state["output_folder"])

def fake_action_select_formats():
    logger.info("Simulazione: selezione formati")
    print("DEBUG: Formati selezionati:", state["formats"])

def fake_action_process():
    if not state["records"] or not state["formats"] or not state["output_folder"]:
        logger.warning("Simulazione: condizioni non soddisfatte")
        print("DEBUG: Nessun record/formato/cartella")
        return
    logger.info("Simulazione: elaborazione completata")
    print("DEBUG: Elaborazione completata")

def fake_action_close():
    logger.info("Simulazione: chiusura applicazione")
    print("DEBUG: Chiusura applicazione")

# Sequenza simulata
if __name__ == "__main__":
    fake_action_open_input()
    fake_action_select_output()
    fake_action_select_formats()
    fake_action_process()
    fake_action_close()

    logger.info("Test automatico completato")
    print("DEBUG: Test automatico completato")
