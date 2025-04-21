from geopandas import GeoSeries

from city_metrix.constants import GEOJSON_FILE_EXTENSION
from city_metrix.layers import AcagPM2p5, PopWeightedPM2p5, UrbanLandUse, WorldPopClass
from city_metrix.metrix_model import GeoZone, Metric


class MeanPM2P5Exposure(Metric):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,
                 informal_only=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.informal_only = informal_only

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:

        pm2p5_layer = AcagPM2p5()

        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=3)
            mean_pm2p5 = pm2p5_layer.mask(informal_layer).groupby(geo_zone).mean()
        else:
            mean_pm2p5 = pm2p5_layer.groupby(geo_zone).mean()

        return mean_pm2p5


class MeanPM2P5ExposurePopWeighted(Metric):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,
                 worldpop_agesex_classes=[],
                 informal_only=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.informal_only = informal_only

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:

        pop_weighted_pm2p5 = PopWeightedPM2p5(worldpop_agesex_classes=self.worldpop_agesex_classes)

        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=3)
            mean_pm2p5 = pop_weighted_pm2p5.mask(informal_layer).groupby(geo_zone).mean()
        else:
            mean_pm2p5 = pop_weighted_pm2p5.groupby(geo_zone).mean()

        return mean_pm2p5


class MeanPM2P5ExposurePopWeightedChildren(Metric):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:
        pop_weighted_pm2p5_children = (MeanPM2P5ExposurePopWeighted(worldpop_agesex_classes=WorldPopClass.CHILDREN,
                                                                    informal_only=False))

        return pop_weighted_pm2p5_children.get_metric(geo_zone=geo_zone)


class MeanPM2P5ExposurePopWeightedElderly(Metric):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:
        pop_weighted_pm2p5_elderly = (MeanPM2P5ExposurePopWeighted(worldpop_agesex_classes=WorldPopClass.ELDERLY,
                                                                    informal_only=False))

        return pop_weighted_pm2p5_elderly.get_metric(geo_zone=geo_zone)


class MeanPM2P5ExposurePopWeightedFemale(Metric):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:
        pop_weighted_pm2p5_female = (MeanPM2P5ExposurePopWeighted(worldpop_agesex_classes=WorldPopClass.FEMALE,
                                                                  informal_only=False))

        return pop_weighted_pm2p5_female.get_metric(geo_zone=geo_zone)


class MeanPM2P5ExposurePopWeightedInformal(Metric):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:
        pop_weighted_pm2p5_informal = (MeanPM2P5ExposurePopWeighted(worldpop_agesex_classes=[],
                                                                  informal_only=True))

        return pop_weighted_pm2p5_informal.get_metric(geo_zone=geo_zone)
