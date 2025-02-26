from geopandas import GeoDataFrame, GeoSeries
import xarray as xr
import numpy as np
import ee
from city_metrix.layers import Layer, WorldPop, WorldPopClass, UrbanLandUse
from city_metrix.layers.layer import get_image_collection


def canopy_covered_population(
    zones: GeoDataFrame,
    agesex_classes=[],
    percentage=30,
    height=3,
    ulu_class=None
) -> GeoSeries:

    class CoveredMask(Layer):
        def get_data(self, bbox, spatial_resolution:int=1, resampling_method=None):
            canopy_ht_ic = ee.ImageCollection("projects/meta-forest-monitoring-okw37/assets/CanopyHeight")
            ee_rectangle = bbox.to_ee_rectangle()
            pop_ic = ee.ImageCollection("WorldPop/GP/100m/pop").filterBounds(ee_rectangle['ee_geometry'])
            covered_img = canopy_ht_ic.filterBounds(ee_rectangle['ee_geometry']).mosaic().gte(height).multiply(1).setDefaultProjection(pop_ic.first().projection())
            covered_reprojected_img = covered_img.reduceResolution(ee.Reducer.mean(), True, 65536)
            thirtypct_covered_img = covered_reprojected_img.gte(percentage/100).multiply(1).rename('thirtypercent_covered')
            data = get_image_collection(
                ee.ImageCollection(thirtypct_covered_img),
                ee_rectangle,
                thirtypct_covered_img.projection().nominalScale().getInfo(),
                "canopy cover"
            ).thirtypercent_covered
            result = xr.where(data == 1, data, np.nan).rio.write_crs(data.crs)
            result = result.assign_attrs(**data.attrs)
            return result

    coverage_mask = CoveredMask()
    if ulu_class:
        urban_land_use = UrbanLandUse(ulu_class=ulu_class)
        pop_layer = WorldPop(agesex_classes=agesex_classes, masks=[urban_land_use, coverage_mask])
    else:
        pop_layer = WorldPop(agesex_classes=agesex_classes, masks=[coverage_mask,])
    access_pop = pop_layer.groupby(zones).sum()
    total_pop = WorldPop(agesex_classes=agesex_classes).groupby(zones).sum()
    return GeoDataFrame({'access_popfraction': 100 * access_pop / total_pop, 'geometry': zones['geometry']}).fillna(0).access_popfraction


def canopy_covered_population_elderly(zones: GeoDataFrame, percentage=30, height=3) -> GeoSeries:
    return canopy_covered_population(zones, WorldPopClass.ELDERLY, percentage, height, None)


def canopy_covered_population_children(zones: GeoDataFrame, percentage=30, height=3) -> GeoSeries:
    return canopy_covered_population(zones, WorldPopClass.CHILDREN, percentage, height, None)


def canopy_covered_population_female(zones: GeoDataFrame, percentage=30, height=3) -> GeoSeries:
    return canopy_covered_population(zones, WorldPopClass.FEMALE, percentage, height, None)


def canopy_covered_population_informal(zones: GeoDataFrame, percentage=30, height=3) -> GeoSeries:
    return canopy_covered_population(zones, [], percentage, height, 3)
