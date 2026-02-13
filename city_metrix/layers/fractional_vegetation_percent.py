import ee
import numpy as np
import xarray as xr

from city_metrix.metrix_model import GeoExtent, Layer, get_image_collection
from city_metrix.metrix_tools import align_raster_array

from ..constants import GTIFF_FILE_EXTENSION
from .world_pop import WorldPop

DEFAULT_SPATIAL_RESOLUTION = 10


class FractionalVegetationPercent(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    PROCESSING_TILE_SIDE_M = 5000
    MAJOR_NAMING_ATTS = ["min_threshold"]
    MINOR_NAMING_ATTS = None

    def __init__(self, min_threshold=None, year=2024, index_aggregation=False, **kwargs):
        super().__init__(**kwargs)
        self.min_threshold = min_threshold
        self.year = year
        self.index_aggregation = index_aggregation


    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        stophere
        if resampling_method is not None:
            raise Exception("resampling_method can not be specified.")
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        dw = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
        S2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        S2CS = ee.ImageCollection("GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED")
        ENDMEMBERS_IC = ee.ImageCollection("projects/wri-datalab/cities/heat/fracveg_endmembers_bybbox")
        bbox_ee = bbox.to_ee_rectangle()

        # Sentinel
        # year = self.year
        date_start = f"{self.year}-01-01"
        date_end = f"{self.year}-12-31"

        # The threshold for masking; values between 0.50 and 0.65 generally work well.
        # Higher values will remove thin clouds, haze & cirrus shadows.
        CLEAR_THRESHOLD = 0.60

        # Function to create the Fr vegetation image in the UTM projection of the S2 image
        # using the first image, in some cases a city may span two zones but for now this is
        # good enough

        PCTL_FULLVEG = 75
        PCTL_NONVEG = 5

        def calcFr(aoi, vegpctl, soilpctl):

            endm_ic = ENDMEMBERS_IC.filterBounds(aoi)
            if endm_ic.size().gt(0):
                endm_img = endm_ic.first()
            else:
                endm_img = None

            # Cloud score+
            S2filtered = (
                S2.filterBounds(aoi)
                .filterDate(date_start, date_end)
                .linkCollection(S2CS, ["cs"])
                .map(lambda img: img.updateMask(img.select("cs").gte(CLEAR_THRESHOLD)).divide(10000))
            )

            # Function to add NDVI to Sentinel images
            def addNDVI(image):
                ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
                return image.addBands(ndvi)

            S2ndvi = S2filtered.map(addNDVI)

            # Create a 90th percentile NDVI image
            ndvi = S2ndvi.select("NDVI").reduce(ee.Reducer.percentile([90])).rename("NDVI")

            if endm_img is not None:
                print('Using stored endmembers')
                aoi_centroid = (
                    aoi
                    .intersection(endm_img.geometry(), maxError=1, proj=aoi.projection())
                    .centroid(maxError=1)
                )
                sample = endm_img.sampleRegions(collection=ee.FeatureCollection(aoi_centroid)).first()
                vegNDVI = sample.get('fullveg_ndvi')
                soilNDVI = sample.get('nonveg_ndvi')
            else:
                print('Retrieving new endmembers')
                # Filter dynamic world data
                dwFiltered = dw.filterBounds(aoi).filterDate(date_start, date_end)

                # choose the most commonly occurring class for each pixel
                # clip to city area and map to 1 for veg (trees & grass)
                # and 2 for bare soil
                dwMode = dwFiltered.select("label").reduce(ee.Reducer.mode()).clip(aoi)

                dwClass = (
                    dwMode.remap([0, 1, 2, 3, 4, 5, 6, 7, 8], [0, 1, 1, 0, 0, 1, 2, 0, 0])
                    .selfMask()
                    .rename("lc")
                )

                # Percentile values from:
                # Zeng, X., Dickinson, R. E., Walker, A., Shaikh, M., DeFries, R. S., & Qi, J. (2000).
                # Derivation and Evaluation of Global 1-km Fractional Vegetation Cover Data for Land Modeling.
                # Journal of Applied Meteorology, 39(6), 826–839.
                # https://doi.org/10.1175/1520-0450(2000)039<0826:DAEOGK>2.0.CO;2

                # Calculates the nth percentile value for vegetation and soil NDVI

                vegNDVI = (
                    ndvi.updateMask(dwClass.eq(1))
                    .reduceRegion(
                        reducer=ee.Reducer.percentile([vegpctl]),
                        geometry=aoi,
                        scale=10,
                        maxPixels=10e13,
                    )
                    .get("NDVI")
                )
                soilNDVI = (
                    ndvi.updateMask(dwClass.eq(2))
                    .reduceRegion(
                        reducer=ee.Reducer.percentile([soilpctl]),
                        geometry=aoi,
                        scale=10,
                        maxPixels=10e13,
                    )
                    .get("NDVI")
                )

            return ee.Dictionary({"vegNDVI": vegNDVI, "soilNDVI": soilNDVI, "ndviImage": ndvi})

        # calcFr(bbox_ee["ee_geometry"], PCTL_FULLVEG, PCTL_NONVEG)

        def fracVeg(geom, vegpctl, soilpctl):
            results = calcFr(geom, vegpctl, soilpctl)
            ndviImage = ee.Image(results.get("ndviImage")).multiply(100).toUint8()
            vegNDVI = results.getNumber("vegNDVI").multiply(100).toUint8()
            soilNDVI = results.getNumber("soilNDVI").multiply(100).toUint8()

        #    if vegNDVI.getInfo() is None or soilNDVI.getInfo() is None:
        #        return None

            return (
                ndviImage.subtract(soilNDVI)
                .divide(vegNDVI.subtract(soilNDVI))
                .pow(2)
                .min(1)
                .multiply(100)
                .toUint8()
                .rename("Fr")
            )

        Fr = fracVeg(bbox_ee["ee_geometry"], PCTL_FULLVEG, PCTL_NONVEG)
        if Fr is None:
            data = (
                get_image_collection(
                    ee.ImageCollection(
                        [
                            dw.filterBounds(bbox_ee["ee_geometry"])
                            .first()
                            .select("label")
                        ]
                    ),
                    bbox_ee,
                    spatial_resolution,
                    "dummy",
                ).label * np.nan
            )
            data.rio.write_crs(bbox.as_utm_bbox().crs, inplace=True)
        else:
            data = get_image_collection(
                ee.ImageCollection([Fr]),
                bbox_ee,
                spatial_resolution,
                "fractional vegetation",
            ).astype(np.uint8).Fr

            if self.min_threshold is not None:
                data = xr.where(data >= self.min_threshold, 1, np.nan).rio.write_crs(bbox.as_utm_bbox().crs, inplace=True)
        if self.index_aggregation:
            wp_array =  WorldPop().get_data(bbox)
            return align_raster_array(data, wp_array)
        return data
