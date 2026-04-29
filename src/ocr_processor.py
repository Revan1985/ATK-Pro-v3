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
        """Dispatcher: instrada al provider corretto.
        Per immagini a doppia pagina affiancata (aspect ratio > 1.6) con Gemini,
        esegue lo split TOP/BOTTOM per aumentare l'accuratezza OCR su tabelle lunghe."""
        prompt   = self._build_prompt()
        provider = (self.provider or "Gemini").strip()

        # Per provider non-Gemini usa il path diretto
        if "OpenAI" in provider or "GPT" in provider:
            return self._transcribe_openai(api_key, self._prepare_image_b64(img_path), prompt)
        if "Anthropic" in provider or "Claude" in provider:
            return self._transcribe_anthropic(api_key, self._prepare_image_b64(img_path), prompt)

        # Gemini: split se la tipologia documentale prevede doppia pagina
        # oppure se l'immagine è effettivamente molto larga (foglio aperto fisico)
        with Image.open(img_path) as _probe:
            w, h = _probe.size
        is_double_page = (
            "DOPPIA PAGINA" in prompt  # il tipo documentale lo dichiara esplicitamente
            or ((w / h) >= 1.6 if h > 0 else False)  # o il formato è fisicamente panoramico
        )

        if is_double_page:
            return self._transcribe_gemini_split(img_path, api_key, prompt)

        return self._transcribe_gemini(api_key, self._prepare_image_b64(img_path), prompt)

    def _transcribe_gemini_split(self, img_path, api_key, prompt):
        """Per immagini a doppia pagina affiancata: divide in TOP+BOTTOM,
        trascrive ciascuna metà con il prompt completo (tutte le colonne visibili)
        e concatena le righe. Questo approccio è più accurato dello split SX/DX
        perché ogni chiamata vede tutte le colonne ma su meno righe."""

        with Image.open(img_path) as img:
            w, h = img.size
            # Overlap del 20%: TOP va fino al 60%, BOTTOM parte dal 40%.
            # Ogni riga è garantita di essere completamente visibile in almeno una metà.
            cut_top = int(h * 0.60)
            cut_bottom = int(h * 0.40)
            top_img = img.crop((0, 0, w, cut_top))
            bottom_img = img.crop((0, cut_bottom, w, h))

            def _to_b64(pil_img):
                max_size = 3072
                if max(pil_img.size) > max_size:
                    ratio = max_size / max(pil_img.size)
                    pil_img = pil_img.resize(
                        (int(pil_img.size[0] * ratio), int(pil_img.size[1] * ratio)),
                        Image.Resampling.LANCZOS
                    )
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG", quality=90)
                return base64.b64encode(buf.getvalue()).decode("utf-8")

            b64_top = _to_b64(top_img)
            b64_bottom = _to_b64(bottom_img)

        prompt_top = (
            prompt
            + "\n\nNOTA OPERATIVA — METÀ SUPERIORE DEL REGISTRO:"
            " Stai vedendo i primi 2/3 circa del foglio aperto."
            " Trascrivi TUTTE le righe visibili in questa metà, inclusa la riga di intestazione."
            " Le due pagine fisiche affiancate formano UN'UNICA RIGA ciascuna:"
            " unisci le colonne di sinistra e di destra con ' | ' (come già indicato sopra)."
            "\n⚠ NON inventare righe non visibili nell'immagine."
            "\nESEMPIO FORMATO OBBLIGATORIO (RISPETTA ESATTAMENTE):"
            "\n  capofamiglia Ammogliato:  1 | 1 | 1 | Acciaj | Gaspero | 60 |  | 1 |  |  |  |  | Cattolica |  | Possidente | "
            "\n  moglie (Maritata):        |  | 2 | \" | Rosa | 62 |  |  |  |  | 1 |  | \" |  |  | "
            "\n  figlio Celibe:            |  | 3 | \" | Pietro | 1 | 1 |  |  |  |  |  | \" |  |  | "
            "\n  figlia Nubile:            |  | 4 | \" | Rosa | 2 |  |  |  | 1 |  |  | \" |  |  | "
            "\n  → Nelle righe di continuazione N°Casa (col.1) e N°Famiglia (col.2) sono BLANK."
            "\n  → Il numero progressivo crescente va SEMPRE nella TERZA colonna (N°Progressivo)."
            "\n  → NON mettere il numero progressivo nella seconda colonna (N°Famiglia)."
            "\n⚠ STATO CIVILE — CONTA LE CASELLE DA SINISTRA:"
            " le 6 caselle sono nell'ordine: [1]Celibe [2]Ammogliato [3]Vedovo [4]Nubile [5]Maritata [6]Vedova."
            " Il segno (tratto, croce) in casella [1] = Celibe (maschio); in casella [4] = Nubile (femmina)."
            " NON scambiare [1] con [4]: un bambino di 1 anno con il segno nella PRIMA casella è Celibe=maschio."
        )

        logging.info("[OCR] Immagine a doppia pagina — split TOP/BOTTOM (overlap 20%) per Gemini")
        text_top = self._transcribe_gemini(api_key, b64_top, prompt_top)

        # Costruisci contesto dalle ultime righe del TOP per aiutare il modello BOTTOM
        # a riconoscere cambi di nucleo familiare alla prima riga visibile.
        _lines_top_ctx = [l for l in text_top.strip().splitlines() if l.strip()]
        _data_top_ctx = _lines_top_ctx[1:] if len(_lines_top_ctx) > 1 else _lines_top_ctx
        _last_rows = _data_top_ctx[-3:] if _data_top_ctx else []
        _context_note = ""
        if _last_rows:
            _context_note = (
                "\n\nCONTESTO — ultime righe già trascritte dalla metà superiore:\n"
                + "\n".join(_last_rows)
                + "\nUsa queste righe come riferimento per determinare il numero progressivo e il nucleo"
                " familiare in corso. Se la prima riga visibile nella tua immagine appartiene a un"
                " NUOVO nucleo familiare (N°Casa e N°Famiglia diversi dall'ultima riga sopra),"
                " compilane obbligatoriamente le colonne 1 e 2 con i numeri letti nell'immagine."
            )

        prompt_bottom = (
            prompt
            + "\n\nNOTA OPERATIVA — METÀ INFERIORE DEL REGISTRO:"
            " Stai vedendo gli ultimi 2/3 circa del foglio aperto"
            " (con una sovrapposizione rispetto alla metà superiore già trascritta)."
            " Trascrivi TUTTE le righe visibili in questa metà."
            " NON includere la riga di intestazione — inizia direttamente dalla prima riga dati."
            " Le due pagine fisiche affiancate formano UN'UNICA RIGA ciascuna."
            "\n⚠ NON inventare righe non visibili nell'immagine."
            "\nESEMPIO FORMATO:"
            "\n  riga continuazione: |  | 14 | \" | Pietro | 42 |  | 1 |  |  |  |  | \" |  |  | "
            "\n  riga capofamiglia: 4 | 4 | 13 | Bargelli | Caterina | 72 |  |  |  |  |  | 1 | \" |  |  | "
            "\n  → Nelle righe di continuazione N°Casa (col.1) e N°Famiglia (col.2) sono BLANK."
            "\n  → Il numero progressivo va SEMPRE nella TERZA colonna."
            + _context_note
        )

        text_bottom = self._transcribe_gemini(api_key, b64_bottom, prompt_bottom)

        # Salva diagnostica raw TOP/BOTTOM per debugging
        try:
            import pathlib
            stem = pathlib.Path(img_path).stem
            diag_dir = self.output_dir if (self.output_dir and os.path.isdir(self.output_dir)) else os.getcwd()
            for label, raw in (("TOP", text_top), ("BOTTOM", text_bottom)):
                diag_path = os.path.join(diag_dir, f"DIAG_{stem}_{label}.txt")
                with open(diag_path, "w", encoding="utf-8") as _df:
                    _df.write(raw)
            logging.debug(f"[OCR] Diagnostica split salvata in: {diag_dir}")
        except Exception as _de:
            logging.warning(f"[OCR] Impossibile salvare diagnostica split: {_de}")

        lines_top = [l for l in text_top.strip().splitlines() if l.strip()]
        lines_bottom = [l for l in text_bottom.strip().splitlines() if l.strip()]

        # Rimuovi intestazione dal bottom se il modello l'ha inclusa
        if lines_bottom and any(
            k in lines_bottom[0]
            for k in ("N°", "Religione", "Cognome", "Nome", "Età", "Casa", "Famiglia")
        ):
            lines_bottom = lines_bottom[1:]

        if not lines_top:
            return "\n".join(lines_bottom)

        # Merge con column-level fusion per le righe nell'overlap (TOP e BOTTOM).
        # Strategia: per ogni riga presente in entrambi, il TOP è master (ha visibilità ottimale
        # sulla zona superiore). Se il TOP ha un valore non-blank per una colonna, lo usa; altrimenti
        # integra con il BOTTOM. Questo preserva N°Casa/N°Fam dal TOP per le righe di cambio nucleo.
        def _get_prog(row: str):
            parts = [p.strip() for p in row.split("|")]
            if len(parts) >= 3:
                try:
                    return int(parts[2])
                except ValueError:
                    pass
            return None

        def _merge_cols(top_row: str, bot_row: str) -> str:
            """Merge sovrapposizione: BOTTOM è master (lettura ottimale nella zona centrale).
            Il TOP integra SOLO le colonne 0 (N°Casa) e 1 (N°Fam) se il BOTTOM le ha vuote,
            perché il TOP ha visibilità del contesto del nucleo familiare precedente."""
            tc = [c.strip() for c in top_row.split("|")]
            bc = [c.strip() for c in bot_row.split("|")]
            # Riempi N°Casa e N°Fam dal TOP se il BOTTOM è blank
            for idx in (0, 1):
                if idx < len(tc) and idx < len(bc) and not bc[idx] and tc[idx]:
                    bc[idx] = tc[idx]
            return " | ".join(bc)

        header_lines = [lines_top[0]] if lines_top else []
        data_top = lines_top[1:] if len(lines_top) > 1 else []

        # Mappe {prog: riga} per TOP e BOTTOM
        top_map: dict[int, str] = {}
        for row in data_top:
            p = _get_prog(row)
            if p is not None:
                top_map[p] = row

        valid_bottom_progs = [p for p in (_get_prog(l) for l in lines_bottom) if p is not None]
        first_bottom_prog = min(valid_bottom_progs) if valid_bottom_progs else None
        max_top_prog = max(top_map.keys()) if top_map else None

        if first_bottom_prog is not None and max_top_prog is not None:
            # Righe solo nel TOP (prima della zona di overlap)
            rows_top_only = [row for row in data_top
                             if (_get_prog(row) or 0) < first_bottom_prog]

            # Righe nell'overlap: column-level merge (TOP master)
            overlap_rows = []
            for row in lines_bottom:
                p = _get_prog(row)
                if p is not None and p <= max_top_prog:
                    if p in top_map:
                        overlap_rows.append(_merge_cols(top_map[p], row))
                    else:
                        overlap_rows.append(row)  # solo nel BOTTOM

            # Righe solo nel BOTTOM (oltre la fine del TOP)
            rows_bottom_only = [row for row in lines_bottom
                                 if (_get_prog(row) or 0) > max_top_prog]

            merged_data = rows_top_only + overlap_rows + rows_bottom_only
        else:
            # Fallback: comportamento conservativo
            data_top_filtered = [row for row in data_top
                                  if (_get_prog(row) or 0) < (first_bottom_prog or float("inf"))]
            merged_data = data_top_filtered + lines_bottom

        return "\n".join(header_lines + merged_data)

    def _call_gemini_rest(self, api_key, model, b64_img, prompt):
        """Chiama l'API REST Gemini con un'immagine e ritorna il testo."""
        url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
            ]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 32768}
        }
        resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=180)
        resp.raise_for_status()
        res_json = resp.json()
        if "candidates" in res_json:
            candidate = res_json["candidates"][0]
            finish_reason = candidate.get("finishReason", "UNKNOWN")
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"]
            logging.warning(f"[OCR] Gemini risposta senza testo. finishReason={finish_reason}, content={str(content)[:200]}")
            raise Exception(f"Risposta Gemini senza testo (finishReason={finish_reason})")
        raise Exception(f"Risposta Gemini vuota: {res_json}")

    def _transcribe_gemini(self, api_key, b64_img, prompt):
        """Trascrizione via Gemini REST. Per OCR usa pro → flash come fallback."""
        from ai_utils import get_best_gemini_model

        # Ordine di preferenza: prima pro (più accurato su tabelle), poi flash
        model_candidates = [
            get_best_gemini_model(api_key, preferred="pro"),
            get_best_gemini_model(api_key, preferred="flash"),
        ]
        # Rimuovi duplicati mantenendo l'ordine
        seen = set()
        model_candidates = [m for m in model_candidates if m not in seen and not seen.add(m)]

        last_error = None
        for model in model_candidates:
            try:
                logging.info(f"[OCR] Gemini — modello: {model}")
                return self._call_gemini_rest(api_key, model, b64_img, prompt)
            except Exception as e:
                err_str = str(e).lower()
                last_error = e
                if any(k in err_str for k in ["404", "not found", "does_not_exist", "invalid"]):
                    logging.warning(f"[OCR] Modello {model} non disponibile, provo successivo.")
                    continue
                raise e
        raise Exception(f"[OCR] Nessun modello Gemini disponibile. Ultimo errore: {last_error}")

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
