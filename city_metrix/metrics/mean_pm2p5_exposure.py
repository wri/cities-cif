from geopandas import GeoDataFrame, GeoSeries
import ee
from city_metrix.layers import Layer, AcagPM2p5, WorldPop, UrbanLandUse
from city_metrix.layers.layer import get_image_collection


def mean_pm2p5_exposure(zones: GeoDataFrame, acag_year=2022, pop_weighted=True, worldpop_agesex_classes=[], worldpop_year=2020, informal_only=False) -> GeoSeries:
    class WorldPopReprojected(Layer):
        def __init__(self, agesex_classes=[], worldpop_year=2020, acag_year=2022, multiply_by_pm2p5=False, **kwargs):
            super().__init__(**kwargs)
            self.agesex_classes = agesex_classes
            self.worldpop_year = worldpop_year
            self.acag_year = acag_year
            self.multiply_by_pm2p5 = multiply_by_pm2p5

        def get_data(self, bbox):
            acag_data = ee.Image(f'projects/wri-datalab/cities/aq/acag_annual_pm2p5_{self.acag_year}')
            if not self.agesex_classes:
                # total population
                dataset = ee.ImageCollection('WorldPop/GP/100m/pop')

                world_pop_ic = ee.ImageCollection(
                    dataset
                    .filterBounds(ee.Geometry.BBox(*bbox))
                    .filter(ee.Filter.inList('year', [self.worldpop_year]))
                    .select('population')
                    .mean()
                )

            else:
                # sum population for selected age-sex groups
                world_pop_age_sex = ee.ImageCollection('WorldPop/GP/100m/pop_age_sex')

                world_pop_age_sex_year = (world_pop_age_sex
                    .filterBounds(ee.Geometry.BBox(*bbox))
                    .filter(ee.Filter.inList('year', [self.worldpop_year]))
                    .select(self.agesex_classes)
                    .mean()
                )

                world_pop_ic = ee.ImageCollection(
                    world_pop_age_sex_year
                    .reduce(ee.Reducer.sum())
                    .rename('population')
                )
            world_pop_img = world_pop_ic.mosaic()
            world_pop_img_acagproj = world_pop_img.setDefaultProjection('EPSG:4326').reduceResolution(ee.Reducer.sum(), True, 65000).reproject(acag_data.projection())

            if self.multiply_by_pm2p5:
                result_img = world_pop_img_acagproj.multiply(acag_data)
            else:
                result_img = world_pop_img_acagproj

            data = get_image_collection(
                ee.ImageCollection(result_img),
                    bbox,
                    acag_data.projection().nominalScale().getInfo(),
                    "mean pm2.5 concentration"
                ).population
            return data
    class InformalMask(UrbanLandUse):
        def get_data(self, bbox):
            allvalues = super().get_data(bbox)
            return allvalues.where(allvalues==3)

    pm2p5_layer = AcagPM2p5(year=2022, return_above=0)
    if pop_weighted:
        if not informal_only:
            weightedsum = WorldPopReprojected(agesex_classes=worldpop_agesex_classes, worldpop_year=worldpop_year, multiply_by_pm2p5=True).groupby(zones).sum()
            sumofweights = WorldPopReprojected(agesex_classes=worldpop_agesex_classes, worldpop_year=worldpop_year, multiply_by_pm2p5=False).groupby(zones).sum()
        else:  # informal only
            informal_mask = InformalMask()
            weightedsum = WorldPopReprojected(agesex_classes=worldpop_agesex_classes, worldpop_year=worldpop_year, multiply_by_pm2p5=True).mask(informal_mask).groupby(zones).sum().fillna(0)
            sumofweights = WorldPopReprojected(agesex_classes=worldpop_agesex_classes, worldpop_year=worldpop_year, multiply_by_pm2p5=False).mask(informal_mask).groupby(zones).sum()
        return weightedsum / sumofweights
    else:  # not pop_weighted
        return pm2p5_layer.groupby(zones).sum() / pm2p5_layer.groupby(zones).count()
