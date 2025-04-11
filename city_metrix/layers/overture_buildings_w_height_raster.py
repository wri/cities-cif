from geocube.api.core import make_geocube
from shapely.geometry import mapping

from .layer import Layer
from .layer_geometry import GeoExtent
from .overture_buildings_w_height import OvertureBuildingsHeight

DEFAULT_SPATIAL_RESOLUTION = 1


class OvertureBuildingsHeightRaster(Layer):
    def __init__(self, city="portland", **kwargs):
        super().__init__(**kwargs)
        self.city = city

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

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
