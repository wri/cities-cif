import ee
import geopandas as gpd
import geemap

from city_metrix.metrix_model import Layer, GeoExtent
from ..constants import GEOJSON_FILE_EXTENSION


class ProtectedAreas(Layer):
    OUTPUT_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["status_year", "status", "iucn_cat"]

    """
    Attributes:
        status: Proposed, Inscribed, Adopted, Designated, or Established 
        status_year: integer, year when status was set
        iucn_cat: IUCN management category, one of: Ia (strict nature reserve), Ib (wilderness area), II (national park), III (natural monument or feature), IV (habitat/species management area), V (protected landscape/seascape), VI (PA with sustainable use of natural resources), Not Applicable, Not Assigned, or Not Reported.
    """
    def __init__(self, status=['Inscribed', 'Adopted', 'Designated', 'Established'], status_year=2024, iucn_cat=['Ia', 'Ib', 'II', 'III', 'IV', 'V', 'VI', 'Not Applicable', 'Not Assigned', 'Not Reported'], **kwargs):
        super().__init__(**kwargs)
        self.status = status
        self.status_year = status_year
        self.iucn_cat = iucn_cat

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 force_data_refresh=False):

        dataset = ee.FeatureCollection('WCMC/WDPA/current/polygons')
        dataset = dataset.filter(ee.Filter.inList('STATUS', self.status)).filter(ee.Filter.lessThanOrEquals('STATUS_YR', self.status_year)).filter(ee.Filter.inList('IUCN_CAT', self.iucn_cat))

        ee_rectangle = bbox.to_ee_rectangle()
        utm_crs = ee_rectangle['crs']

        dataset = dataset.filterBounds(ee_rectangle['ee_geometry'])
        if dataset.size().getInfo() == 0:
            data = gpd.GeoDataFrame({'protected': [], 'geometry': []}).set_crs(utm_crs)

        else:
            data_gdf = geemap.ee_to_gdf(dataset)
            wgs_bbox = bbox.as_geographic_bbox().bounds
            data_gdf = data_gdf.clip(wgs_bbox).reset_index()

            data = gpd.GeoDataFrame({'protected': 1, 'geometry': data_gdf.geometry}).to_crs(utm_crs)

        return data
