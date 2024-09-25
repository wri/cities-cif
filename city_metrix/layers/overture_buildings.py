import geopandas as gpd
import subprocess
from io import StringIO

from .layer import Layer, get_utm_zone_epsg


class OvertureBuildings(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox):
        bbox_str = ','.join(map(str, bbox))

        command = [
            "overturemaps", "download",
            "--bbox="+bbox_str,
            "-f", "geojson",
            "--type=building"
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            geojson_data = result.stdout
            overture_buildings = gpd.read_file(StringIO(geojson_data))
            crs = get_utm_zone_epsg(bbox)
            overture_buildings = overture_buildings.to_crs(crs)
        else:
            print("Error occurred:", result.stderr)

        return overture_buildings
