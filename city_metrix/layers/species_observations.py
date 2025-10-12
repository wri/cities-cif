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

    LIMIT = 300

    API_URL = "https://api.gbif.org/v1/occurrence/search/"
    DATASETKEY = "50c9509d-22c7-4a22-a47d-8c48425ef4a7"  # iNaturalist research-grade observations


    def __init__(self, taxon=GBIFTaxonClass.BIRDS, start_year=2019, end_year=2024, mask_layer=None, **kwargs):
        super().__init__(**kwargs)
        self.taxon = taxon
        self.start_year = start_year
        self.end_year = end_year
        self.mask_layer = mask_layer

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 allow_cache_retrieval=False):
        # Note: spatial_resolution and resampling_method arguments are ignored.

        poly = bbox.as_geographic_bbox().polygon
        print(f"Retrieving {self.taxon.value['taxon']} observations for bbox {bbox.as_geographic_bbox().coords}")
        offset = -self.LIMIT
        observations = gpd.GeoDataFrame({"species": [], "geometry": []})
        at_limit = False
        while offset == -self.LIMIT or (not results_json["endOfRecords"]) or (not at_limit):
            offset += self.LIMIT
            if offset + self.LIMIT < MAX_DOWNLOADS:
                limit = self.LIMIT
            else:
                limit = 99999 - offset
                at_limit = True
            params = {
                "dataset_key": self.DATASETKEY,
                "taxon_key": self.taxon.value["taxon_key"],
                "year": f"{self.start_year},{self.end_year}",
                "geometry": str(poly),
                "limit": limit,
                "offset": offset,
                "hasCoordinate": "true",
            }
            
            remaining_tries = 10
            while remaining_tries > 0:
                resp = requests.get(self.API_URL, params=params, headers={"Accept": "application/json"})
                results_json = resp.json()
                if isinstance(results_json, dict):
                    print(f"Collected {results_json['offset']} of {results_json['count']} observations")
                    break
                else:
                    time.sleep(10)  # Rate limiting
                    remaining_tries -= 1

            has_species = [
                (
                    result.get("species"),
                    shapely.geometry.Point(
                        float(result.get("decimalLongitude")),
                        float(result.get("decimalLatitude")),
                    ),
                )
                for result in results_json["results"]
                if "species" in result
            ]

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
                    bbox.as_utm_bbox().crs).to_crs('EPSG:4326')
                has_species = [
                    obs for obs in has_species if obs[1].intersects(valid_gdf_wgs.geometry.iloc[0])
                ]

            observations = pd.concat(
                [
                    observations,
                    gpd.GeoDataFrame(
                        {
                            "species": [i[0] for i in has_species],
                            "geometry": [i[1] for i in has_species],
                        },
                        crs = WGS_CRS
                    ),
                ]
            )


        return observations.to_crs(bbox.as_utm_bbox().crs)
        #return gpd.GeoDataFrame({"species_count": [count_estimate], "geometry": [bbox.as_utm_bbox().polygon]}, crs=bbox.as_utm_bbox().crs)
