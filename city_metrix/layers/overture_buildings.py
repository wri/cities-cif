import geopandas as gpd
import subprocess
from io import StringIO

from city_metrix.metrix_model import Layer, GeoExtent
from ..constants import GEOJSON_FILE_EXTENSION, GeoType
from ..metrix_dao import write_layer
from ..repo_manager import retrieve_cached_city_data2


class OvertureBuildings(Layer):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 force_data_refresh=False):
        #Note: spatial_resolution and resampling_method arguments are ignored.

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data, file_uri = retrieve_cached_city_data2(self, bbox, force_data_refresh)
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

        if bbox.geo_type == GeoType.CITY:
            write_layer(overture_buildings, file_uri, self.GEOSPATIAL_FILE_FORMAT)

        return overture_buildings
