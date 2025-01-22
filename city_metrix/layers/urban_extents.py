from dask.diagnostics import ProgressBar
import ee
import geemap

from .layer import Layer

class UrbanExtents(Layer):

    def __init__(self, year=2020, **kwargs):
        super().__init__(**kwargs)
        if not year in [1980, 1990, 2000, 2005, 2010, 2015, 2020]:
            raise Exception(f'Year {year} not available.')
        self.year = year

    def get_data(self, bbox):
        ue_fc = ee.FeatureCollection(f'projects/wri-datalab/cities/urban_land_use/data/global_cities_Aug2024/urbanextents_unions_{self.year}')
        urbexts = ue_fc.filterBounds(ee.Geometry.BBox(*bbox))
        urbexts_gdf = geemap.ee_to_gdf(urbexts)
        urbexts_dissolved = urbexts_gdf.dissolve()
        urbexts_dissolved['city_id_large'] = ['+'.join([str(i) for i in urbexts_gdf['city_id_large']])]
        urbexts_dissolved['city_ids'] = ['+'.join([str(i) for i in urbexts_gdf['city_ids']])]
        urbexts_dissolved['city_name_large'] = ['+'.join([str(i) for i in urbexts_gdf['city_name_large']])]
        urbexts_dissolved['city_names'] = ['+'.join([str(i) for i in urbexts_gdf['city_names']])]
        urbexts_dissolved['country_name'] = ['+'.join([str(i) for i in urbexts_gdf['country_name']])]
        urbexts_dissolved['reference_idstring'] = ['+'.join([str(i) for i in urbexts_gdf['reference_idstring']])]

        return urbexts_dissolved