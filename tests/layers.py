from city_metrix.layers import Layer

import shapely.geometry as geometry
import geopandas as gpd
from geocube.api.core import make_geocube


def create_fishnet_grid(min_x, min_y, max_x, max_y, cell_size):
    x, y = (min_x, min_y)
    geom_array = []

    # Polygon Size
    while y < (max_y - 0.000001):
        while x < (max_x - 0.000001):
            geom = geometry.Polygon(
                [
                    (x, y),
                    (x, y + cell_size),
                    (x + cell_size, y + cell_size),
                    (x + cell_size, y),
                    (x, y),
                ]
            )
            geom_array.append(geom)
            x += cell_size
        x = min_x
        y += cell_size

    fishnet = gpd.GeoDataFrame(geom_array, columns=["geometry"]).set_crs("EPSG:4326")
    return fishnet

# Test zones of a regular 0.01x0.01 grid over a 0.1x0.1 extent
ZONES = create_fishnet_grid(106.7, -6.3, 106.8, -6.2, 0.01).reset_index()


class MockLayer(Layer):
    """
    Simple mock layer that just rasterizes the zones
    """
    def get_data(self, bbox):
        arr = make_geocube(
            vector_data=ZONES,
            measurements=['index'],
            resolution=(0.001, 0.001),
            output_crs=4326,
        ).index
        return arr


def test_count():
    counts = MockLayer().groupby(ZONES).count()
    assert counts.size == 100
    assert all([count == 100 for count in counts])


def test_mean():
    means = MockLayer().groupby(ZONES).mean()
    assert means.size == 100
    assert all([mean == i for i, mean in enumerate(means)])


