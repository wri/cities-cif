import geopandas as gpd
import subprocess
from io import StringIO

from .layer import Layer
from .layer_geometry import GeoExtent, retrieve_cached_city_data
from .layer_tools import build_s3_names


class OvertureBuildings(Layer):
    OUTPUT_FILE_FORMAT = 'geojson'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_layer_names(self):
        layer_name, layer_id, file_format = build_s3_names(self, None, None)
        return layer_name, layer_id, file_format

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 allow_s3_cache_retrieval=False):
        #Note: spatial_resolution and resampling_method arguments are ignored.

        layer_name, layer_id, file_format = self.get_layer_names()
        retrieved_cached_data = retrieve_cached_city_data(bbox, layer_name, layer_id, file_format, allow_s3_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        geographic_box = bbox.as_geographic_bbox()
        geographic_bbox_str = ','.join(map(str, geographic_box.bounds))

        command = [
            "overturemaps", "download",
            "--bbox="+geographic_bbox_str,
            "-f", "geojson",
            "--type=building"
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            geojson_data = result.stdout
            overture_buildings = gpd.read_file(StringIO(geojson_data))

            utm_crs = bbox.as_utm_bbox().crs
            overture_buildings = overture_buildings.to_crs(utm_crs)
        else:
            print("Error occurred:", result.stderr)

        return overture_buildings
