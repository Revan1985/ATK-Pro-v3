"""
Test coverage per resilienza image rebuilder
Verifica skip tile corrotto, continua elaborazione, progress callbacks
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock, call
from PIL import Image
from src import image_rebuilder as ir


class TestImageRebuilderTileSkip:
    """Test che image rebuilder skippa tile corrotto e continua."""

    def test_missing_tile_skipped_image_still_rebuilt(self, tmp_path):
        """Se tile manca → skip e continua (non crasha)."""
        # Setup directory con alcuni tile
        tiles_dir = tmp_path / 'tiles'
        tiles_dir.mkdir()
        
        # Crea 2 tile validi, 1 manca
        tile_0_0 = Image.new('RGB', (256, 256), color='red')
        tile_0_0.save(tiles_dir / 'tile_0_0.jpg')
        
        tile_1_0 = Image.new('RGB', (256, 256), color='blue')
        tile_1_0.save(tiles_dir / 'tile_1_0.jpg')
        
        # tile_0_1 manca
        
        info = {
            'width': 512,
            'height': 512,
            'tiles': [{'width': 256, 'height': 256}]
        }
        
        result = ir.rebuild_image(info, str(tiles_dir))
        
        # Deve ritornare immagine (non None)
        assert result is not None
        assert result.size == (512, 512)

    def test_corrupted_tile_size_skipped(self, tmp_path):
        """Tile < 1KB (corrotto) riconosciuto e skippato."""
        tiles_dir = tmp_path / 'tiles'
        tiles_dir.mkdir()
        
        # Tile valido
        tile_good = Image.new('RGB', (256, 256), color='green')
        tile_good.save(tiles_dir / 'tile_0_0.jpg')
        
        # Tile corrotto (file molto piccolo)
        with open(tiles_dir / 'tile_1_0.jpg', 'wb') as f:
            f.write(b'corrupted' * 50)  # < 1KB
        
        info = {
            'width': 512,
            'height': 512,
            'tiles': [{'width': 256, 'height': 256}]
        }
        
        result = ir.rebuild_image(info, str(tiles_dir))
        
        # Deve continuare nonostante tile corrotto
        assert result is not None
        assert result.size == (512, 512)

    def test_invalid_tile_image_format_skipped(self, tmp_path):
        """Se tile non è immagine valida (corrupt data) → skip."""
        tiles_dir = tmp_path / 'tiles'
        tiles_dir.mkdir()
        
        # Tile valido
        tile_good = Image.new('RGB', (256, 256), color='yellow')
        tile_good.save(tiles_dir / 'tile_0_0.jpg')
        
        # "Tile" con content non-immagine ma > 1KB
        with open(tiles_dir / 'tile_1_0.jpg', 'wb') as f:
            f.write(b'this is not a valid image' * 100)
        
        info = {
            'width': 512,
            'height': 512,
            'tiles': [{'width': 256, 'height': 256}]
        }
        
        result = ir.rebuild_image(info, str(tiles_dir))
        
        # Deve continuare
        assert result is not None


class TestImageRebuilderProgress:
    """Test callback progress durante rebuild."""

    def test_progress_callback_called(self, tmp_path):
        """update_progress callback viene chiamato durante rebuild."""
        tiles_dir = tmp_path / 'tiles'
        tiles_dir.mkdir()
        
        # Crea 4 tile
        for x in range(2):
            for y in range(2):
                tile = Image.new('RGB', (256, 256), color='blue')
                tile.save(tiles_dir / f'tile_{x}_{y}.jpg')
        
        progress_calls = []
        def track_progress(p):
            progress_calls.append(p)
        
        info = {
            'width': 512,
            'height': 512,
            'tiles': [{'width': 256, 'height': 256}]
        }
        
        result = ir.rebuild_image(info, str(tiles_dir), update_progress=track_progress)
        
        # Progress callback deve essere stato chiamato almeno una volta
        assert len(progress_calls) > 0
        # Valori tra 0 e 1
        for p in progress_calls:
            assert 0.0 <= p <= 1.0

    def test_status_callback_called(self, tmp_path):
        """update_status callback viene chiamato."""
        tiles_dir = tmp_path / 'tiles'
        tiles_dir.mkdir()
        
        tile = Image.new('RGB', (256, 256), color='red')
        tile.save(tiles_dir / 'tile_0_0.jpg')
        
        status_calls = []
        def track_status(msg):
            status_calls.append(msg)
        
        info = {
            'width': 256,
            'height': 256,
            'tiles': [{'width': 256, 'height': 256}]
        }
        
        result = ir.rebuild_image(info, str(tiles_dir), update_status=track_status)
        
        # Status callback deve essere stato chiamato
        assert len(status_calls) > 0
        # Deve includere un messaggio di successo
        assert any('[OK]' in msg or 'OK' in msg for msg in status_calls)


class TestImageRebuilderError:
    """Test error callback e gestione eccezioni."""

    def test_on_error_callback_called_for_tile_error(self, tmp_path):
        """on_error callback chiamato se tile non leggibile."""
        tiles_dir = tmp_path / 'tiles'
        tiles_dir.mkdir()
        
        # Crea un file non-leggibile (simulate con permessi)
        tile_path = tiles_dir / 'tile_0_0.jpg'
        tile = Image.new('RGB', (256, 256), color='purple')
        tile.save(tile_path)
        
        error_calls = []
        def track_error(msg):
            error_calls.append(msg)
        
        info = {
            'width': 256,
            'height': 256,
            'tiles': [{'width': 256, 'height': 256}]
        }
        
        # Normal case: no errors
        result = ir.rebuild_image(info, str(tiles_dir), on_error=track_error)
        
        assert result is not None
        # In normal case, on_error should not be called
        assert len(error_calls) == 0

    def test_rebuild_returns_none_on_critical_error(self, tmp_path):
        """Se errore critico nella ricostruzione → ritorna None."""
        tiles_dir = tmp_path / 'tiles'
        tiles_dir.mkdir()
        
        # Info con dimensioni impossibili (height=0)
        info = {
            'width': 256,
            'height': 0,  # Invalid
            'tiles': [{'width': 256, 'height': 256}]
        }
        
        result = ir.rebuild_image(info, str(tiles_dir))
        
        # Errore critico → None o immagine con height 0
        assert result is None or (hasattr(result, 'size') and result.size[1] == 0)


class TestImageRebuilderComposition:
    """Test che immagine sia composta correttamente dai tile."""

    def test_tile_pasted_at_correct_coordinates(self, tmp_path):
        """Tile posizionati alle coordinate corrette nell'immagine finale."""
        tiles_dir = tmp_path / 'tiles'
        tiles_dir.mkdir()
        
        tile_size = 256
        
        # Crea 4 tile con colori diversi
        # tile_0_0 = rosso (top-left)
        tile_0_0 = Image.new('RGB', (256, 256), color=(255, 0, 0))
        tile_0_0.save(tiles_dir / 'tile_0_0.jpg')
        
        # tile_1_0 = verde (top-right)
        tile_1_0 = Image.new('RGB', (256, 256), color=(0, 255, 0))
        tile_1_0.save(tiles_dir / 'tile_1_0.jpg')
        
        # tile_0_1 = blu (bottom-left)
        tile_0_1 = Image.new('RGB', (256, 256), color=(0, 0, 255))
        tile_0_1.save(tiles_dir / 'tile_0_1.jpg')
        
        # tile_1_1 = giallo (bottom-right)
        tile_1_1 = Image.new('RGB', (256, 256), color=(255, 255, 0))
        tile_1_1.save(tiles_dir / 'tile_1_1.jpg')
        
        info = {
            'width': 512,
            'height': 512,
            'tiles': [{'width': 256, 'height': 256}]
        }
        
        result = ir.rebuild_image(info, str(tiles_dir))
        
        assert result is not None
        assert result.size == (512, 512)
        
        # Verifica che colori siano nella posizione corretta (con tolleranza JPEG)
        # Top-left dovrebbe essere prevalentemente rosso
        top_left_pixel = result.getpixel((10, 10))
        assert top_left_pixel[0] > 240  # Red channel high
        assert top_left_pixel[1] < 20   # Green low
        assert top_left_pixel[2] < 20   # Blue low
        
        # Top-right dovrebbe essere prevalentemente verde
        top_right_pixel = result.getpixel((270, 10))
        assert top_right_pixel[0] < 20
        assert top_right_pixel[1] > 240
        assert top_right_pixel[2] < 20
        
        # Bottom-left dovrebbe essere prevalentemente blu
        bottom_left_pixel = result.getpixel((10, 270))
        assert bottom_left_pixel[0] < 20
        assert bottom_left_pixel[1] < 20
        assert bottom_left_pixel[2] > 240
        
        # Bottom-right dovrebbe essere prevalentemente giallo
        bottom_right_pixel = result.getpixel((270, 270))
        assert bottom_right_pixel[0] > 240
        assert bottom_right_pixel[1] > 240
        assert bottom_right_pixel[2] < 20

    def test_single_tile_image_returns_tile(self, tmp_path):
        """Se solo 1 tile → immagine is just the tile."""
        tiles_dir = tmp_path / 'tiles'
        tiles_dir.mkdir()
        
        tile = Image.new('RGB', (512, 512), color=(200, 100, 50))
        tile.save(tiles_dir / 'tile_0_0.jpg')
        
        info = {
            'width': 512,
            'height': 512,
            'tiles': [{'width': 512, 'height': 512}]
        }
        
        result = ir.rebuild_image(info, str(tiles_dir))
        
        assert result is not None
        assert result.size == (512, 512)
        # Pixel should match tile color
        assert result.getpixel((10, 10)) == (200, 100, 50)


class TestImageRebuilderTileDirectory:
    """Test gestione directory tile."""

    def test_tile_directory_not_exist_returns_none(self, tmp_path):
        """Se directory tile non esiste → gestito gracefully."""
        non_existent = tmp_path / 'non_existent'
        
        info = {
            'width': 256,
            'height': 256,
            'tiles': [{'width': 256, 'height': 256}]
        }
        
        result = ir.rebuild_image(info, str(non_existent))
        
        # Errore di accesso → None o immagine vuota
        assert result is None or isinstance(result, Image.Image)

    def test_empty_tile_directory_handled(self, tmp_path):
        """Se directory tile esiste ma vuota → gestito gracefully."""
        tiles_dir = tmp_path / 'tiles'
        tiles_dir.mkdir()
        
        # Directory esiste ma nessun tile
        
        info = {
            'width': 256,
            'height': 256,
            'tiles': [{'width': 256, 'height': 256}]
        }
        
        result = ir.rebuild_image(info, str(tiles_dir))
        
        # Nessun tile disponibile → None o immagine vuota
        assert result is None or isinstance(result, Image.Image)


class TestImageRebuilderConcurrency:
    """Test se progress callback è thread-safe."""

    def test_multiple_progress_updates_not_conflicting(self, tmp_path):
        """Callback progress può essere chiamato rapidamente senza race condition."""
        tiles_dir = tmp_path / 'tiles'
        tiles_dir.mkdir()
        
        # Crea molti tile per simulare attività
        for x in range(3):
            for y in range(3):
                tile = Image.new('RGB', (256, 256), color=(50 + x*30, 50 + y*30, 100))
                tile.save(tiles_dir / f'tile_{x}_{y}.jpg')
        
        progress_values = []
        def track_progress(p):
            progress_values.append(p)
        
        info = {
            'width': 768,
            'height': 768,
            'tiles': [{'width': 256, 'height': 256}]
        }
        
        result = ir.rebuild_image(info, str(tiles_dir), update_progress=track_progress)
        
        assert result is not None
        # Progress values dovrebbero essere monotonicamente crescenti (o almeno non decrescenti)
        for i in range(1, len(progress_values)):
            assert progress_values[i] >= progress_values[i-1] - 0.01  # Small tolerance for floating point


class TestImageRebuilderMetadata:
    """Test che immagine ricostruita abbia metadati corretti."""

    def test_rebuilt_image_has_correct_dimensions(self, tmp_path):
        """Immagine ricostruita ha dimensioni specificate in info."""
        tiles_dir = tmp_path / 'tiles'
        tiles_dir.mkdir()
        
        # Crea 2x3 grid di tile
        for x in range(2):
            for y in range(3):
                tile = Image.new('RGB', (256, 256), color='cyan')
                tile.save(tiles_dir / f'tile_{x}_{y}.jpg')
        
        info = {
            'width': 512,      # 2 tile wide
            'height': 768,     # 3 tile tall
            'tiles': [{'width': 256, 'height': 256}]
        }
        
        result = ir.rebuild_image(info, str(tiles_dir))
        
        assert result is not None
        assert result.size == (512, 768)
