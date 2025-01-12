from geopandas import GeoDataFrame, GeoSeries
import xarray as xr
import numpy as np
from city_metrix.layers import CanopyCoverageByPercentage, WorldPop, UrbanLandUse
from city_metrix.layers.layer import get_utm_zone_epsg


def canopy_covered_population(zones: GeoDataFrame, agesex_classes=[], percentage=33, height=5) -> GeoSeries:
    class CoveredTemp(CanopyCoverageByPercentage):
        def get_data(self, bbox) -> xr.DataArray:
            data = super().get_data(bbox)
            result = xr.where(data==1, data, np.nan).rio.write_crs(data.crs)
            result = result.assign_attrs(**data.attrs)
            return result
    pop_layer = WorldPop()
    coverage_layer = CoveredTemp(percentage=percentage, height=height, reduce_resolution=True)
    access_pop = pop_layer.mask(coverage_layer).groupby(zones).sum()
    total_pop = pop_layer.groupby(zones).sum()
    return GeoDataFrame({'access_popfraction': 100 * access_pop / total_pop, 'geometry': zones['geometry']}).fillna(-9999)

def canopy_covered_population_elderly(zones: GeoDataFrame, percentage=33, height=5) -> GeoSeries:
    return canopy_covered_population(zones, agesex_classes=['F_60', 'F_65', 'F_70', 'F_75', 'F_80', 'M_60', 'M_65', 'M_70', 'M_75', 'M_80'], percentage=33, height=5)

def canopy_covered_population_children(zones: GeoDataFrame, percentage=33, height=5) -> GeoSeries:
    return canopy_covered_population(zones, agesex_classes=['F_0', 'F_1', 'F_5', 'F_10', 'M_0', 'M_1', 'M_5', 'M_10'], percentage=33, height=5)

def canopy_covered_population_female(zones: GeoDataFrame, percentage=33, height=5) -> GeoSeries:
    return canopy_covered_population(zones, agesex_classes=['F_0', 'F_1', 'F_5', 'F_10', 'F_15', 'F_20', 'F_25', 'F_30', 'F_35', 'F_40', 'F_45', 'F_50', 'F_55', 'F_60', 'F_65', 'F_70', 'F_75', 'F_80'], percentage=33, height=5)

'''
def canopy_covered_population_informal(zones: GeoDataFrame, percentage=33, height=5) -> GeoSeries:
    class CoveredTemp(CanopyCoverageByPercentage):
        def get_data(self, bbox) -> xr.DataArray:
            data = super().get_data(bbox)
            result = xr.where(data==1, data, np.nan).rio.write_crs(data.crs)
            result = result.assign_attrs(**data.attrs)
            return result
    class InformalTemp(UrbanLandUse):
        def get_data(self, bbox):
            data = super().get_data(bbox)
            result = xr.where(data==3, data-2, np.nan).rio.write_crs(get_utm_zone_epsg(bbox))
            result = result.assign_attrs(**data.attrs)
            return result
    informal_layer = InformalTemp()
    pop_layer = WorldPop()
    coverage_layer = CoveredTemp(percentage=percentage, height=height, reduce_resolution=True)
    access_pop = pop_layer.mask(informal_layer).mask(coverage_layer).groupby(zones).sum()
    total_pop = pop_layer.groupby(zones).sum()
    return GeoDataFrame({'access_popfraction': 100 * access_pop / total_pop, 'geometry': zones['geometry']}).fillna(-9999)
'''
