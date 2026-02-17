# === Copertura test ===
# ✔ Test realistici presenti
# ✔ Rami difensivi simulati
# ✅ Validato (logico)

"""
Modulo: link_editor.py
ATK-Pro v2.0 — Gestione dei link (CLI + GUI)

Funzionalità:
- Caricamento e salvataggio dei link da file
- Editing via CLI (aggiungi, modifica, cancella, salva, esci)
- Editing via GUI (Tkinter)

Note storiche:
- v1.x: implementazione base CLI
- v2.0: aggiunta GUI con Tkinter
- Patch v2.0.1: controllo difensivo in delete_link
- Patch v2.0.2: import difensivi per ambienti senza Tkinter GUI
- Patch v2.0.3: gestione input non numerico in CLI e rilancio PermissionError
- Patch v2.0.4: uniformato messaggio CLI → "Indice non valido"
"""

import os
import tkinter as tk
from src import input_loader

# --- Import difensivi per ambienti headless ---
try:
    from tkinter import simpledialog, messagebox
except ImportError:
    class _StubDialog:
        @staticmethod
        def askstring(title, prompt, initialvalue=""):
            print(f"[stub simpledialog] {title}: {prompt} (initial={initialvalue})")
            return None

    class _StubMessageBox:
        @staticmethod
        def showinfo(title, msg):
            print(f"[stub messagebox INFO] {title}: {msg}")

        @staticmethod
        def showerror(title, msg):
            print(f"[stub messagebox ERROR] {title}: {msg}")

    simpledialog = _StubDialog()
    messagebox = _StubMessageBox()


DEFAULT_PATH = "input_link.txt"


# ---------------- Funzioni di utilità ----------------

def load_links(path: str = DEFAULT_PATH):
    """Carica i link dal file indicato."""
    if not os.path.exists(path):
        return []
    raw = input_loader.load_input_file(path)
    return [line.strip() for line in raw.splitlines() if line.strip()]


def save_input_links(links, path: str = DEFAULT_PATH):
    """Salva i link nel file indicato."""
    with open(path, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")


# ---------------- CLI ----------------

def edit_links_cli(path: str = DEFAULT_PATH):
    """Editor CLI per i link."""
    links = load_links(path)
    while True:
        print("\nLink correnti:")
        for i, link in enumerate(links, 1):
            print(f"{i}. {link}")
        cmd = input("(a)ggiungi, (m)odifica, (c)cancella, (s)alva, (q)uit: ").strip().lower()

        if cmd == "a":
            new_link = input("Nuovo link: ").strip()
            if new_link:
                links.append(new_link)

        elif cmd == "m":
            raw = input("Indice da modificare: ")
            try:
                idx = int(raw) - 1
            except ValueError:
                print("Indice non valido")
                continue
            if 0 <= idx < len(links):
                new_val = input("Nuovo valore: ").strip()
                if new_val:
                    links[idx] = new_val
            else:
                print("Indice fuori range")

        elif cmd == "c":
            raw = input("Indice da cancellare: ")
            try:
                idx = int(raw) - 1
            except ValueError:
                print("Indice non valido")
                continue
            if 0 <= idx < len(links):
                links.pop(idx)
            else:
                print("Indice fuori range")

        elif cmd == "s":
            save_input_links(links, path)
            print("Salvato.")

        elif cmd == "q":
            break

        else:
            print("Comando non valido")


# ---------------- GUI ----------------

class LinkEditorGUI:
    """Editor GUI per i link (Tkinter)."""

    def __init__(self, master, path: str = DEFAULT_PATH, glossario_data=None, lingua="IT"):
        self.master = master
        self.master.title("Link Editor")
        self.path = path
        self.glossario_data = glossario_data
        self.lingua = lingua

        # Helper per localizzazione
        def get_msg_fallback(key, fallback):
            if glossario_data is None:
                return fallback
            try:
                from src.metadata_utils import get_msg
                return get_msg(glossario_data, key, lingua.upper())
            except Exception:
                return fallback

        # Lista link
        self.listbox = tk.Listbox(master, width=80, height=15)
        self.listbox.pack()
        self.links = load_links(path)
        for link in self.links:
            self.listbox.insert(tk.END, link)

        # Pulsanti
        tk.Button(master, text=get_msg_fallback("Aggiungi", "Aggiungi"), command=self.add_link).pack()
        tk.Button(master, text=get_msg_fallback("Modifica", "Modifica"), command=self.edit_link).pack()
        tk.Button(master, text=get_msg_fallback("Cancella", "Cancella"), command=self.delete_link).pack()
        tk.Button(master, text=get_msg_fallback("Salva", "Salva"), command=self.save_links).pack()

    def _prompt(self, title, prompt, initial=""):
        return simpledialog.askstring(title, prompt, initialvalue=initial)

    def add_link(self):
        new_link = self._prompt("Aggiungi link", "Inserisci nuovo link:")
        if new_link:
            self.links.append(new_link)
            self.listbox.insert(tk.END, new_link)

    def edit_link(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        current = self.links[idx]
        new_val = self._prompt("Modifica link", "Nuovo valore:", current)
        if new_val:
            self.links[idx] = new_val
            self.listbox.delete(idx)
            self.listbox.insert(idx, new_val)

    def delete_link(self):
        """Elimina il link selezionato dalla lista e dal file.

        Patch v2.0.1 — aggiunto controllo difensivo su indice fuori range.
        """
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < 0 or idx >= len(self.links):
            print(f"[link_editor] delete_link: indice {idx} fuori range, nessuna azione eseguita")
            return
        self.links.pop(idx)
        self.listbox.delete(idx)

    def save_links(self):
        try:
            save_input_links(self.links, self.path)
            messagebox.showinfo("Salvataggio", "Link salvati con successo.")
        except PermissionError:
            error_title = self.glossario_data.get("Errore", "Errore") if self.glossario_data else "Errore"
            error_msg = self.glossario_data.get("Permesso negato durante il salvataggio", "Permesso negato durante il salvataggio") if self.glossario_data else "Permesso negato durante il salvataggio"
            messagebox.showerror(error_title, error_msg)
            raise
