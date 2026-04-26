# -----------------------------------------------------------------------------
# ATK-Pro v1.5 – tile_rebuilder.py
# Data creazione: 2025-08-15
#
# RESPONSABILITÀ:
# • Lettura dei singoli tasselli (tile) da disco
# • Ricomposizione in un’unica immagine a griglia
# • Embed di metadati EXIF/PNG + creazione sidecar JSON
# • Salvataggio e logging
# -----------------------------------------------------------------------------

# === Copertura test ===
# tests/test_tile_rebuilder.py → ricostruzione tile, gestione tile mancanti
# tests/test_tile_rebuilder_extra.py → tile corrotte, mismatch dimensioni, fallback
# ✅ Validato (logico) — test attivi e rami difensivi verificati

import os
import json
import logging
import argparse
from typing import List, Tuple, Optional, Dict, Any
from PIL import Image, PngImagePlugin, ImageDraw, ImageFont
import piexif


def build_image_metadata(
    ua: Optional[str] = None,
    ark: Optional[str] = None,
    canvas_id: Optional[str] = None,
    page_label: Optional[str] = None,
    range_label: Optional[str] = None,
    description: Optional[str] = None,
    source_url: Optional[str] = None,
    atk_version: str = "1.5"
) -> Dict[str, Any]:
    """Costruisce il dizionario dei metadati da inserire in EXIF/PNG e nel .json sidecar."""
    meta: Dict[str, Any] = {}
    if description:
        meta["Description"] = description
    if ua:
        meta["UA"] = ua
    if ark:
        meta["ARK"] = ark
    if canvas_id:
        meta["CanvasID"] = canvas_id
    if page_label:
        meta["Page"] = page_label
    if range_label:
        meta["Range"] = range_label
    if source_url:
        meta["Source"] = source_url
    meta["Software"] = "Antenati ToolKit Pro"
    meta["ATK-Pro-Version"] = atk_version
    # Prepara lo JSON sidecar (stesso contenuto, indentato)
    sidecar = {k: v for k, v in meta.items()}
    meta["_json"] = json.dumps(sidecar, ensure_ascii=False, indent=2)
    return meta


def _exif_from_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
    """Converte il dict meta in struttura EXIF per piexif."""
    zeroth_ifd: Dict[int, bytes] = {}
    exif_ifd: Dict[int, bytes] = {}
    # ImageDescription
    if "Description" in meta:
        zeroth_ifd[piexif.ImageIFD.ImageDescription] = meta["Description"].encode("utf-8")
    # Artist (UA)
    if "UA" in meta:
        zeroth_ifd[piexif.ImageIFD.Artist] = meta["UA"].encode("utf-8")
    return {"0th": zeroth_ifd, "Exif": exif_ifd}

class TileRebuilder:
    """Classe per la ricomposizione di tasselli in un’unica immagine."""

    def __init__(
        self,
        input_dir: str,
        output_path: str,
        grid_size: Tuple[int, int],
        tile_size: Tuple[int, int],
        padding: Tuple[int, int] = (0, 0),
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.input_dir = input_dir
        self.output_path = output_path
        self.columns, self.rows = grid_size
        self.tile_w, self.tile_h = tile_size
        self.pad_x, self.pad_y = padding
        self.metadata = metadata or {}
        self._validate_params()
        logging.debug(
            f"Initialized with {self.columns}x{self.rows} grid, "
            f"tile {self.tile_w}×{self.tile_h}, padding {self.pad_x},{self.pad_y}"
        )

    def _validate_params(self) -> None:
        if not os.path.isdir(self.input_dir):
            raise FileNotFoundError(f"Directory non trovata: {self.input_dir}")
        if self.columns < 1 or self.rows < 1:
            raise ValueError("grid_size deve essere >= 1 per colonne e righe")
        if self.tile_w < 1 or self.tile_h < 1:
            raise ValueError("tile_size deve essere >= 1 per larghezza e altezza")

    def load_tiles(self) -> List[Image.Image]:
        """Carica tutti i file immagine ordinati per nome."""
        tiles: List[Image.Image] = []
        for fname in sorted(os.listdir(self.input_dir)):
            path = os.path.join(self.input_dir, fname)
            try:
                img = Image.open(path)
                tiles.append(img)
            except Exception as e:
                logging.warning(f"Skip non-image {fname}: {e}")
        return tiles

    def rebuild(self) -> Image.Image:
        """Ricompone le tile in un'unica immagine e restituisce il canvas PIL.Image (con footer opzionale)."""
        tiles = self.load_tiles()
        expected = self.columns * self.rows
        if len(tiles) != expected:
            logging.warning(
                f"Numero di tile ({len(tiles)}) non corrisponde a grid_size ({expected})"
            )
        
        total_w = self.columns * self.tile_w + (self.columns - 1) * self.pad_x
        total_h = self.rows * self.tile_h + (self.rows - 1) * self.pad_y
        
        # --- FOOTER LOGIC (AIT Integration) ---
        source_url = self.metadata.get("Source")
        footer_height = 60 if source_url else 0
        
        canvas = Image.new("RGB", (total_w, total_h + footer_height), (255, 255, 255))
        
        # Incolla le tile
        for idx, tile in enumerate(tiles):
            row = idx // self.columns
            col = idx % self.columns
            x = col * (self.tile_w + self.pad_x)
            y = row * (self.tile_h + self.pad_y)
            canvas.paste(tile, (x, y))
            
        # Aggiunge il testo nel footer se presente
        if source_url:
            draw = ImageDraw.Draw(canvas)
            font = None
            # Font standard per Windows, macOS e Linux
            font_paths = [
                "arial.ttf", "Arial.ttf", 
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
            ]
            for fpath in font_paths:
                try:
                    font = ImageFont.truetype(fpath, 35)
                    break
                except:
                    continue
            if not font:
                font = ImageFont.load_default()
            
            label_text = f"Source: {source_url}"
            draw.text((20, total_h + 10), label_text, fill=(0, 0, 0), font=font)
            
        return canvas

    def save(self) -> None:
        """Ricompone le tile, embed di metadata PNG e salva l'immagine + sidecar JSON."""
        new_img = self.rebuild()
        png_info = PngImagePlugin.PngInfo()
        for key, value in self.metadata.items():
            if key == "_json":
                png_info.add_text("json", value)
            else:
                png_info.add_text(key, str(value))
        new_img.save(self.output_path, pnginfo=png_info)
        sidecar_path = os.path.splitext(self.output_path)[0] + ".json"
        with open(sidecar_path, "w", encoding="utf-8") as f:
            to_dump = {k: v for k, v in self.metadata.items() if k != "_json"}
            json.dump(to_dump, f, ensure_ascii=False, indent=2)

def run() -> None:
    """Entry-point CLI. Ricostruisce la griglia di tile in un'unica immagine."""
    parser = argparse.ArgumentParser(
        prog="tile_rebuilder",
        description="Ricompone una griglia di tile in un'unica immagine con metadata"
    )
    parser.add_argument("input_dir", help="Directory contenente le tile")
    parser.add_argument("output_path", help="File di output per l'immagine")
    parser.add_argument("--columns", "-c", type=int, required=True, help="Numero di colonne")
    parser.add_argument("--rows", "-r", type=int, required=True, help="Numero di righe")
    parser.add_argument("--tile-width", "-w", type=int, required=True, help="Larghezza tile")
    # -h è riservato per --help; usare -H per evitare conflitti
    parser.add_argument("--tile-height", "-H", type=int, required=True, help="Altezza tile")
    parser.add_argument("--pad-x", type=int, default=0, help="Padding orizzontale")
    parser.add_argument("--pad-y", type=int, default=0, help="Padding verticale")
    parser.add_argument("--ua", help="User agent / operatore")
    parser.add_argument("--ark", help="ARK identifier")
    parser.add_argument("--canvas-id", help="ID del canvas IIIF")
    parser.add_argument("--page-label", help="Etichetta pagina")
    parser.add_argument("--range-label", help="Etichetta range")
    parser.add_argument("--description", help="Descrizione immagine finale")
    parser.add_argument("--source-url", help="URL di provenienza")
    parser.add_argument("--atk-version", default="1.5", help="Versione ATK-Pro")

    args = parser.parse_args()

    metadata = build_image_metadata(
        ua=args.ua,
        ark=args.ark,
        canvas_id=args.canvas_id,
        page_label=args.page_label,
        range_label=args.range_label,
        description=args.description,
        source_url=args.source_url,
        atk_version=args.atk_version
    )

    rebuilder = TileRebuilder(
        input_dir=args.input_dir,
        output_path=args.output_path,
        grid_size=(args.columns, args.rows),
        tile_size=(args.tile_width, args.tile_height),
        padding=(args.pad_x, args.pad_y),
        metadata=metadata
    )
    rebuilder.save()

__all__ = ["build_image_metadata", "TileRebuilder", "run", "rebuild_image"]


def rebuild_image(info: Dict[str, Any], tile_dir: str, source_url: str = None) -> Image.Image:
    """
    Funzione helper per ricostruire un'immagine da tiles (compatibile con v1.4.1).
    
    Parametri:
    - info: dict IIIF info.json con width, height, tiles
    - tile_dir: directory contenente i tile file
    - source_url: URL opzionale da inserire nel footer
    
    Ritorna: PIL Image ricostruita
    """
    width = info.get("width", 256)
    height = info.get("height", 256)
    tile_size = info["tiles"][0]["width"]
    
    # Calcola grid
    cols = (width + tile_size - 1) // tile_size
    rows = (height + tile_size - 1) // tile_size
    
    # --- FOOTER LOGIC ---
    footer_height = 60 if source_url else 0
    final_image = Image.new("RGB", (width, height + footer_height), (255, 255, 255))
    
    # Crea canvas e incolla tile
    for y in range(rows):
        for x in range(cols):
            tile_filename = os.path.join(tile_dir, f"tile_{x}_{y}.jpg")
            if os.path.exists(tile_filename):
                try:
                    tile = Image.open(tile_filename)
                    final_image.paste(tile, (x * tile_size, y * tile_size))
                except Exception as e:
                    logging.warning("Errore caricamento tile %s: %s", tile_filename, e)
            else:
                logging.debug("Tile mancante: tile_%d_%d.jpg", x, y)
    
    # Disegna footer
    if source_url:
        draw = ImageDraw.Draw(final_image)
        font = None
        font_paths = [
            "arial.ttf", "Arial.ttf", 
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        ]
        for fpath in font_paths:
            try:
                font = ImageFont.truetype(fpath, 35)
                break
            except:
                continue
        if not font:
            font = ImageFont.load_default()
        draw.text((20, height + 10), f"Source: {source_url}", fill=(0, 0, 0), font=font)
        
    return final_image
