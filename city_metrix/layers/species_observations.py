from enum import Enum
import numpy as np
import pandas as pd
import geopandas as gpd
import requests

import shapely
import rasterio
import time

from city_metrix.metrix_model import Layer, GeoExtent
from ..constants import GEOJSON_FILE_EXTENSION, WGS_CRS

GBIF_PATH = 'https://wri-cities-indicators.s3.us-east-1.amazonaws.com/devdata/inputdata/gbif_occurrence'

# MAX_DOWNLOADS = 100000

class GBIFTaxonClass(Enum):
    VASCULAR_PLANTS = {"taxon": "Tracheophyta", "taxon_key": 7707728}
    ARTHROPODS = {"taxon": "Arthropoda", "taxon_key": 54}
    BIRDS = {"taxon": "Aves", "taxon_key": 212}


class SpeciesObservations(Layer):
    """
    Layer for estimating species richness using GBIF/iNaturalist data.

    Attributes:
        taxon: Enum value from GBIFTaxonClass
        start_year, end_year: years used for data retrieval
        mask_layer: Optional mask to filter valid regions
    """
    OUTPUT_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["taxon"]
    MINOR_NAMING_ATTS = ["start_year", "end_year"]

    # LIMIT = 300

    # API_URL = "https://api.gbif.org/v1/occurrence/search/"
    # DATASETKEY = "50c9509d-22c7-4a22-a47d-8c48425ef4a7"  # iNaturalist research-grade observations


    def __init__(self, city_id='ARG-Buenos_Aires', geo_level='adminbound', taxon=GBIFTaxonClass.BIRDS, start_year=2019, end_year=2024, mask_layer=None, **kwargs):
        super().__init__(**kwargs)
        self.city_id = city_id
        self.geo_level = geo_level
        self.taxon = taxon
        self.start_year = start_year
        self.end_year = end_year
        self.mask_layer = mask_layer

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 allow_cache_retrieval=False):
        filepath = f'{GBIF_PATH}/{self.city_id}__urbext-admin-union__{self.taxon.value["taxon"]}__{self.start_year}-{self.end_year}.geojson'
        print(filepath)
        all_observations = gpd.GeoDataFrame.from_file(filepath)
        bbox_shape = shapely.box(*bbox.as_geographic_bbox().coords)
        observations = all_observations.loc[all_observations.within(bbox_shape)]

        if self.mask_layer is not None:  # Filter for points within unmasked region
            mask_raster = (self.mask_layer.get_data(bbox) * 0) + 1
            valid_shapes = rasterio.features.shapes(
                # Polygonize the natural-areas raster
                mask_raster, connectivity=8, transform=mask_raster.rio.transform())
            valid_shapes = list(valid_shapes)
            # Only want the natural areas
            valid_geoms = [i[0] for i in valid_shapes if i[1] == 1]
            valid_gdf = gpd.GeoDataFrame({'id': range(len(valid_geoms)), 'geometry': [
                                         shapely.Polygon(j['coordinates'][0]) for j in valid_geoms]})
            valid_gdf_wgs = valid_gdf.dissolve().set_crs(
                bbox.as_utm_bbox().crs).to_crs(WGS_CRS)
            observations = observations.loc[observations.intersects(valid_gdf_wgs.geometry.iloc[0])]


        return observations.to_crs(bbox.as_utm_bbox().crs)
        #return gpd.GeoDataFrame({"species_count": [count_estimate], "geometry": [bbox.as_utm_bbox().polygon]}, crs=bbox.as_utm_bbox().crs)
