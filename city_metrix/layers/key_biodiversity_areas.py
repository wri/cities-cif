from geopandas import GeoDataFrame
from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GEOJSON_FILE_EXTENSION

AWS_STEM = 'https://wri-cities-indicators.s3.us-east-1.amazonaws.com'
COUNTRYBBOXES_PATH = 'devdata/inputdata/country_bboxes.geojson'
COUNTRYBOUNDS_PATH = 'devdata/inputdata/country_boundaries.geojson'
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
            country_bboxes = GeoDataFrame.from_file(f'{AWS_STEM}/{COUNTRYBBOXES_PATH}')
            matches = country_bboxes.loc[country_bboxes.intersects(bbox.as_geographic_bbox().polygon)]
            if len(matches > 1):
                country_bounds = GeoDataFrame.from_file(f'{AWS_STEM}/{COUNTRYBOUNDS_PATH}')
                matches = country_bounds.loc[country_bounds.intersects(bbox.as_geographic_bbox().polygon)]
            country_code_iso3 = matches.countrycode[matches.index[0]]

        utm_crs = bbox.as_utm_bbox().crs

        country_kba_data = GeoDataFrame.from_file(f'{AWS_STEM}/{S3_KBA_PREFIX}/KBA_{country_code}.geojson')
        city_kba_data = country_kba_data.loc[country_kba_data.intersects(bbox.as_geographic_bbox().polygon)]

        if len(city_kba_data) > 0:
            dissolved_kba_data = city_kba_data.dissolve()
            data = GeoDataFrame({'id': [0], 'is_kba': 1, 'geometry': dissolved_kba_data.geometry}).to_crs(utm_crs)
        else:  # No KBAs intersect with boundary -- return point to avoid empty gdf
            data = GeoDataFrame({'id': [0], 'is_kba': 1, 'geometry': [bbox.centroid]}).set_crs(bbox.crs).to_crs(utm_crs)
        
        return data
