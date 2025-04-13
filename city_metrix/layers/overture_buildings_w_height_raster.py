from geocube.api.core import make_geocube
from shapely.geometry import mapping

from .layer import Layer
from .layer_geometry import GeoExtent
from ..constants import GTIFF_FILE_EXTENSION
from .overture_buildings_w_height import OvertureBuildingsHeight
from ..metrix_dao import retrieve_cached_city_data

DEFAULT_SPATIAL_RESOLUTION = 1


class OvertureBuildingsHeightRaster(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_LAYER_NAMING_ATTS = ["city"]
    MINOR_LAYER_NAMING_ATTS = None

    """
    Attributes:
        city: city id from https://sat-io.earthengine.app/view/ut-globus
    """

    def __init__(self, city="", **kwargs):
        super().__init__(**kwargs)
        self.city = city

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data = retrieve_cached_city_data(self, bbox, allow_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        if self.city == "":
            raise Exception("'city' can not be empty. Check and select a city id from https://sat-io.earthengine.app/view/ut-globus")

        # Load the datasets
        overture_buildings_height = OvertureBuildingsHeight(self.city).get_data(bbox)

        # Define the bounding box
        utm_crs = bbox.as_utm_bbox().crs
        geom = {
            "type": "Feature",
            "geometry": mapping(bbox.as_utm_bbox().polygon),
            "crs": {"properties": {"name": utm_crs}},
        }

        # Rasterize the GeoDataFrame into an xarray Dataset
        cube = make_geocube(
            vector_data=overture_buildings_height,
            measurements=["height"],
            output_crs=utm_crs,
            resolution=(spatial_resolution, spatial_resolution),
            geom=geom,
            fill=-999,
        )

        # Extract the DataArray for the 'height' measurement
        data = cube["height"]

        return data
