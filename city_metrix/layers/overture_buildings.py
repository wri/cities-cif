import geopandas as gpd
import subprocess
from io import StringIO

from .layer import Layer
from .layer_geometry import LayerBbox


class OvertureBuildings(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: LayerBbox, spatial_resolution=None, resampling_method=None):
        #Note: spatial_resolution and resampling_method arguments are ignored.

        if bbox.units == "degrees":
            utm_bbox = bbox.as_utm_bbox()
            utm_crs = utm_bbox.crs
            bbox_str = ','.join(map(str, bbox.bbox))
        else:
            utm_crs = bbox.crs
            wgs_bbox = bbox.as_lat_lon_bbox()
            bbox_str = ','.join(map(str, wgs_bbox.bbox))

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
            overture_buildings = overture_buildings.to_crs(utm_crs)
        else:
            print("Error occurred:", result.stderr)

        return overture_buildings
