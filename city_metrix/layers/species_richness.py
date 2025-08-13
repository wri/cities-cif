from enum import Enum
import numpy as np
import pandas as pd
import geopandas as gpd
import requests
import random, scipy
import shapely
import rasterio

from city_metrix.metrix_model import Layer, GeoExtent
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

    def __init__(self, taxon=GBIFTaxonClass.BIRDS, start_year=2019, end_year=2024, mask_layer=None, **kwargs):
        super().__init__(**kwargs)
        self.taxon = taxon
        self.start_year = start_year
        self.end_year = end_year
        self.mask_layer = mask_layer

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 allow_cache_retrieval=False):
        #Note: spatial_resolution and resampling_method arguments are ignored.

        poly = bbox.as_geographic_bbox().polygon
        print(
            "Retrieving {0} observations for bbox {1}, {2}, {3}, {4}\n".format(
                self.taxon.value["taxon"], *bbox.as_geographic_bbox().coords
            )
        )
        offset = -self.LIMIT
        observations = gpd.GeoDataFrame({"species": [], "geometry": []})
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
                    shapely.geometry.Point(
                        float(result["decimalLongitude"]),
                        float(result["decimalLatitude"]),
                    ),
                )
                for result in results["results"]
                if "species" in result.keys()
            ]

            if self.mask_layer is not None:  # Filter for points within unmasked region
                mask_raster = (self.mask_layer.get_data(bbox) * 0) + 1
                valid_shapes = rasterio.features.shapes(mask_raster, connectivity=8, transform=mask_raster.rio.transform())  # Polygonize the natural-areas raster
                valid_shapes = list(valid_shapes)
                valid_geoms = [i[0] for i in valid_shapes if i[1]==1]  # Only want the natural areas
                valid_gdf = gpd.GeoDataFrame({'id': range(len(valid_geoms)), 'geometry': [shapely.Polygon(j['coordinates'][0]) for j in valid_geoms]})
                valid_gdf_wgs = valid_gdf.dissolve().set_crs(bbox.as_utm_bbox().crs).to_crs('EPSG:4326')
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

        return gpd.GeoDataFrame({"species_count": [count_estimate], "geometry": [bbox.as_utm_bbox().polygon]}, crs=bbox.as_utm_bbox().crs)
