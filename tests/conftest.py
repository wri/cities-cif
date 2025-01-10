from city_metrix.layers import Layer
from city_metrix.layers.layer import create_fishnet_grid
from geocube.api.core import make_geocube

# EXECUTE_IGNORED_TESTS is the master control for whether to execute tests decorated with
# pytest.mark.skipif. These tests are temporarily ignored due to some unresolved issue.
# Setting EXECUTE_IGNORED_TESTS to True turns on code execution. This should be done for local testing.
# The value must be set to False when pushing to GitHub since the ignored tests would otherwise fail
# in GitHub Actions.
EXECUTE_IGNORED_TESTS = False

def test_create_fishnet_grid(min_x, min_y, max_x, max_y, cell_size):
    # Slightly reduce aoi to avoid partial cells
    reduction = 0.000001
    max_y = (max_y - reduction)
    max_x = (max_x - reduction)
    fishnet = create_fishnet_grid(min_x, min_y, max_x, max_y, cell_size)
    fishnet.drop('fishnet_geometry', axis=1, inplace=True)
    return fishnet

# Test zones of a regular 0.01x0.01 grid over a 0.1x0.1 extent by degrees
ZONES = test_create_fishnet_grid(106.7, -6.3, 106.8, -6.2, 0.01).reset_index()
LARGE_ZONES = test_create_fishnet_grid(106, -7, 107, -6, 0.1).reset_index()


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
        cell_size_degrees = 0.01
        mask_gdf = test_create_fishnet_grid(*bbox, cell_size_degrees).reset_index()
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
        cell_size_degrees = 0.001
        group_by_gdf = test_create_fishnet_grid(*bbox, cell_size_degrees).reset_index()
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
        cell_size_degrees =  0.01
        group_by_gdf = test_create_fishnet_grid(*bbox, cell_size_degrees).reset_index()
        group_by_gdf['index'] = (group_by_gdf['index'] % 2) + 1
        group_by = make_geocube(
            vector_data=group_by_gdf,
            measurements=['index'],
            resolution=(0.01, 0.01),
            output_crs=4326,
        ).index

        return group_by
