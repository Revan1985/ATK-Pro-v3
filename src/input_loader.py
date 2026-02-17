# -*- coding: utf-8 -*-
# Modulo: input_loader.py
# Caricamento file di input e normalizzazione modalità
# Riallineato alla logica Antenati_Tile_Rebuilder_v1.4.1.py

import os
import logging

logger = logging.getLogger(__name__)

def load_input_file(percorso_file):
    """
    Carica il contenuto di un file di input come stringa.
    Solleva FileNotFoundError se il file non esiste.
    """
    try:
        with open(percorso_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"❌ File non trovato: {percorso_file}")
        raise
    except PermissionError:
        logger.error(f"🚫 Permessi negati per il file: {percorso_file}")
        raise
    except Exception as e:
        logger.error(f"❌ Errore imprevisto nel caricamento file {percorso_file}: {e}", exc_info=True)
        raise

def carica_input_file_con_gui():
    """
    Apre una finestra di dialogo per selezionare un file di input.
    Restituisce il contenuto del file selezionato.
    """
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()  # Nasconde la finestra principale

    percorso_file = filedialog.askopenfilename(
        title="Seleziona file di input",
        filetypes=[("File di testo", "*.txt"), ("Tutti i file", "*.*")]
    )

    if not percorso_file:
        raise FileNotFoundError("Nessun file selezionato")

    return load_input_file(percorso_file)

def normalizza_modalita(modalita_raw):
    """
    Normalizza la modalità (D/R) come nella v1.4.1.
    - Rimuove spazi
    - Converte in maiuscolo
    - Valida contro valori ammessi
    """
    if not modalita_raw:
        return None

    modalita = modalita_raw.strip().upper()
    if modalita in ["D", "R"]:
        return modalita

    logger.warning(f"⚠️ Modalità non riconosciuta: {modalita_raw}")
    return None
