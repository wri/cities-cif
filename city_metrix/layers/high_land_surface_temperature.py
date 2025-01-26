from .landsat_collection_2 import LandsatCollection2
from .land_surface_temperature import LandSurfaceTemperature
from .layer import Layer
from shapely.geometry import box
import datetime
import ee

from .layer_geometry import LayerBbox

DEFAULT_SPATIAL_RESOLUTION = 30

class HighLandSurfaceTemperature(Layer):
    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """
    THRESHOLD_ADD = 3

    def __init__(self, start_date="2013-01-01", end_date="2023-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, bbox: LayerBbox, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        hottest_date = self.get_hottest_date(bbox)
        start_date = (hottest_date - datetime.timedelta(days=45)).strftime("%Y-%m-%d")
        end_date = (hottest_date + datetime.timedelta(days=45)).strftime("%Y-%m-%d")

        ee_rectangle = bbox.to_ee_rectangle(output_as='utm')
        lst = (LandSurfaceTemperature(start_date, end_date)
               .get_data(bbox, spatial_resolution))

        lst_mean = lst.mean(dim=['x', 'y'])
        high_lst = lst.where(lst >= (lst_mean + self.THRESHOLD_ADD))
        return high_lst

    def get_hottest_date(self, bbox):
        if bbox.units == "degrees":
            centroid = bbox.centroid
        else:
            wgs_bbox = bbox.as_lat_lon_bbox()
            centroid = wgs_bbox.centroid
        center_lon = centroid.x
        center_lat = centroid.y

        dataset = ee.ImageCollection("ECMWF/ERA5/DAILY")

        ee_rectangle = bbox.to_ee_rectangle(output_as='utm')
        AirTemperature = (
            dataset
            .filter(
                ee.Filter
                .And(ee.Filter.date(self.start_date, self.end_date),
                     ee.Filter.bounds(ee_rectangle['ee_geometry'])
                     )
            )
            .select(['maximum_2m_air_temperature'], ['tasmax'])
        )

        # add date as a band to image collection
        def addDate(image):
            img_date = ee.Date(image.date())
            img_date = ee.Number.parse(img_date.format('YYYYMMdd'))
            return image.addBands(ee.Image(img_date).rename('date').toInt())

        withdates = AirTemperature.map(addDate)

        # create a composite with the hottest day value and dates for every location and add to map
        hottest = withdates.qualityMosaic('tasmax')

        # reduce composite to get the hottest date for centroid of ROI
        resolution = dataset.first().projection().nominalScale()
        hottest_date = (
            ee.Number(
                hottest.reduceRegion(ee.Reducer.firstNonNull(),
                                     ee.Geometry.Point([center_lon, center_lat]),
                                     resolution
                                     ).get('date')
            )
            .getInfo()
        )

        # convert to date object
        formated_hottest_data = datetime.datetime.strptime(str(hottest_date), "%Y%m%d").date()

        return formated_hottest_data
