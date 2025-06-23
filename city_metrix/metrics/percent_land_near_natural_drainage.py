from geopandas import GeoSeries

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import HeightAboveNearestDrainage
from city_metrix.metrix_model import GeoZone, Metric

DEFAULT_SPATIAL_RESOLUTION = 30

class PercentLandNearNaturalDrainage(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = DEFAULT_SPATIAL_RESOLUTION) -> GeoSeries:

        neardrainage_area = HeightAboveNearestDrainage(thresh=1, nanval=None).groupby(geo_zone).count()
        total_area = HeightAboveNearestDrainage(nanval=0).groupby(geo_zone).count()

        return 100 * neardrainage_area / total_area
