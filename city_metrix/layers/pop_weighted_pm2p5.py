from city_metrix.metrix_model import Layer, GeoExtent
from city_metrix.metrix_dao import retrieve_cached_city_data
from .world_pop import WorldPop
from .acag_pm2p5 import AcagPM2p5
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 1113.1949

class PopWeightedPM2p5(Layer):
    GEOSPATIAL_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["worldpop_agesex_classes"]
    MINOR_NAMING_ATTS = ["worldpop_year", "acag_year", "acag_return_above"]

    """
    Attributes:
        worldpop_agesex_classes:Enum value from WorldPopClass OR
                                list of age-sex classes to retrieve (see https://airtable.com/appDWCVIQlVnLLaW2/tblYpXsxxuaOk3PaZ/viwExxAgTQKZnRfWU/recFjH7WngjltFMGi?blocks=hide)
        worldpop_year: year used for data retrieval
        acag_year: only available year is 2022
        acag_return_above:
    """
    # get_data() for this class returns DataArray with pm2.5 concentration multiplied by (pixelpop/meanpop)
    def __init__(self, worldpop_agesex_classes=[], worldpop_year=2020, acag_year=2022, acag_return_above=0, **kwargs):
        super().__init__(**kwargs)
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.worldpop_year = worldpop_year
        self.acag_year = acag_year
        self.acag_return_above = acag_return_above

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data = retrieve_cached_city_data(self, bbox, allow_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        world_pop = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year).get_data(bbox, spatial_resolution=spatial_resolution)
        pm2p5 = AcagPM2p5(year=self.acag_year, return_above=self.acag_return_above).get_data(bbox, spatial_resolution=spatial_resolution)

        utm_crs = bbox.as_utm_bbox().crs

        data = pm2p5 * (world_pop / world_pop.mean()).rio.write_crs(utm_crs)

        return data
