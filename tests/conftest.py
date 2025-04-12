from enum import Enum

from city_metrix.layers import Layer
from city_metrix.constants import WGS_EPSG_CODE, ProjectionType
from city_metrix.layers.layer import create_fishnet_grid, WGS_CRS
from geocube.api.core import make_geocube

from city_metrix.layers.layer_geometry import GeoExtent
from city_metrix.metrics.metric_geometry import GeoZone
from tests.resources.bbox_constants import BBOX_USA_OR_PORTLAND, BBOX_NLD_AMSTERDAM, BBOX_IDN_JAKARTA, \
    BBOX_IDN_JAKARTA_LARGE

# EXECUTE_IGNORED_TESTS is the master control for whether to execute tests decorated with
# pytest.mark.skipif. These tests are temporarily ignored due to some unresolved issue.
# Setting EXECUTE_IGNORED_TESTS to True turns on code execution. This should be done for local testing.
# The value must be set to False when pushing to GitHub since the ignored tests would otherwise fail
# in GitHub Actions.
EXECUTE_IGNORED_TESTS = False

def create_fishnet_gdf_for_testing(coords, tile_side_length):
    min_x, min_y, max_x, max_y = coords
    # Slightly reduce aoi to avoid partial cells
    reduction = 0.000001
    max_y = (max_y - reduction)
    max_x = (max_x - reduction)
    bbox = (min_x, min_y, max_x, max_y)
    wgs_bbox = GeoExtent(bbox=bbox, crs=WGS_CRS)
    fishnet_gdf = create_fishnet_grid(wgs_bbox, tile_side_length=tile_side_length, length_units='degrees',
                                      output_as=ProjectionType.GEOGRAPHIC)
    fishnet_gdf.drop('fishnet_geometry', axis=1, inplace=True)
    fishnet_gdf['geo_id'] = fishnet_gdf.index.map(lambda idx: f"dummy_{idx}")
    return fishnet_gdf

def create_single_bbox_gdf_for_testing(coords):
    min_x, min_y, max_x, max_y = coords
    from shapely import geometry
    import geopandas as gp
    geom_array = []
    poly = geometry.Polygon(((min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, min_y)))
    geom_array.append(poly)
    gdf = gp.GeoDataFrame(geom_array, columns=["geometry"]).set_crs(WGS_CRS)
    return gdf

IDN_JAKARTA_TILED_BBOXES = (
    create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA.coords, 0.01).reset_index())
IDN_JAKARTA_TILED_LARGE_BBOXES = (
    create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA_LARGE.coords, 0.1).reset_index())
USA_OR_PORTLAND_BBOX = create_single_bbox_gdf_for_testing(BBOX_USA_OR_PORTLAND.coords)
NLD_AMSTERDAM_BBOX = create_single_bbox_gdf_for_testing(BBOX_NLD_AMSTERDAM.coords)

# Test zones of a regular 0.01x0.01 grid over a 0.1x0.1 extent by degrees
IDN_JAKARTA_TILED_ZONES = GeoZone(IDN_JAKARTA_TILED_BBOXES)
IDN_JAKARTA_TILED_LARGE_ZONES = GeoZone(IDN_JAKARTA_TILED_LARGE_BBOXES)
# Test single tiles
USA_OR_PORTLAND_ZONE = GeoZone(USA_OR_PORTLAND_BBOX)
NLD_AMSTERDAM_ZONE = GeoZone(NLD_AMSTERDAM_BBOX)


class MockLayer(Layer):
    """
    Simple mock layer that just rasterizes the zones
    """
    def get_data(self, bbox, spatial_resolution=None, resampling_method=None):
        arr = make_geocube(
            vector_data=IDN_JAKARTA_TILED_BBOXES,
            measurements=['index'],
            resolution=(0.001, 0.001),
            output_crs=WGS_EPSG_CODE,
        ).index
        return arr


class MockMaskLayer(Layer):
    """
    Simple layer where even indices are masked
    """
    def get_data(self, bbox, spatial_resolution=None, resampling_method=None):
        tile_side_length = 0.01
        mask_gdf = create_fishnet_gdf_for_testing(bbox.bounds, tile_side_length).reset_index()
        mask_gdf['index'] = mask_gdf['index'] % 2
        mask = make_geocube(
            vector_data=mask_gdf,
            measurements=['index'],
            resolution=(0.001, 0.001),
            output_crs=WGS_EPSG_CODE,
        ).index

        mask = mask.where(mask != 0)
        return mask


class MockGroupByLayer(Layer):
    """
    Simple categorical layer with alternating 1s and 2s
    """
    def get_data(self, bbox, spatial_resolution=None, resampling_method=None):
        tile_side_length = 0.001
        group_by_gdf = create_fishnet_gdf_for_testing(bbox.bounds, tile_side_length).reset_index()
        group_by_gdf['index'] = (group_by_gdf['index'] % 2) + 1
        group_by = make_geocube(
            vector_data=group_by_gdf,
            measurements=['index'],
            resolution=(0.001, 0.001),
            output_crs=WGS_EPSG_CODE,
        ).index

        return group_by


class MockLargeLayer(Layer):
    """
    Simple mock layer that just rasterizes the zones
    """
    def get_data(self, bbox, spatial_resolution=None, resampling_method=None):
        arr = make_geocube(
            vector_data=IDN_JAKARTA_TILED_LARGE_BBOXES,
            measurements=['index'],
            resolution=(0.01, 0.01),
            output_crs=WGS_EPSG_CODE,
        ).index
        return arr


class MockLargeGroupByLayer(Layer):
    """
    Large categorical layer with alternating 1s and 2s
    """

    def get_data(self, bbox, spatial_resolution=None, resampling_method=None):
        tile_side_length =  0.01
        group_by_gdf = create_fishnet_gdf_for_testing(bbox.bounds, tile_side_length).reset_index()
        group_by_gdf['index'] = (group_by_gdf['index'] % 2) + 1
        group_by = make_geocube(
            vector_data=group_by_gdf,
            measurements=['index'],
            resolution=(0.01, 0.01),
            output_crs=WGS_EPSG_CODE,
        ).index

        return group_by
