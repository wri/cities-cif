import pandas as pd
import numpy as np
from typing import Union
from geocube.api.core import make_geocube

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import GeoExtent, GeoZone, Metric
from city_metrix.layers import LandCoverSimplifiedGlad, LandCoverHabitatChangeGlad


class HabitatTypesRestored__CoverTypes(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["start_year", "end_year"]

    def __init__(self, start_year=2000, end_year=2020, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year
        self.unit = 'cover type'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:

        cover_array = LandCoverSimplifiedGlad(year=self.end_year).retrieve_data(GeoExtent(geo_zone))
        restored_array = LandCoverHabitatChangeGlad(start_year=self.start_year, end_year=self.end_year).get_data(GeoExtent(geo_zone))
        # Count unique cover types in each zone, only within pixels classed 01 in change raster
        cover_array_masked = cover_array.where(restored_array == 1)

        results = []
        for rownum in geo_zone.zones.index:  # Must loop over rows because cannot assume zones do not overlap. Overlaps cause overwrites when making geocube.
            geo_zone.zones['is_focal'] = geo_zone.zones.index==rownum
            
            zone_raster = make_geocube(
                vector_data=geo_zone.zones.iloc[[rownum]],
                measurements=["index"],
                like=cover_array,
            ).index

            df = pd.DataFrame({
                "zone": zone_raster.values.ravel(),
                "value": cover_array_masked.values.ravel()
            })

            # Group by zone and count unique values
            unique_counts = df.groupby("zone")["value"].nunique()
            if len(unique_counts) > 0:
                results.append(int(unique_counts[rownum]))
            else:
                results.append(np.nan)

        if geo_zone.aoi_id == 'urban_extent':
            result = pd.Series(results)
        else:
            result = pd.DataFrame({'zone': range(len(geo_zone.zones)), 'value': results})
        return result

class HabitatTypesRestored__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["start_year", "end_year"]

    def __init__(self, start_year=2000, end_year=2020, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year
        self.unit = 'percent of cover types present'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:

        cover_array = LandCoverSimplifiedGlad(year=self.end_year).retrieve_data(GeoExtent(geo_zone))
        restored_array = LandCoverHabitatChangeGlad(start_year=self.start_year, end_year=self.end_year).get_data(GeoExtent(geo_zone))
        # Count unique cover types in each zone, only within pixels classed 01 in change raster
        cover_array_masked = cover_array.where(restored_array == 1)

        results = []
        for rownum in geo_zone.zones.index:  # Must loop over rows because cannot assume zones do not overlap. Overlaps cause overwrites when making geocube.
            geo_zone.zones['is_focal'] = geo_zone.zones.index==rownum
            
            zone_raster = make_geocube(
                vector_data=geo_zone.zones.iloc[[rownum]],
                measurements=["index"],
                like=cover_array,
            ).index

            df_all = pd.DataFrame({
                "zone": zone_raster.values.ravel(),
                "value": cover_array.values.ravel()
            })

            df_masked = pd.DataFrame({
                "zone": zone_raster.values.ravel(),
                "value": cover_array_masked.values.ravel()
            })

            # Group by zone and count unique values
            unique_counts_all = df_all.groupby("zone")["value"].nunique()
            unique_counts_restored = df_masked.groupby("zone")["value"].nunique()
            if len(unique_counts_all) > 0:
                results.append(100 * unique_counts_restored[rownum] / unique_counts_all[rownum])
            else:
                results.append(np.nan)
    
        if geo_zone.aoi_id == 'urban_extent':
            result = pd.Series(results)
        else:
            result = pd.DataFrame({'zone': range(len(geo_zone.zones)), 'value': results})

        return result
