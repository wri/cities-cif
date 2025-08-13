import numpy as np
import pandas as pd
import geopandas as gpd
from pandas import Series
from geocube.api.core import make_geocube
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import LandCoverSimplifiedGlad, LandCoverHabitatChangeGlad
from city_metrix.metrix_model import GeoExtent, GeoZone, Metric


START_YEAR = 2000
END_YEAR = 2020

def _rasterize(gdf, snap_to):
    if gdf.empty:
        nan_array = np.full(snap_to.shape, np.nan, dtype=float)
        raster = snap_to.copy(data=nan_array)
    else:
        raster = make_geocube(
            vector_data=gdf,
            measurements=["index"],
            like=snap_to,
        ).index

    return raster.rio.reproject_match(snap_to)

class HabitatTypesRestored__CoverTypes(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> pd.DataFrame:

        results = []

        # Count unique cover types in each zone, only within pixels classed 01 in change raster
        for rownum in range(len(geo_zone.zones)):
            zone = geo_zone.zones.iloc[[rownum]]
            cover_array = LandCoverSimplifiedGlad(year=END_YEAR).get_data(GeoExtent(zone))
            restored_array = LandCoverHabitatChangeGlad(start_year=START_YEAR, end_year=END_YEAR).get_data(GeoExtent(zone))
            zone_array = _rasterize(zone, cover_array)
            restored_cover_inzone = restored_array.where(restored_array==1) * cover_array * (zone_array + 1)
            results.append(len([i for i in np.unique(restored_cover_inzone) if not np.isnan(i)]))

        result_df = geo_zone.zones.copy()
        result_df['value'] = results
        result_df['zone'] = result_df['id']
        return result_df[['zone', 'value']]
