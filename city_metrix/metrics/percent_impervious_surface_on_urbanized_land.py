from geopandas import GeoSeries

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import GeoZone, Metric
from city_metrix.layers import UrbanExtents, ImperviousSurface, WorldPop


DEFAULT_SPATIAL_RESOLUTION = 100

# TODO: layer generation and zonal stats use different spatial resolutions

class PercentImperviousSurfaceOnUrbanizedLand(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution=DEFAULT_SPATIAL_RESOLUTION) -> GeoSeries:
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        impervious_layer = ImperviousSurface()
        urban_layer = UrbanExtents()
        area_layer = WorldPop()

        return 100 * area_layer.mask(urban_layer).mask(impervious_layer).groupby(geo_zone).count() / area_layer.mask(urban_layer).groupby(geo_zone).count()
