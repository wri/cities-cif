import ee

from .layer import Layer, get_image_collection
from .albedo import Albedo
from .layer_geometry import GeoExtent, retrieve_cached_data

DEFAULT_SPATIAL_RESOLUTION = 10

class VegetationWaterMap(Layer):
    LAYER_ID = "vegetation_water_map"
    OUTPUT_FILE_FORMAT = 'tif'

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
        greenwater_layer: select returned layer from 'startgreenwaterIndex'/'endgreenwaterIndex'/'lossgreenwaterSlope'/'gaingreenwaterSlope'
    """
    def __init__(self, start_date="2016-01-01", end_date="2022-12-31", greenwater_layer='startgreenwaterIndex', **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.greenwater_layer = greenwater_layer

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cached_data_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        retrieved_cached_data = retrieve_cached_data(bbox, self.LAYER_ID, None, self.OUTPUT_FILE_FORMAT
                                                     ,allow_cached_data_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        NDVIthreshold = 0.4  # decimal
        NDWIthreshold = 0.3  # decimal
        # half the value of the p-value threshold to be used in the significance test.
        halfpvalue = 0.025

        # annual image collections and images
        def AnnualIC(ic, year):
            def addNDVI(image):
                ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
                return image.addBands(ndvi)
            def addNDWI(image):
                ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
                return image.addBands(ndwi)
            def addyear(image):
                return image.set("year", year)
            ImgColl = ic.filter(ee.Filter.stringStartsWith('system:index', year)).map(addNDVI).map(addNDWI).map(addyear)
            return ImgColl

        def AnnualImgGreen(ic, year):
            greenest = ic.select('NDVI').reduce(ee.Reducer.median()).rename('NDVI').addBands(ee.Image(year).rename('time_start')).float()
            bluest = ic.qualityMosaic('NDWI').select('NDWI').addBands(ee.Image(year).rename('time_start')).float()
            bluestThres = bluest.updateMask(bluest.select('NDWI').gte(NDWIthreshold))
            greenestnowater = greenest.updateMask(bluestThres.select('NDWI').unmask().Not())
            return greenestnowater

        def AnnualImgWater(ic, year):
            bluest = ic.select('NDWI').reduce(ee.Reducer.median()).rename('NDWI').addBands(ee.Image(year).rename('time_start')).float()
            return bluest

        def AnnualImgWatermask(ic, year):
            bluest = ic.qualityMosaic('NDWI').select('NDWI').addBands(ee.Image(year).rename('time_start')).float()
            bluestThres = bluest.updateMask(bluest.select('NDWI').gte(NDWIthreshold))
            return bluestThres

        def AnnualImgGreenmask(ic, year):
            greenest = ic.qualityMosaic('NDVI').select('NDVI').addBands(ee.Image(year).rename('time_start')).float()
            greenestThres = greenest.updateMask(greenest.select('NDVI').gte(NDVIthreshold))
            return greenestThres

        # Functions for significance test
        # https://developers.google.com/earth-engine/tutorials/community/nonparametric-trends
        # https://code.earthengine.google.com/bce3dc00c56df4246c5d32f5fcccf5c7
        # //////////////////////////////////////singificance test///////////////////////////////////////////////////////////////
        def senum(lfx):
            def senumwrap(Im):
                esty = lfx.select('scale').multiply(Im.select('time_start')).add(lfx.select('offset'))
                diff = Im.select('NDVI').subtract(esty)
                pow = diff.multiply(diff)
                return (pow)
            return (senumwrap)

        def sedenom(mosaicmeanx):
            def sedenomwrap(Im):
                diff = Im.select('time_start').subtract(mosaicmeanx.select('time_start'))
                pow = diff.multiply(diff)
                return (pow)
            return (sedenomwrap)

        # https://en.wikipedia.org/wiki/Error_function#Cumulative_distribution_function
        def eeCdf(t):
            return ee.Image(0.5).multiply(ee.Image(1).add(ee.Image(t).divide(ee.Image(2).sqrt()).erf()))

        # /////green normalized Difference///////
        def significanceGreen(gtrend, glinearfit, SampleNumber):
            mosaicmean = gtrend.mean()
            mosaicNum = gtrend.map(senum(glinearfit)).sum()
            mosaicDenom = gtrend.map(sedenom(mosaicmean)).sum()
            StdDev = mosaicNum.divide(mosaicDenom)
            # Standard Error - from SampleNumber samples
            se = StdDev.divide(SampleNumber).sqrt()
            # Test Statistic
            gT = glinearfit.select('scale').divide(se)
            # Compute P-values.
            gP = ee.Image(1).subtract(eeCdf(gT.abs()))
            return gP

        # /////water normalized Difference///////
        def significanceWater(wtrend, wlinearfit, SampleNumber):
            def senum(lfx):
                def senumwrap(Im):
                    esty = lfx.select('scale').multiply(Im.select('time_start')).add(lfx.select('offset'))
                    diff = Im.select('NDWI').subtract(esty)
                    pow = diff.multiply(diff)
                    return (pow)
                return (senumwrap)

            mosaicmean = wtrend.mean()
            mosaicNum = wtrend.map(senum(wlinearfit)).sum()
            mosaicDenom = wtrend.map(sedenom(mosaicmean)).sum()
            StdDev = mosaicNum.divide(mosaicDenom)
            # Standard Error - from SampleNumber samples
            se = StdDev.divide(SampleNumber).sqrt()
            # Test Statistic
            wT = wlinearfit.select('scale').divide(se)
            # Compute P-values.
            wP = ee.Image(1).subtract(eeCdf(wT.abs()))
            return wP


        # function to generate vegetation and water trend and change maps
        def get_map_vegwaterchange(IC, greenwater_layer):
            gwic2019 = AnnualIC(IC, '2019')
            gwic2020 = AnnualIC(IC, '2020')
            gwic2021 = AnnualIC(IC, '2021')
            gwic2022 = AnnualIC(IC, '2022')
            gwic = ((gwic2019).merge(gwic2020).merge(gwic2021).merge(gwic2022))

            d = {}
            for i in range(2019, 2023):
                # https://stackoverflow.com/questions/6181935/how-do-you-create-different-variable-names-while-in-a-loop
                filteredgwic = gwic.filter(ee.Filter.eq("year", str(i)))
                d["g{0}".format(i)] = AnnualImgGreen(filteredgwic, i)
                d["w{0}".format(i)] = AnnualImgWater(filteredgwic, i)
                d["w{0}mask".format(i)] = AnnualImgWatermask(filteredgwic, i)
                d["g{0}mask".format(i)] = AnnualImgGreenmask(filteredgwic, i)

            gtrend = ee.ImageCollection.fromImages([d["g2019"], d["g2020"], d["g2021"], d["g2022"]])
            wtrend = ee.ImageCollection.fromImages([d["w2019"], d["w2020"], d["w2021"], d["w2022"]])
            wanyyear = (ee.Image(
                d["w2019mask"].select('NDWI'))
                .blend(d["w2020mask"].select('NDWI'))
                .blend(d["w2021mask"].select('NDWI'))
                .blend(d["w2022mask"].select('NDWI'))
            )
            ganyyear = (ee.Image(
                d["g2019mask"].select('NDVI'))
                .blend(d["g2020mask"].select('NDVI'))
                .blend(d["g2021mask"].select('NDVI'))
                .blend(d["g2022mask"].select('NDVI'))
            )
            startyear = ee.Number(2019)
            endyear = ee.Number(2022)
            sampleNumber = (endyear.subtract(startyear)).add(1)
            gstartmask = AnnualImgGreenmask(gwic.filter(ee.Filter.eq("year", '2019')), startyear)
            wstartmask = AnnualImgWatermask(gwic.filter(ee.Filter.eq("year", '2019')), startyear)
            gendmask = AnnualImgGreenmask(gwic.filter(ee.Filter.eq("year", '2022')), endyear)
            wendmask = AnnualImgWatermask(gwic.filter(ee.Filter.eq("year", '2022')), endyear)

            # 0.05 #   minimum threshold scale value from linear fit trend line to be considered a vegetation change.
            minSlopeVeg = ee.Number(0.1)
            # 0.05 #  minimum threshold scale value from linear fit trend line to be considered a water change.
            minSlopeWater = ee.Number(0.1)

            # Create linear fit trend line for years of NDVI data
            # https://developers.google.com/earth-engine/guides/reducers_regression#linearfit
            glinearfit = ee.Image(gtrend.select(['time_start', 'NDVI']).reduce(ee.Reducer.linearFit()))

            # apply significance test
            # Pixels that can have the null hypothesis (there is no trend) rejected.
            # Specifically, if the true trend is zero, there would be less than 5% (double "halfpvalue")
            # chance of randomly obtaining the observed result (that there is a trend).
            gsignifMask = significanceGreen(gtrend, glinearfit, sampleNumber).lte(halfpvalue)
            glinearfit = glinearfit.updateMask(gsignifMask)

            # Annual slope value for each pixel above threshold. If interested in value for timeperiod, can use .multiply(ee.Image(6)). Can also mask based on offset to limit based on starting vegetation level.
            glfLimit = (glinearfit.select('scale')  # .multiply(ee.Image(6))
                        .updateMask(glinearfit.select('scale').gte(minSlopeVeg).Or(glinearfit.select('scale').lte(ee.Number(0).subtract(minSlopeVeg))))
                        )
            greenanyyearMask = ee.Image(0).where(ganyyear.neq(0), 1)

            glfLimitanyyeargreen = glfLimit.updateMask(greenanyyearMask)
            glfLimitanyyeargreenLoss = glfLimitanyyeargreen.updateMask(glfLimitanyyeargreen.lt(0))
            glfLimitanyyeargreenGain = glfLimitanyyeargreen.updateMask(glfLimitanyyeargreen.gt(0))

            # Create linear fit trend line for years of NDWI data
            wlinearfit = ee.Image(wtrend.select(['time_start', 'NDWI']).reduce(ee.Reducer.linearFit()))

            # apply significance test
            # Pixels that can have the null hypothesis (there is no trend) rejected.
            # Specifically, if the true trend is zero, there would be less than 5% (double "halfpvalue")
            # chance of randomly obtaining the observed result (that there is a trend).
            wsignifMask = significanceWater(wtrend, wlinearfit, sampleNumber).lte(halfpvalue)
            wlinearfit = wlinearfit.updateMask(wsignifMask)

            # Annual slope value for each pixel above threshold. If interested in value for timeperiod, can use .multiply(ee.Image(6)). Can also mask based on offset to limit based on starting vegetation level.
            wlfLimit = (wlinearfit.select('scale')  # .multiply(ee.Image(6))
                        .updateMask(wlinearfit.select('scale').gte(minSlopeWater).Or(wlinearfit.select('scale').lte(ee.Number(0).subtract(minSlopeVeg))))
                        )

            wateranyyearMask = ee.Image(0).where(wanyyear.neq(0), 1)

            wlfLimitanyyearwater = wlfLimit.updateMask(wateranyyearMask)
            wlfLimitanyyearwaterLoss = wlfLimitanyyearwater.updateMask(wlfLimitanyyearwater.lt(0))
            wlfLimitanyyearwaterGain = wlfLimitanyyearwater.updateMask(wlfLimitanyyearwater.gt(0))

            gorwstartmask = gstartmask.select('NDVI').blend(wstartmask.select('NDWI'))
            gorwendmask = gendmask.select('NDVI').blend(wendmask.select('NDWI'))
            greenorwaterLimitLoss = glfLimitanyyeargreenLoss.blend(wlfLimitanyyearwaterLoss)
            greenorwaterLimitGain = glfLimitanyyeargreenGain.blend(wlfLimitanyyearwaterGain)

            if greenwater_layer == 'startgreenwaterIndex':
                return gorwstartmask.rename('greenwater_layer')
            elif greenwater_layer == 'endgreenwaterIndex':
                return gorwendmask.rename('greenwater_layer')
            elif greenwater_layer == 'lossgreenwaterSlope':
                return greenorwaterLimitLoss.rename('greenwater_layer')
            elif greenwater_layer == 'gaingreenwaterSlope':
                return greenorwaterLimitGain.rename('greenwater_layer')

        ee_rectangle = bbox.to_ee_rectangle()
        s2cloudmasked = (Albedo()
                         .get_masked_s2_collection(ee_rectangle['ee_geometry'],
                                                   self.start_date,
                                                   self.end_date)
                         )

        vegwatermap = get_map_vegwaterchange(s2cloudmasked, self.greenwater_layer)

        data = get_image_collection(
            ee.ImageCollection(vegwatermap), 
            ee_rectangle,
            spatial_resolution,
            "vegetation water map"
        ).greenwater_layer

        return data
