from geopandas import GeoDataFrame, GeoSeries
import xarray as xr
import numpy as np
from city_metrix.layers import TreeCanopyHeight, WorldPop, UrbanLandUse


def canopy_area_per_resident(zones: GeoDataFrame, agesex_classes=[], height=5, informal_only=False) -> GeoSeries:
    class CanopyTemp(TreeCanopyHeight):
        def get_data(self, bbox):
            data = super().get_data(bbox)
            result = xr.where(data >= height, 1, 0).rio.write_crs(data.crs)
            result = result.assign_attrs(**data.attrs)
            return result
    class InformalTemp(UrbanLandUse):
        def get_data(self, bbox):
            data = super().get_data(bbox)
            result = xr.where(data==3, 1, np.nan).rio.write_crs(data.crs)
            result = result.assign_attrs(**data.attrs)
            return result

    results = []
    for rownum in range(len(zones)):  # Row by row because of memory issues
        onezone = zones.iloc[[rownum]].reset_index()
        canopy_layer = CanopyTemp()
        canopy_area = canopy_layer.groupby(onezone).sum().fillna(0)[0]

        if informal_only:
            informal_layer = InformalTemp()
            pop_layer = WorldPop(agesex_classes=agesex_classes, masks=[informal_layer,])
        else:
            pop_layer = WorldPop(agesex_classes=agesex_classes)
        total_pop = pop_layer.groupby(onezone).sum()[0]

        results.append(canopy_area / total_pop)
    return GeoDataFrame({'canopyarea_per_resident_squaremeter': results, 'geometry': zones['geometry']})

def canopy_area_per_resident_elderly(zones: GeoDataFrame, height=5) -> GeoSeries:
    return canopy_area_per_resident(zones, agesex_classes=['F_60', 'F_65', 'F_70', 'F_75', 'F_80', 'M_60', 'M_65', 'M_70', 'M_75', 'M_80'], height=5, informal_only=False)

def canopy_area_per_resident_children(zones: GeoDataFrame, height=5) -> GeoSeries:
    return canopy_area_per_resident(zones, agesex_classes=['F_0', 'F_1', 'F_5', 'F_10', 'M_0', 'M_1', 'M_5', 'M_10'], height=5, informal_only=False)

def canopy_area_per_resident_female(zones: GeoDataFrame, height=5) -> GeoSeries:
    return canopy_area_per_resident(zones, agesex_classes=['F_0', 'F_1', 'F_5', 'F_10', 'F_15', 'F_20', 'F_25', 'F_30', 'F_35', 'F_40', 'F_45', 'F_50', 'F_55', 'F_60', 'F_65', 'F_70', 'F_75', 'F_80'], height=5, informal_only=False)

def canopy_area_per_resident_informal(zones: GeoDataFrame, height=5) -> GeoSeries:
        return canopy_area_per_resident(zones, agesex_classes=[], height=5, informal_only=True)
