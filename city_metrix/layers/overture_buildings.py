import geopandas as gpd
import subprocess
from io import StringIO

from city_metrix.metrix_model import Layer, GeoExtent
from ..constants import GEOJSON_FILE_EXTENSION


class OvertureBuildings(Layer):
    OUTPUT_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 force_data_refresh=False):
        #Note: spatial_resolution and resampling_method arguments are ignored.

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
