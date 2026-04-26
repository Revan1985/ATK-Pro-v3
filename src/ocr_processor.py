import os
import io
import base64
import logging
import requests
from PIL import Image
from key_manager import KeyManager


class AdvancedOCRWorker:
    def __init__(self, provider, api_key, formats, output_dir, custom_prompt="", example_text=""):
        self.provider = provider
        self.formats = formats
        self.output_dir = output_dir
        self.custom_prompt = custom_prompt
        self.example_text = example_text

        # --- Gestione chiavi: Cassaforte > campo manuale ---
        km = KeyManager()
        km_keys = km.get_all_keys(provider)
        if km_keys:
            self.api_keys = km_keys
            logging.info(f"[OCR] Cassaforte: {len(km_keys)} chiave/i disponibili per {provider}.")
        elif api_key:
            self.api_keys = [api_key]
            logging.info(f"[OCR] Chiave manuale in uso per {provider}.")
        else:
            raise ValueError(f"Nessuna API Key disponibile per {provider}. Aprire la Cassaforte e inserire almeno una chiave.")

        self.current_key_idx = 0

    def _current_key(self):
        return self.api_keys[self.current_key_idx]

    def _rotate_key(self):
        """Passa alla prossima chiave disponibile. Ritorna False se ha esaurito il giro."""
        next_idx = (self.current_key_idx + 1) % len(self.api_keys)
        if next_idx == 0:
            return False  # Giro completo, tutte le chiavi sature
        self.current_key_idx = next_idx
        logging.warning(f"[OCR] Rotazione chiave → slot {next_idx + 1}/{len(self.api_keys)}")
        return True

    def process_file(self, f_path, review_callback=None):
        """Elabora un singolo file immagine con retry automatico sulle chiavi."""
        logging.info(f"[OCR] Elaborazione: {os.path.basename(f_path)}")

        ext = os.path.splitext(f_path)[1].lower()
        if ext == ".pdf":
            logging.warning("[OCR] Supporto PDF diretto richiede pdf2image. Saltato.")
            return

        last_error = None
        for attempt in range(len(self.api_keys)):
            try:
                raw_text = self._transcribe_image(f_path, self._current_key())

                # Revisione interattiva opzionale
                final_text = raw_text
                if review_callback:
                    final_text = review_callback(f_path, raw_text)
                    if final_text is None:
                        logging.info(f"[OCR] Salvataggio saltato dall'utente.")
                        return

                self._save_results(f_path, final_text)
                return  # Successo

            except Exception as e:
                err_str = str(e).lower()
                last_error = e
                is_quota = any(k in err_str for k in ["429", "quota", "resource_exhausted", "rate"])
                if is_quota:
                    logging.warning(f"[OCR] Quota esaurita ({self._current_key()[:6]}...). Tentativo rotazione chiave...")
                    if not self._rotate_key():
                        break  # Tutte le chiavi sature
                else:
                    raise e  # Errore non recuperabile, rilancia

        raise Exception(f"[OCR] Tutte le chiavi esaurite. Ultimo errore: {last_error}")

    def _transcribe_image(self, img_path, api_key):
        """Chiama Gemini con scoperta dinamica del modello migliore."""
        from ai_utils import get_best_gemini_model
        model = get_best_gemini_model(api_key, preferred="flash")
        logging.info(f"[OCR] Modello selezionato: {model}")

        url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"

        # Prepara e ottimizza immagine
        with Image.open(img_path) as img:
            max_size = 3072
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                img = img.resize((int(img.size[0] * ratio), int(img.size[1] * ratio)), Image.Resampling.LANCZOS)
            if img.mode != "RGB":
                img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")

        # Se è stato passato un prompt composto (da compose_ocr_prompt via dialog), usarlo direttamente.
        # Altrimenti usa il prompt generico di fallback.
        if self.custom_prompt:
            prompt = self.custom_prompt
        else:
            prompt = (
                "Sei un esperto di paleografia e diplomatica.\n"
                "TRASCRIVI FEDELMENTE il testo contenuto in questa immagine.\n"
                "REGOLE ASSOLUTE:\n"
                "1. Mantieni la disposizione del testo originale (a capo, paragrafi).\n"
                "2. Non aggiungere commenti, introduzioni o conclusioni.\n"
                "3. Se il testo è incerto, usa [?].\n"
                "4. Sciogli le abbreviazioni ovvie tra parentesi angolate < >.\n"
                "5. Non normalizzare nomi propri o termini dialettali.\n"
            )
            if self.example_text:
                prompt += f"\nTRASCRIZIONE DI ESEMPIO (stessa calligrafia):\n{self.example_text}\n"
            prompt += "\nINIZIA LA TRASCRIZIONE:"

        payload = {
            "contents": [{"parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
            ]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 4096}
        }

        resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=120)
        resp.raise_for_status()
        res_json = resp.json()

        if "candidates" in res_json:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        raise Exception(f"Risposta Gemini vuota: {res_json}")

    def _save_results(self, orig_path, text):
        base_name = os.path.splitext(os.path.basename(orig_path))[0]

        if "txt" in self.formats:
            out_p = os.path.join(self.output_dir, f"{base_name}_trascrizione.txt")
            with open(out_p, "w", encoding="utf-8") as f:
                f.write(text)
            logging.info(f"[OCR] TXT salvato: {out_p}")

        if "docx" in self.formats:
            try:
                import docx
                doc = docx.Document()
                doc.add_heading(f"Trascrizione: {base_name}", 0)
                doc.add_paragraph(text)
                out_p = os.path.join(self.output_dir, f"{base_name}_trascrizione.docx")
                doc.save(out_p)
                logging.info(f"[OCR] DOCX salvato: {out_p}")
            except Exception as e:
                logging.error(f"[OCR] Errore salvataggio DOCX: {e}")

        if "xml" in self.formats:
            out_p = os.path.join(self.output_dir, f"{base_name}_trascrizione.xml")
            safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            xml = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<TEI xmlns="http://www.tei-c.org/ns/1.0">\n'
                f'  <teiHeader><fileDesc><titleStmt><title>Trascrizione di {base_name}</title></titleStmt></fileDesc></teiHeader>\n'
                f'  <text><body><ab>{safe}</ab></body></text>\n'
                '</TEI>'
            )
            with open(out_p, "w", encoding="utf-8") as f:
                f.write(xml)
            logging.info(f"[OCR] XML TEI salvato: {out_p}")
