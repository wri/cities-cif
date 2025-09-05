import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import WorldPop, OpenStreetMap, OpenStreetMapClass
from city_metrix.metrix_model import Metric
from city_metrix.metrics import GeoZone

DEFAULT_SPATIAL_RESOLUTION = 100


class RecreationalSpacePerThousand__HectaresPerThousandPersons(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution=DEFAULT_SPATIAL_RESOLUTION
                   ) -> Union[pd.DataFrame | pd.Series]:
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        world_pop = WorldPop()
        open_space = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE)

        # per 1000 people
        world_pop_sum = world_pop.groupby(geo_zone, spatial_resolution).sum() / 1000
        # convert square meter to hectare
        open_space_counts = open_space.mask(world_pop).groupby(geo_zone, spatial_resolution).count()
        open_space_area = open_space_counts.fillna(0) * spatial_resolution ** 2 / 10000

        if isinstance(open_space_area, pd.DataFrame):
            result = open_space_area.copy()
            result['value'] = open_space_area['value'] / world_pop_sum['value']
        else:
            result = open_space_area / world_pop_sum

        return result
