from enum import Enum

import ee

from city_metrix.metrix_model import GeoExtent, Layer, get_image_collection

from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 100

class WorldPopClass(Enum):
    ADULT = ['F_20', 'F_25', 'F_30', 'F_35', 'F_40', 'F_45', 'F_50', 'F_55', 'F_60', 'F_65', 'F_70', 'F_75', 'F_80',
            'M_20', 'M_25', 'M_30', 'M_35', 'M_40', 'M_45', 'M_50', 'M_55', 'M_60', 'M_65', 'M_70', 'M_75', 'M_80']
    ELDERLY = ['F_60', 'F_65', 'F_70', 'F_75', 'F_80',
               'M_60', 'M_65', 'M_70', 'M_75', 'M_80']
    CHILDREN = ['F_0', 'F_1', 'F_5', 'F_10', 'M_0', 'M_1', 'M_5', 'M_10']
    YOUNG_CHILDREN = ['F_0', 'F_1', 'M_0', 'M_1']
    FEMALE = ['F_0', 'F_1', 'F_5', 'F_10', 'F_15', 'F_20', 'F_25', 'F_30', 'F_35',
              'F_40', 'F_45', 'F_50', 'F_55', 'F_60', 'F_65', 'F_70', 'F_75', 'F_80']


class WorldPop(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["agesex_classes"]
    MINOR_NAMING_ATTS = ["version"]

    """
    Attributes:
        agesex_classes: Enum value from WorldPopClass OR
                        list of age-sex classes to retrieve (see https://airtable.com/appDWCVIQlVnLLaW2/tblYpXsxxuaOk3PaZ/viwExxAgTQKZnRfWU/recFjH7WngjltFMGi?blocks=hide)
        year: year used for data retrieval
    """
    def __init__(self, agesex_classes:WorldPopClass=[], version=1, year=2020, **kwargs):
        super().__init__(**kwargs)
        # agesex_classes options:
        # M_0, M_1, M_5, M_10, M_15, M_20, M_25, M_30, M_35, M_40, M_45, M_50, M_55, M_60, M_65, M_70, M_75, M_80
        # F_0, F_1, F_5, F_10, F_15, F_20, F_25, F_30, F_35, F_40, F_45, F_50, F_55, F_60, F_65, F_70, F_75, F_80
        self.agesex_classes = agesex_classes
        self.version=version
        self.year = year if version==1 else str(year)

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        # spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        spatial_resolution = self.resolution or spatial_resolution or DEFAULT_SPATIAL_RESOLUTION

        ee_rectangle = bbox.to_ee_rectangle()
        if not self.agesex_classes:
            # total population
            if self.version == 1:
                dataset = ee.ImageCollection('WorldPop/GP/100m/pop')
            elif self.version == 2:
                dataset = ee.ImageCollection('projects/sat-io/open-datasets/WORLDPOP/pop')
            else:
                raise Exception(f"WorldPop version {self.version} not supported") 

            world_pop_ic = ee.ImageCollection(
                dataset
                .filterBounds(ee_rectangle['ee_geometry'])
                .filter(ee.Filter.inList('year', [self.year]))
                .select('population')
                .mean()
            )

            data = get_image_collection(
                world_pop_ic,
                ee_rectangle,
                spatial_resolution,
                "world pop"
            ).population

        else:
            # sum population for selected age-sex groups
            if self.version == 1:
                world_pop_age_sex = ee.ImageCollection('WorldPop/GP/100m/pop_age_sex')
            elif self.version == 2:
                world_pop_age_sex = ee.ImageCollection('projects/sat-io/open-datasets/WORLDPOP/agesex')
            else:
                raise Exception(f"WorldPop version {self.version} not supported") 

            if isinstance(self.agesex_classes, WorldPopClass):
                agesex_value = self.agesex_classes.value
            else:
                agesex_value = self.agesex_classes
            
            world_pop_age_sex_year = (world_pop_age_sex
                                      .filterBounds(ee_rectangle['ee_geometry'])
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
                ee_rectangle,
                spatial_resolution,
                "world pop age sex"
            ).sum_age_sex_group

            if self.version != 1:
                # Interpolate to WorldPop v1 grid

                wp_v1_ee = ee.ImageCollection(
                    ee.ImageCollection('WorldPop/GP/100m/pop')
                    .filterBounds(ee_rectangle['ee_geometry'])
                    .filter(ee.Filter.eq('year', 2020))
                    .select('population')
                    .mean()
                )
                wp_v1_xr = get_image_collection(
                    wp_v1_ee,
                    ee_rectangle,
                    spatial_resolution,
                    "world pop grid"
                ).population
                data = data.interp_like(wp_v1_xr)

        return data
