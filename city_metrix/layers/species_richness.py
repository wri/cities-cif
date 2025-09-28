from enum import Enum
import numpy as np
import pandas as pd
import geopandas as gpd
import requests
import random
import scipy
import shapely
import rasterio
import time

from city_metrix.metrix_model import Layer, GeoExtent
from ..constants import GEOJSON_FILE_EXTENSION


class GBIFTaxonClass(Enum):
    VASCULAR_PLANTS = {"taxon": "Tracheophyta", "taxon_key": 7707728}
    ARTHROPODS = {"taxon": "Arthropoda", "taxon_key": 54}
    BIRDS = {"taxon": "Aves", "taxon_key": 212}


class SpeciesRichness(Layer):
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

    API_URL = "https://api.gbif.org/v1/occurrence/search/"
    DATASETKEY = "50c9509d-22c7-4a22-a47d-8c48425ef4a7"  # iNaturalist research-grade observations
    LIMIT = 300
    NUM_CURVEFITS = 200

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
        while offset == -self.LIMIT or not results_json["endOfRecords"]:
            offset += self.LIMIT
            params = {
                "dataset_key": self.DATASETKEY,
                "taxon_key": self.taxon.value["taxon_key"],
                "year": f"{self.start_year},{self.end_year}",
                "geometry": str(poly),
                "limit": self.LIMIT,
                "offset": offset,
                "hasCoordinate": "true",
            }
            remaining_attempts = 6
            while remaining_attempts > 0:
                resp = requests.get(self.API_URL, params=params, headers={"Accept": "application/json"})
                results_json = resp.json()
                if isinstance(results_json, dict):
                    print(f"Collected {results_json['offset']} of {results_json['count']} observations")
                    break
                else:
                    time.sleep(5)  # Rate limiting
                    remaining_attempts -= 1

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
                        }
                    ),
                ]
            )

        # Estimate species counts by estimating asymptote of species-accumulation curve created when observation order is randomized
        # Final estimate is average over NUM_CURVEFITS estimates

        if len(observations) >= 10:
            taxon_observations = list(observations.species)
            asymptotes = []
            tries = 0
            # Different observation-orders give different results, so average over many
            while (len(asymptotes) < self.NUM_CURVEFITS):
                tries += 1
                # Randomize order of observations
                random.shuffle(taxon_observations)
                sac = []  # Initialize species accumulation curve data
                # Go through observation list from beginning
                for obs_count in range(1, len(taxon_observations)):
                    # and count unique species from start to index
                    sac.append(len(set(taxon_observations[:obs_count])))
                # Avoid letting infinite-species errors stop the process
                if (len(sac) > 5 and tries <= 1000):
                    try:
                        asymptotes.append(
                            scipy.optimize.curve_fit(
                                lambda x, a, b, c: -((a * np.exp(-b * x)) + c),
                                list(range(1, len(sac) + 1)),
                                sac,
                            )[0][2]
                        )
                    except:
                        pass
                else:
                    asymptotes.append(-1)
            if -1 in asymptotes:
                count_estimate = np.nan
            else:
                count_estimate = -round(np.mean(asymptotes))
        else:
            count_estimate = np.nan

        return gpd.GeoDataFrame({"species_count": [count_estimate], "geometry": [bbox.as_utm_bbox().polygon]}, crs=bbox.as_utm_bbox().crs)
