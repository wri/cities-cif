import ee

from city_metrix.constants import GTIFF_FILE_EXTENSION
from city_metrix.metrix_model import Layer, GeoExtent, get_image_collection

class OpenUrban(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None
    PROCESSING_TILE_SIDE_M = 5000

    def __init__(self, band='b1', **kwargs):
        super().__init__(**kwargs)
        self.band = band

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=None, resampling_method:str=None):

        dataset = ee.ImageCollection("projects/wri-datalab/cities/OpenUrban/OpenUrban_LULC")
        ## It is important if the cif code is pulling data from GEE to take the maximum value where the image tiles overlap

        # Check for data
        data = None
        ee_rectangle = bbox.to_ee_rectangle()
        if dataset.filterBounds(ee_rectangle['ee_geometry']).size().getInfo() == 0:
            print("No OpenUrban Data Available")
        else:
            ulu = ee.ImageCollection(dataset
                                     .filterBounds(ee_rectangle['ee_geometry'])
                                     .select(self.band)
                                     .max()
                                     .reduce(ee.Reducer.firstNonNull())
                                     .rename('lulc')
                                     )

            data = get_image_collection(
                ulu,
                ee_rectangle,
                1,
                "urban land use"
            ).lulc

        return data

# Define reclassification
from enum import Enum

# From https://gfw.atlassian.net/wiki/spaces/CIT/pages/872349733/Surface+characteristics+by+LULC#Major-update-to-LULC-codes
class OpenUrbanClass(Enum):
    GREEN_SPACE_OTHER = 110.0
    BUILT_UP_OTHER = 120.0
    BARREN = 130.0
    PUBLIC_OPEN_SPACE = 200.0
    WATER = 300.0
    PARKING = 400.0
    ROADS = 500.0
    BUILDINGS_UNCLASSIFIED = 600.0
    BUILDINGS_UNCLASSIFIED_LOW_SLOPE = 601.0
    BUILDINGS_UNCLASSIFIED_HIGH_SLOPE = 602.0
    BUILDINGS_RESIDENTIAL = 610.0
    BUILDINGS_RESIDENTIAL_LOW_SLOPE = 611.0
    BUILDINGS_RESIDENTIAL_HIGH_SLOPE = 612.0
    BUILDINGS_NON_RESIDENTIAL = 620.0
    BUILDINGS_NON_RESIDENTIAL_LOW_SLOPE = 621.0
    BUILDINGS_NON_RESIDENTIAL_HIGH_SLOPE = 622.0

# Note, it seems these have to be in the same order as the OpenUrbanClass
reclass_map = {
    OpenUrbanClass.GREEN_SPACE_OTHER.value: 5.0,
    OpenUrbanClass.BUILT_UP_OTHER.value: 1.0,
    OpenUrbanClass.BARREN.value: 6.0,
    OpenUrbanClass.PUBLIC_OPEN_SPACE.value: 5.0,
    OpenUrbanClass.WATER.value: 7.0,
    OpenUrbanClass.PARKING.value: 1.0,
    OpenUrbanClass.ROADS.value: 1.0,
    OpenUrbanClass.BUILDINGS_UNCLASSIFIED.value: 2.0,
    OpenUrbanClass.BUILDINGS_UNCLASSIFIED_LOW_SLOPE.value: 2.0,
    OpenUrbanClass.BUILDINGS_UNCLASSIFIED_HIGH_SLOPE.value: 2.0,
    OpenUrbanClass.BUILDINGS_RESIDENTIAL.value: 2.0,
    OpenUrbanClass.BUILDINGS_RESIDENTIAL_LOW_SLOPE.value: 2.0,
    OpenUrbanClass.BUILDINGS_RESIDENTIAL_HIGH_SLOPE.value: 2.0,
    OpenUrbanClass.BUILDINGS_NON_RESIDENTIAL.value: 2.0,
    OpenUrbanClass.BUILDINGS_NON_RESIDENTIAL_LOW_SLOPE.value: 2.0,
    OpenUrbanClass.BUILDINGS_NON_RESIDENTIAL_HIGH_SLOPE.value: 2.0,
    }
