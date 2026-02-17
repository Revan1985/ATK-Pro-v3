import os
from PIL import Image
from src.image_rebuilder import rebuild_image


def _create_tile(path, color=(0, 0, 0)):
    im = Image.new('RGB', (256, 256), color=color)
    im.save(path, format='PNG')


def test_rebuild_image_with_scaled_names(tmp_path):
    info = {"width": 512, "height": 512, "tiles": [{"width": 256}]}
    tile_dir = tmp_path / 'tiles_scaled'
    tile_dir.mkdir()

    # create 4 tiles using scaled names (pixel offsets)
    _create_tile(tile_dir / 'tile_0_0.jpg', color=(255, 0, 0))
    _create_tile(tile_dir / 'tile_256_0.jpg', color=(0, 255, 0))
    _create_tile(tile_dir / 'tile_0_256.jpg', color=(0, 0, 255))
    _create_tile(tile_dir / 'tile_256_256.jpg', color=(255, 255, 0))

    final = rebuild_image(info, str(tile_dir))
    assert final is not None
    assert final.size == (512, 512)
    # check some pixels correspond to tile colors
    assert final.getpixel((10, 10)) == (255, 0, 0)
    assert final.getpixel((300, 10))[:2] == (0, 255)


def test_rebuild_image_with_simple_names_and_missing_tile(tmp_path, capsys):
    info = {"width": 512, "height": 512, "tiles": [{"width": 256}]}
    tile_dir = tmp_path / 'tiles_simple'
    tile_dir.mkdir()

    # create only three tiles using simple names (col,row)
    _create_tile(tile_dir / 'tile_0_0.jpg', color=(1, 2, 3))
    _create_tile(tile_dir / 'tile_1_0.jpg', color=(4, 5, 6))
    # missing tile_0_1.jpg to trigger 'Tile mancante'
    _create_tile(tile_dir / 'tile_1_1.jpg', color=(7, 8, 9))

    final = rebuild_image(info, str(tile_dir))
    assert final is not None
    captured = capsys.readouterr()
    assert 'Tile mancante' in captured.out
