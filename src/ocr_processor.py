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

    def process_file(self, f_path, review_callback=None, page_progress=None):
        """Elabora un singolo file (immagine o PDF) con retry automatico sulle chiavi."""
        logging.info(f"[OCR] Elaborazione: {os.path.basename(f_path)}")

        ext = os.path.splitext(f_path)[1].lower()
        if ext == ".pdf":
            self._process_pdf(f_path, review_callback, page_progress)
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

    def _process_pdf(self, pdf_path, review_callback=None, page_progress=None):
        """Converte ogni pagina del PDF in immagine e le trascrive una per una."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise Exception("[OCR] PyMuPDF non installato. Esegui: pip install pymupdf")

        import tempfile
        doc = fitz.open(pdf_path)
        n_pages = len(doc)
        logging.info(f"[OCR] PDF: {n_pages} pagine trovate — {os.path.basename(pdf_path)}")

        all_texts = []
        with tempfile.TemporaryDirectory() as tmp_dir:
            for page_num in range(n_pages):
                if page_progress:
                    page_progress(page_num + 1, n_pages)

                page = doc[page_num]
                # Render a 200 DPI per leggibilità ottimale
                mat = fitz.Matrix(200 / 72, 200 / 72)
                pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
                img_path = os.path.join(tmp_dir, f"page_{page_num + 1:04d}.jpg")
                pix.save(img_path)
                logging.info(f"[OCR] PDF pagina {page_num + 1}/{n_pages} → {img_path}")

                # Trascrivi con retry chiavi
                last_error = None
                page_text = None
                for attempt in range(len(self.api_keys)):
                    try:
                        page_text = self._transcribe_image(img_path, self._current_key())
                        break
                    except Exception as e:
                        err_str = str(e).lower()
                        last_error = e
                        is_quota = any(k in err_str for k in ["429", "quota", "resource_exhausted", "rate"])
                        if is_quota:
                            if not self._rotate_key():
                                break
                        else:
                            raise e

                if page_text is None:
                    raise Exception(f"[OCR] Pagina {page_num + 1}: tutte le chiavi esaurite. {last_error}")

                # Revisione interattiva per pagina (immagine temp ancora disponibile)
                final_page_text = page_text
                if review_callback:
                    result = review_callback(img_path, page_text)
                    if result is None:
                        logging.info(f"[OCR] Pagina {page_num + 1} saltata dall'utente.")
                        continue
                    final_page_text = result

                all_texts.append(f"--- Pagina {page_num + 1} ---\n{final_page_text}")

        doc.close()

        if not all_texts:
            logging.info("[OCR] Nessuna pagina approvata. File non salvato.")
            return

        full_text = "\n\n".join(all_texts)
        self._save_results(pdf_path, full_text)

    def _prepare_image_b64(self, img_path):
        """Carica, ridimensiona e converte l'immagine in JPEG base64."""
        with Image.open(img_path) as img:
            max_size = 3072
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                img = img.resize((int(img.size[0] * ratio), int(img.size[1] * ratio)), Image.Resampling.LANCZOS)
            if img.mode != "RGB":
                img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            return base64.b64encode(buf.getvalue()).decode("utf-8")

    def _build_prompt(self):
        """Costruisce il prompt da usare per la trascrizione."""
        if self.custom_prompt:
            prompt = self.custom_prompt
            if self.example_text:
                prompt += (
                    f"\n\nTRASCRIZIONE DI ESEMPIO (stessa calligrafia — segui questo stile):"
                    f"\n{self.example_text}\n\nINIZIA LA TRASCRIZIONE:"
                )
            return prompt
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
        return prompt

    def _transcribe_image(self, img_path, api_key):
        """Dispatcher: instrada al provider corretto."""
        b64_img = self._prepare_image_b64(img_path)
        prompt  = self._build_prompt()
        provider = (self.provider or "Gemini").strip()
        if "OpenAI" in provider or "GPT" in provider:
            return self._transcribe_openai(api_key, b64_img, prompt)
        if "Anthropic" in provider or "Claude" in provider:
            return self._transcribe_anthropic(api_key, b64_img, prompt)
        return self._transcribe_gemini(api_key, b64_img, prompt)

    def _transcribe_gemini(self, api_key, b64_img, prompt):
        """Trascrizione via Gemini REST (scoperta dinamica del modello)."""
        from ai_utils import get_best_gemini_model
        model = get_best_gemini_model(api_key, preferred="flash")
        logging.info(f"[OCR] Gemini — modello: {model}")
        url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"
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

    def _transcribe_openai(self, api_key, b64_img, prompt):
        """Trascrizione via OpenAI Vision (gpt-4o)."""
        logging.info("[OCR] OpenAI — modello: gpt-4o")
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-4o",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{b64_img}", "detail": "high"}}
                ]
            }],
            "temperature": 0.1,
            "max_tokens": 4096
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        res_json = resp.json()
        try:
            return res_json["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise Exception(f"Risposta OpenAI non valida: {res_json}")

    def _transcribe_anthropic(self, api_key, b64_img, prompt):
        """Trascrizione via Anthropic Messages API (claude-opus-4-5)."""
        logging.info("[OCR] Anthropic — modello: claude-opus-4-5")
        url = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": "claude-opus-4-5",
            "max_tokens": 4096,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image",
                     "source": {"type": "base64", "media_type": "image/jpeg", "data": b64_img}},
                    {"type": "text", "text": prompt}
                ]
            }]
        }
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        res_json = resp.json()
        try:
            return res_json["content"][0]["text"]
        except (KeyError, IndexError):
            raise Exception(f"Risposta Anthropic non valida: {res_json}")

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
            from datetime import date as _date
            tei_body = self._text_to_tei_body(text)
            xml = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<TEI xmlns="http://www.tei-c.org/ns/1.0">\n'
                '  <teiHeader>\n'
                '    <fileDesc>\n'
                '      <titleStmt>\n'
                f'        <title>Trascrizione di {base_name}</title>\n'
                '      </titleStmt>\n'
                '      <publicationStmt>\n'
                f'        <p>Trascrizione automatica ATK-Pro — {_date.today().isoformat()}</p>\n'
                '      </publicationStmt>\n'
                '      <sourceDesc>\n'
                f'        <p>File originale: {os.path.basename(orig_path)}</p>\n'
                '      </sourceDesc>\n'
                '    </fileDesc>\n'
                '  </teiHeader>\n'
                '  <text>\n'
                '    <body>\n'
                '      <div type="transcription">\n'
                f'{tei_body}'
                '      </div>\n'
                '    </body>\n'
                '  </text>\n'
                '</TEI>'
            )
            with open(out_p, "w", encoding="utf-8") as f:
                f.write(xml)
            logging.info(f"[OCR] XML TEI-P5 salvato: {out_p}")

    def _text_to_tei_body(self, text):
        """Converte il testo trascritto in markup TEI-P5 valido."""
        import re
        out_lines = []
        for line in text.split('\n'):
            # --- Pagina N --- → <pb n="N"/>
            m = re.match(r'^---\s*Pagina\s+(\d+)\s*---$', line.strip())
            if m:
                out_lines.append(f'        <pb n="{m.group(1)}"/>')
                continue

            # Estrai le espansioni < > PRIMA di fare l'escaping
            parts = []
            pos = 0
            for am in re.finditer(r'<([^>]+)>', line):
                before = line[pos:am.start()].replace('&', '&amp;')
                parts.append(before)
                parts.append(f'<expan>{am.group(1)}</expan>')
                pos = am.end()
            remaining = line[pos:].replace('&', '&amp;')
            parts.append(remaining)
            line_content = ''.join(parts)

            # [?] → <unclear reason="illegible"/>
            line_content = re.sub(r'\[\?\]', '<unclear reason="illegible"/>', line_content)

            out_lines.append(f'        <ab>{line_content}</ab>')

        return '\n'.join(out_lines) + '\n'
