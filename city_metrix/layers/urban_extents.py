import ee
import geemap
import geopandas as gpd

from city_metrix.metrix_model import Layer, GeoExtent
from city_metrix.metrix_dao import retrieve_cached_city_data
from ..constants import GEOJSON_FILE_EXTENSION


class UrbanExtents(Layer):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        year:
    """
    def __init__(self, year=2020, **kwargs):
        super().__init__(**kwargs)
        if not year in [1980, 1990, 2000, 2005, 2010, 2015, 2020]:
            raise Exception(f'Year {year} not available.')
        self.year = year

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 allow_cache_retrieval=False):

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data = retrieve_cached_city_data(self, bbox, allow_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        ue_fc = ee.FeatureCollection(f'projects/wri-datalab/cities/urban_land_use/data/global_cities_Aug2024/urbanextents_unions_{self.year}')

        ee_rectangle = bbox.to_ee_rectangle()
        urbexts = ue_fc.filterBounds(ee_rectangle['ee_geometry'])

        columns_to_join = ['city_id_large', 'city_ids', 'city_name_large',
                           'city_names', 'country_name', 'reference_idstring']

        if urbexts.size().getInfo() == 0:
            urbexts_dissolved = gpd.GeoDataFrame(columns=columns_to_join+['geometry'], geometry='geometry')
            urbexts_dissolved.set_crs(ee_rectangle['crs'], inplace=True)
        else:
            urbexts_gdf = geemap.ee_to_gdf(urbexts)
            urbexts_dissolved = urbexts_gdf.dissolve()
            for col in columns_to_join:
                urbexts_dissolved[col] = ['+'.join(map(str, urbexts_gdf[col]))]

            urbexts_dissolved = urbexts_dissolved.to_crs(ee_rectangle['crs'])

        return urbexts_dissolved
