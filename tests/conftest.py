from city_metrix.layers import Layer
from geocube.api.core import make_geocube
from tests.tools.general_tools import create_fishnet_grid

# Test zones of a regular 0.01x0.01 grid over a 0.1x0.1 extent
ZONES = create_fishnet_grid(106.7, -6.3, 106.8, -6.2, 0.01).reset_index()
LARGE_ZONES = create_fishnet_grid(106, -7, 107, -6, 0.1).reset_index()


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


class MockMaskLayer(Layer):
    """
    Simple layer where even indices are masked
    """
    def get_data(self, bbox):
        mask_gdf = create_fishnet_grid(*bbox, 0.01).reset_index()
        mask_gdf['index'] = mask_gdf['index'] % 2
        mask = make_geocube(
            vector_data=mask_gdf,
            measurements=['index'],
            resolution=(0.001, 0.001),
            output_crs=4326,
        ).index

        mask = mask.where(mask != 0)
        return mask


class MockGroupByLayer(Layer):
    """
    Simple categorical layer with alternating 1s and 2s
    """
    def get_data(self, bbox):
        group_by_gdf = create_fishnet_grid(*bbox, 0.001).reset_index()
        group_by_gdf['index'] = (group_by_gdf['index'] % 2) + 1
        group_by = make_geocube(
            vector_data=group_by_gdf,
            measurements=['index'],
            resolution=(0.001, 0.001),
            output_crs=4326,
        ).index

        return group_by


class MockLargeLayer(Layer):
    """
    Simple mock layer that just rasterizes the zones
    """
    def get_data(self, bbox):
        arr = make_geocube(
            vector_data=LARGE_ZONES,
            measurements=['index'],
            resolution=(0.01, 0.01),
            output_crs=4326,
        ).index
        return arr


class MockLargeGroupByLayer(Layer):
    """
    Large categorical layer with alternating 1s and 2s
    """

    def get_data(self, bbox):
        group_by_gdf = create_fishnet_grid(*bbox, 0.01).reset_index()
        group_by_gdf['index'] = (group_by_gdf['index'] % 2) + 1
        group_by = make_geocube(
            vector_data=group_by_gdf,
            measurements=['index'],
            resolution=(0.01, 0.01),
            output_crs=4326,
        ).index

        return group_by