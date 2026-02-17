from PIL import Image
import os
from src.image_rebuilder import rebuild_image


def _save_png(path, size=(256, 256), color=(255, 0, 0)):
    im = Image.new('RGB', size, color=color)
    im.save(path, format='PNG')


def test_rebuild_on_error_called_and_continues(tmp_path, capsys):
    info = {"width": 512, "height": 512, "tiles": [{"width": 256}]}
    td = tmp_path / 'tiles_err'
    td.mkdir()

    # valid tile at 0,0
    _save_png(td / 'tile_0_0.jpg', size=(256, 256), color=(10, 20, 30))
    # invalid tile file for 1,0 (will make Image.open raise)
    bad = td / 'tile_1_0.jpg'
    bad.write_bytes(b'not-an-image')

    errors = []

    def on_error(msg):
        errors.append(msg)

    final = rebuild_image(info, str(td), on_error=on_error)
    # final image should be returned despite the bad tile
    assert final is not None
    # on_error should have been called at least once
    assert len(errors) >= 1
    captured = capsys.readouterr()
    assert 'Errore con il tile' in captured.out or 'Errore con il tile' in captured.err


def test_rebuild_skips_small_tile_and_logs(tmp_path, capsys):
    info = {"width": 512, "height": 512, "tiles": [{"width": 256}]}
    td = tmp_path / 'tiles_small'
    td.mkdir()

    # small tile 1x1 will be considered too small
    _save_png(td / 'tile_0_0.jpg', size=(1, 1), color=(1, 2, 3))
    # other tiles valid
    _save_png(td / 'tile_1_0.jpg', size=(256, 256), color=(4, 5, 6))
    final = rebuild_image(info, str(td))
    assert final is not None
    out = capsys.readouterr().out
    assert 'Tile corrotto o troppo piccolo' in out


def test_rebuild_pastes_oversized_tile(tmp_path):
    # If a tile is larger than tile_size it should still be pasted and cover the area
    info = {"width": 512, "height": 512, "tiles": [{"width": 256}]}
    td = tmp_path / 'tiles_big'
    td.mkdir()

    # create a tile larger than tile_size at 0,0 (300x300)
    _save_png(td / 'tile_0_0.jpg', size=(300, 300), color=(200, 10, 10))
    # leave other tiles missing to see the effect

    final = rebuild_image(info, str(td))
    assert final is not None
    # pixel at x=260 (inside oversized tile) should reflect tile color
    assert final.getpixel((260, 10))[:3] == (200, 10, 10)
