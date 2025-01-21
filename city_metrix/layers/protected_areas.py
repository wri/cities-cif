import ee
import geopandas as gpd
import geemap
from .layer import Layer


class ProtectedAreas(Layer):
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

    def get_data(self, bbox):
        dataset = ee.FeatureCollection('WCMC/WDPA/current/polygons')
        dataset = dataset.filter(ee.Filter.inList('STATUS', self.status)).filter(ee.Filter.lessThanOrEquals('STATUS_YR', self.status_year)).filter(ee.Filter.inList('IUCN_CAT', self.iucn_cat))
        dataset = dataset.filterBounds(ee.Geometry.BBox(*bbox))
        data_gdf = geemap.ee_to_gdf(dataset)
        data_gdf  = data_gdf.clip(bbox).reset_index()
        return gpd.GeoDataFrame({'protected': 1, 'geometry': data_gdf.geometry}).set_crs('EPSG:4326')
