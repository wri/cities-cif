import ee
import geemap
import geopandas as gpd

from city_metrix.metrix_model import Layer, GeoExtent
from ..constants import GEOJSON_FILE_EXTENSION


class UrbanExtents(Layer):
    OUTPUT_FILE_FORMAT = GEOJSON_FILE_EXTENSION
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
                 force_data_refresh=False):

        ue_fc = ee.FeatureCollection(f'projects/wri-datalab/cities/urban_land_use/data/global_cities_Aug2024/urbanextents_unions_{self.year}')

        bbox_utm = bbox.as_utm_bbox()
        if hasattr(bbox, "latitude") and hasattr(bbox, "longitude"):
            ee_centroid = ee.Geometry.Point([bbox.longitude, bbox.latitude])
        else:
            ee_centroid = ee.Geometry.Point([bbox.centroid.x, bbox.centroid.y])
        urbexts = ue_fc.filterBounds(ee_centroid)

        columns_to_join = ['city_id_large', 'city_ids', 'city_name_large',
                           'city_names', 'country_name', 'reference_idstring']

        if urbexts.size().getInfo() == 0:
            urbexts_dissolved = gpd.GeoDataFrame(columns=columns_to_join+['geometry'], geometry='geometry')
            urbexts_dissolved.set_crs(bbox_utm.crs, inplace=True)
        else:
            urbexts_gdf = geemap.ee_to_gdf(urbexts)
            urbexts_dissolved = urbexts_gdf.dissolve()
            for col in columns_to_join:
                urbexts_dissolved[col] = ['+'.join(map(str, urbexts_gdf[col]))]

            urbexts_dissolved = urbexts_dissolved.to_crs(bbox_utm.crs)

        data = urbexts_dissolved
        data['geo_level'] = 'urban_extent'
        if bbox.city_id:
            data['geo_id'] = f'{bbox.city_id}_urban_extent'
            data['geo_name'] = f"{bbox.city_id} - Urban Extent"
            data['geo_parent_name'] = bbox.city_id
        else:
            data['geo_id'] = None
            data['geo_name'] = None
            data['geo_parent_name'] = None

        return data
