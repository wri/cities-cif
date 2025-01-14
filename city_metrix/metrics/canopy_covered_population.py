from geopandas import GeoDataFrame, GeoSeries
import xarray as xr
import numpy as np
import ee
from city_metrix.layers import Layer, WorldPop, UrbanLandUse
from city_metrix.layers.layer import get_image_collection


def canopy_covered_population(zones: GeoDataFrame, agesex_classes=[], percentage=30, height=5, informal_only=False) -> GeoSeries:
    class CoveredMask(Layer):
        def get_data(self, bbox):
            canopy_ht_ic = ee.ImageCollection("projects/meta-forest-monitoring-okw37/assets/CanopyHeight")
            region = ee.Geometry.BBox(*bbox)
            pop_ic = ee.ImageCollection("WorldPop/GP/100m/pop").filterBounds(region)
            covered_img = canopy_ht_ic.filterBounds(region).mosaic().gte(height).multiply(1).setDefaultProjection(pop_ic.first().projection())
            covered_reprojected_img = covered_img.reduceResolution(ee.Reducer.mean(), True, 65536)
            thirtypct_covered_img = covered_reprojected_img.gte(percentage/100).multiply(1).rename('thirtypercent_covered')
            data = get_image_collection(
                ee.ImageCollection(thirtypct_covered_img),
                bbox,
                thirtypct_covered_img.projection().nominalScale().getInfo(),
                "canopy cover"
            ).thirtypercent_covered
            result = xr.where(data==1, data, np.nan).rio.write_crs(data.crs)
            result = result.assign_attrs(**data.attrs)
            return result
    class InformalMask(UrbanLandUse):
        def get_data(self, bbox):
            data = super().get_data(bbox)
            result = xr.where(data==3, 1, np.nan).rio.write_crs(data.crs)
            result = result.assign_attrs(**data.attrs)
            return result

    coverage_mask = CoveredMask()
    if informal_only:
        informal_mask = InformalMask()
        pop_layer = WorldPop(agesex_classes=agesex_classes, masks=[informal_mask, coverage_mask])
    else:
        pop_layer = WorldPop(agesex_classes=agesex_classes, masks=[coverage_mask,])
    access_pop = pop_layer.groupby(zones).sum()
    total_pop = WorldPop(agesex_classes=agesex_classes).groupby(zones).sum()
    return GeoDataFrame({'access_popfraction': 100 * access_pop / total_pop, 'geometry': zones['geometry']}).fillna(0)

def canopy_covered_population_elderly(zones: GeoDataFrame, percentage=30, height=5) -> GeoSeries:
    return canopy_covered_population(zones, agesex_classes=['F_60', 'F_65', 'F_70', 'F_75', 'F_80', 'M_60', 'M_65', 'M_70', 'M_75', 'M_80'], percentage=percentage, height=height, informal_only=False)

def canopy_covered_population_children(zones: GeoDataFrame, percentage=30, height=5) -> GeoSeries:
    return canopy_covered_population(zones, agesex_classes=['F_0', 'F_1', 'F_5', 'F_10', 'M_0', 'M_1', 'M_5', 'M_10'], percentage=percentage, height=height, informal_only=False)

def canopy_covered_population_female(zones: GeoDataFrame, percentage=30, height=5) -> GeoSeries:
    return canopy_covered_population(zones, agesex_classes=['F_0', 'F_1', 'F_5', 'F_10', 'F_15', 'F_20', 'F_25', 'F_30', 'F_35', 'F_40', 'F_45', 'F_50', 'F_55', 'F_60', 'F_65', 'F_70', 'F_75', 'F_80'], percentage=percentage, height=height, informal_only=False)

def canopy_covered_population_informal(zones: GeoDataFrame, percentage=30, height=5) -> GeoSeries:
    return canopy_covered_population(zones, agesex_classes=[], percentage=percentage, height=height, informal_only=True)
