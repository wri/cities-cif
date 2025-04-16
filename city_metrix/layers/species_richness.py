from enum import Enum
from geopandas import GeoDataFrame
import numpy as np
import pandas as pd
import requests
import random, scipy
from shapely.geometry import Point

from .layer import Layer
from .layer_dao import retrieve_cached_city_data
from .layer_geometry import GeoExtent
from ..constants import GEOJSON_FILE_EXTENSION


class GBIFTaxonClass(Enum):
    VASCULAR_PLANTS = {"taxon": "Tracheophyta", "taxon_key": 7707728}
    ARTHROPODS = {"taxon": "Arthropoda", "taxon_key": 54}
    BIRDS = {"taxon": "Aves", "taxon_key": 212}


class SpeciesRichness(Layer):
    OUTPUT_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_LAYER_NAMING_ATTS = ["taxon"]
    MINOR_LAYER_NAMING_ATTS = ["start_year", "end_year"]

    """
    Attributes:
        taxon: Enum value from GBIFTaxonClass
        start_year, end_year: years used for data retrieval
    """

    API_URL = "https://api.gbif.org/v1/occurrence/search/"
    DATASETKEY = "50c9509d-22c7-4a22-a47d-8c48425ef4a7"  # iNaturalist research-grade observations
    LIMIT = 300

    NUM_CURVEFITS = 200

    def __init__(self, taxon=GBIFTaxonClass.BIRDS, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.taxon = taxon
        self.start_year = start_year
        self.end_year = end_year

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 allow_cache_retrieval=False):
        #Note: spatial_resolution and resampling_method arguments are ignored.

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data = retrieve_cached_city_data(self, bbox, allow_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        poly = bbox.as_geographic_bbox().polygon
        print(
            "Retrieving {0} observations for bbox {1}, {2}, {3}, {4}\n".format(
                self.taxon.value["taxon"], *bbox.as_geographic_bbox().coords
            )
        )
        offset = -self.LIMIT
        observations = GeoDataFrame({"species": [], "geometry": []})
        while offset == -self.LIMIT or not results["endOfRecords"]:
            offset += self.LIMIT
            url = "{0}?dataset_key={1}&taxon_key={2}&year={3},{4}&geometry={5}&limit={6}&offset={7}&hasCoordinate=true".format(
                self.API_URL,
                self.DATASETKEY,
                self.taxon.value["taxon_key"],
                self.start_year,
                self.end_year,
                str(poly),
                self.LIMIT,
                offset,
            )
            resp = requests.get(url)
            results = resp.json()
            print(
                "  Collected {0} of {1} observations".format(
                    results["offset"], results["count"]
                )
            )

            has_species = [
                (
                    result["species"],
                    Point(
                        float(result["decimalLongitude"]),
                        float(result["decimalLatitude"]),
                    ),
                )
                for result in results["results"]
                if "species" in result.keys()
            ]
            observations = pd.concat(
                [
                    observations,
                    GeoDataFrame(
                        {
                            "species": [i[0] for i in has_species],
                            "geometry": [i[1] for i in has_species],
                        }
                    ),
                ]
            )

        # Estimate species counts by estimating asymptote of species-accumulation curve created when observation order is randomized
        # Final estimate is average over NUM_CURVEFITS estimates

        if len(observations) > 1:
            taxon_observations = list(observations.species)
            asymptotes = []
            tries = 0
            while (len(asymptotes) < self.NUM_CURVEFITS):  # Different observation-orders give different results, so average over many
                tries += 1
                taxon_observations.sort(key=lambda x: random.random())  # Randomize order of observations
                sac = []  # Initialize species accumulation curve data
                for obs_count in range(1, len(taxon_observations)):  # Go through observation list from beginning
                    sac.append(len(set(taxon_observations[:obs_count])))  # and count unique species from start to index
                if (len(sac) > 5 and tries <= 1000):  # Avoid letting infinite-species errors stop the process
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
                count_estimate = -9999
            else:
                count_estimate = -round(np.mean(asymptotes))
        else:
            count_estimate = -9999

        return GeoDataFrame({"species_count": [count_estimate], "geometry": [bbox.as_utm_bbox().polygon]}, crs=bbox.as_utm_bbox().crs)
