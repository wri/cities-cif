from geopandas import GeoDataFrame
from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GEOJSON_FILE_EXTENSION

AWS_STEM = 'https://wri-cities-indicators.s3.us-east-1.amazonaws.com'
S3_KBA_PREFIX = 'devdata/inputdata/KBA'

class KeyBiodiversityAreas(Layer):
    OUTPUT_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ['country_code_iso3']
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        SitRecID: ID num at BirdLife International
    """

    def __init__(self, country_code_iso3=None, **kwargs):
        super().__init__(**kwargs)
        self.country_code_iso3 = country_code_iso3

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 force_data_refresh=False):
        if self.country_code_iso3 is not None:
            country_code = self.country_code_iso3
        else:
            country_code = 'global'

        utm_crs = bbox.as_utm_bbox().crs

        country_data = GeoDataFrame.from_file(f'{AWS_STEM}/{S3_KBA_PREFIX}/KBA_{country_code}.geojson')
        city_data = country_data.loc[country_data.intersects(bbox.as_geographic_bbox().polygon)]

        if len(city_data) > 0:
            dissolved_data = city_data.dissolve()
            data = GeoDataFrame({'id': [0], 'is_kba': 1, 'geometry': dissolved_data.geometry}).to_crs(utm_crs)
        else:  # No KBAs intersect with boundary -- return point to avoid empty gdf
            data = GeoDataFrame({'id': [0], 'is_kba': 1, 'geometry': [bbox.centroid]}).set_crs(bbox.crs).to_crs(utm_crs)
        
        return data
