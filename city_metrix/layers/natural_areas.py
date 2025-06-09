from xrspatial.classify import reclassify

from city_metrix.metrix_model import Layer, GeoExtent
from .esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from ..constants import GTIFF_FILE_EXTENSION, DEFAULT_PRODUCTION_ENV

DEFAULT_SPATIAL_RESOLUTION = 10

class NaturalAreas(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        esa_world_cover = EsaWorldCover().get_data_with_caching(bbox=bbox, s3_env=DEFAULT_PRODUCTION_ENV, spatial_resolution=spatial_resolution)
        reclass_map = {
            EsaWorldCoverClass.TREE_COVER.value: 1,
            EsaWorldCoverClass.SHRUBLAND.value: 1,
            EsaWorldCoverClass.GRASSLAND.value: 1,
            EsaWorldCoverClass.CROPLAND.value: 0,
            EsaWorldCoverClass.BUILT_UP.value: 0,
            EsaWorldCoverClass.BARE_OR_SPARSE_VEGETATION.value: 0,
            EsaWorldCoverClass.SNOW_AND_ICE.value: 0,
            EsaWorldCoverClass.PERMANENT_WATER_BODIES.value: 0,
            EsaWorldCoverClass.HERBACEOUS_WET_LAND.value: 1,
            EsaWorldCoverClass.MANGROVES.value: 1,
            EsaWorldCoverClass.MOSS_AND_LICHEN.value: 1
            # Add other mappings as needed
        }

        # Perform the reclassification
        reclassified_data = reclassify(
            esa_world_cover,
            bins=list(reclass_map.keys()),
            new_values=list(reclass_map.values())
        )

        # Apply the original CRS (Coordinate Reference System)
        reclassified_data = reclassified_data.rio.write_crs(esa_world_cover.rio.crs, inplace=True)

        return reclassified_data
