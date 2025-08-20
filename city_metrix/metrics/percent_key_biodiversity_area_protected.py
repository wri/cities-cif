import pandas as pd
from typing import Union
import geopandas as gpd
from city_metrix.constants import CSV_FILE_EXTENSION, WGS_CRS
from city_metrix.metrix_model import Metric, GeoZone
from city_metrix.layers import (
    KeyBiodiversityAreas,
    ProtectedAreas,
    WorldPop
)

AWS_STEM = 'https://wri-cities-indicators.s3.us-east-1.amazonaws.com'
COUNTRYBBOXES_PATH = 'devdata/inputdata/country_bboxes.geojson'
COUNTRYBOUNDS_PATH = 'devdata/inputdata/country_boundaries.geojson'


class KeyBiodiversityAreaProtected__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(
        self, country_code_iso3=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.country_code_iso3 = country_code_iso3

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:

        def _to_geographic(poly, source_crs):
            gdf = gpd.GeoDataFrame({'id':[0], 'geometry':poly}).set_crs(source_crs).to_crs(WGS_CRS)
            return gdf.geometry[0]

        if self.country_code_iso3 is None:
            country_bboxes = gpd.GeoDataFrame.from_file(f'{AWS_STEM}/{COUNTRYBBOXES_PATH}')
            geo_polygon = _to_geographic(geo_zone.polygon, geo_zone.crs)
            matches = country_bboxes.loc[country_bboxes.intersects(geo_polygon)]
            if len(matches) > 1:
                country_bounds = gpd.GeoDataFrame.from_file(f'{AWS_STEM}/{COUNTRYBOUNDS_PATH}')
                matches = country_bounds.loc[country_bounds.intersects(geo_polygon)]
            country_code_iso3 = matches.countrycode[matches.index[0]]
        else:
            country_code_iso3 = self.country_code_iso3

        worldpop_layer = WorldPop()
        kba_layer = KeyBiodiversityAreas(country_code_iso3)
        protected_layer = ProtectedAreas()

        kba_area = worldpop_layer.mask(kba_layer).groupby(geo_zone).count()
        protected_kba_area = worldpop_layer.mask(kba_layer).mask(protected_layer).groupby(geo_zone).count()

        fraction_protected = protected_kba_area / kba_area

        if isinstance(fraction_protected, pd.DataFrame):
            result = fraction_protected.copy()
            result['value'] = fraction_protected['value'] * 100
        else:
            result = fraction_protected * 100

        return result