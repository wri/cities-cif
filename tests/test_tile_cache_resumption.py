import os
from pathlib import Path

import pytest

from city_metrix.constants import GTIFF_FILE_EXTENSION
from city_metrix.metrix_model import (
    GeoExtent,
    Layer,
    ProjectionType,
    construct_tile_name,
    create_fishnet_grid,
)


class DummyTileLayer(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    PROCESSING_TILE_SIDE_M = 50

    def __init__(self):
        super().__init__()
        self.processed_tiles = []

    def get_data(self, bbox, spatial_resolution: int = None, resampling_method: str = None):
        raise NotImplementedError

    def _process_fishnet_tile(self, index, tile, crs, spatial_resolution, temp_dir, target_uri):
        self.processed_tiles.append(index)
        file_name = construct_tile_name(index)
        temp_file_path = os.path.join(temp_dir, file_name)
        Path(temp_file_path).write_text("tile")
        target_tile_uri = f"{target_uri}/{file_name}"
        self._write_data_to_cache(temp_file_path, target_tile_uri)
        os.remove(temp_file_path)
        return {index: None}


def test_get_completed_tile_ids_ignores_processing_failures():
    layer = DummyTileLayer()
    files = [
        "/tmp/tile_00001.tif",
        "/tmp/tile_00002_processing_failed.tif",
        "/tmp/tile_00003.tif",
    ]

    assert layer._get_completed_tile_ids(files) == [1, 3]


def test_cache_resume_skips_completed_tiles(tmp_path):
    layer = DummyTileLayer()
    bbox = GeoExtent((0, 0, 150, 150), crs="EPSG:32631")
    target_uri = tmp_path / "tile-cache"

    layer._cache_data_by_fishnet_tiles(
        bbox=bbox,
        tile_side_m=layer.PROCESSING_TILE_SIDE_M,
        spatial_resolution=10,
        target_uri=str(target_uri),
        force_refresh=True,
    )

    fishnet = create_fishnet_grid(
        bbox=bbox,
        tile_side_length=layer.PROCESSING_TILE_SIDE_M,
        length_units="meters",
        spatial_resolution=10,
        output_as=ProjectionType.UTM,
    )
    expected_tile_count = len(fishnet)
    completed_tiles = sorted(
        p.name
        for p in target_uri.glob("tile_*.tif")
        if p.is_file() and "processing_failed" not in p.name
    )
    assert len(completed_tiles) == expected_tile_count

    missing_tile = completed_tiles[0]
    missing_tile_id = int(missing_tile.split("_")[1].split(".")[0])
    (target_uri / missing_tile).unlink()
    (target_uri / "tile_99999_processing_failed.tif").touch()

    assert layer._has_incomplete_tile_cache(
        bbox, layer.PROCESSING_TILE_SIDE_M, 10, str(target_uri)
    )

    layer.processed_tiles = []
    layer._cache_data_by_fishnet_tiles(
        bbox=bbox,
        tile_side_m=layer.PROCESSING_TILE_SIDE_M,
        spatial_resolution=10,
        target_uri=str(target_uri),
    )

    completed_tiles_after_resume = sorted(
        p.name
        for p in target_uri.glob("tile_*.tif")
        if p.is_file() and "processing_failed" not in p.name
    )
    assert len(completed_tiles_after_resume) == expected_tile_count
    assert missing_tile in completed_tiles_after_resume
    assert len(layer.processed_tiles) == 1
    assert layer.processed_tiles[0] == missing_tile_id
    assert not layer._has_incomplete_tile_cache(
        bbox, layer.PROCESSING_TILE_SIDE_M, 10, str(target_uri)
    )
