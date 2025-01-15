from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee
from enum import Enum

from .layer import Layer, get_utm_zone_epsg, get_image_collection


class WorldPopClass(Enum):
    ELDERLY = ['F_60', 'F_65', 'F_70', 'F_75', 'F_80',
               'M_60', 'M_65', 'M_70', 'M_75', 'M_80']
    CHILDREN = ['F_0', 'F_1', 'F_5', 'F_10', 'M_0', 'M_1', 'M_5', 'M_10']
    FEMALE = ['F_0', 'F_1', 'F_5', 'F_10', 'F_15', 'F_20', 'F_25', 'F_30', 'F_35',
              'F_40', 'F_45', 'F_50', 'F_55', 'F_60', 'F_65', 'F_70', 'F_75', 'F_80']


class WorldPop(Layer):
    """
    Attributes:
        agesex_classes: Enum value from WorldPopClass OR
                        list of age-sex classes to retrieve (see https://airtable.com/appDWCVIQlVnLLaW2/tblYpXsxxuaOk3PaZ/viwExxAgTQKZnRfWU/recFjH7WngjltFMGi?blocks=hide)
        year: year used for data retrieval
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, agesex_classes=[], year=2020, spatial_resolution=100, **kwargs):
        super().__init__(**kwargs)
        # agesex_classes options:
        # M_0, M_1, M_5, M_10, M_15, M_20, M_25, M_30, M_35, M_40, M_45, M_50, M_55, M_60, M_65, M_70, M_75, M_80
        # F_0, F_1, F_5, F_10, F_15, F_20, F_25, F_30, F_35, F_40, F_45, F_50, F_55, F_60, F_65, F_70, F_75, F_80
        self.agesex_classes = agesex_classes
        self.year = year
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        if not self.agesex_classes:
            # total population
            dataset = ee.ImageCollection('WorldPop/GP/100m/pop')

            world_pop_ic = ee.ImageCollection(
                dataset
                .filterBounds(ee.Geometry.BBox(*bbox))
                .filter(ee.Filter.inList('year', [self.year]))
                .select('population')
                .mean()
            )

            data = get_image_collection(
                world_pop_ic,
                bbox,
                self.spatial_resolution,
                "world pop"
            ).population

        else:
            # sum population for selected age-sex groups
            world_pop_age_sex = ee.ImageCollection('WorldPop/GP/100m/pop_age_sex')

            if isinstance(self.agesex_classes, WorldPopClass):
                agesex_value = self.agesex_classes.value
            else:
                agesex_value = self.agesex_classes
            
            world_pop_age_sex_year = (world_pop_age_sex
                                      .filterBounds(ee.Geometry.BBox(*bbox))
                                      .filter(ee.Filter.inList('year', [self.year]))
                                      .select(agesex_value)
                                      .mean()
                                      )

            world_pop_group_ic = ee.ImageCollection(
                world_pop_age_sex_year
                .reduce(ee.Reducer.sum())
                .rename('sum_age_sex_group')
            )

            data = get_image_collection(
                world_pop_group_ic,
                bbox,
                self.spatial_resolution,
                "world pop age sex"
            ).sum_age_sex_group

        return data
