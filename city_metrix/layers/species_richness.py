from .layer import Layer
from enum import Enum
from geopandas import GeoDataFrame
import numpy as np
import shapely
import requests, json, geojson
import random, scipy
from collections import defaultdict
from scipy.optimize import curve_fit
from shapely.geometry import Point, Polygon, MultiPolygon, shape

class GBIFTaxonClass(Enum):
    VASCULAR_PLANTS = {'taxon': 'Tracheophyta', 'taxon_key': 7707728}
    ARTHROPODS = {'taxon': 'Arthropoda', 'taxon_key': 54}
    BIRDS = {'taxon': 'Aves', 'taxon_key': 212}


class SpeciesRichness(Layer):
    """
    Attributes:
        taxon: Enum value from GBIFTaxonClass
        start_year, end_year: years used for data retrieval
    """

    API_URL = 'https://api.gbif.org/v1/occurrence/search/'
    DATASETKEY = '50c9509d-22c7-4a22-a47d-8c48425ef4a7'  # iNaturalist research-grade observations
    LIMIT = 300

    NUM_CURVEFITS = 200

    def __init__(self, taxon, start_year=2024, end_year=2019, **kwargs):
        super().__init__(**kwargs)
        self.taxon = taxon.value
        self.start_year = start_year
        self.end_year = end_year

    def get_data(self, bbox):
        poly = shapely.geometry.box(*bbox)
        print("Retrieving {0} observations for bbox {1}, {2}, {3}, {4}\n".format(self.taxon['taxon'], *bbox))
        offset = -self.LIMIT
        observations = gpd.GeoDataFrame({'species': [], 'geometry': []})
        while offset == -self.LIMIT or not results['endOfRecords']:
            offset += self.LIMIT
            url = '{0}?dataset_key={1}&taxon_key={2}&year={3},{4}&geometry={5}&limit={6}&offset={7}&hasCoordinate=true'.format(self.API_URL, self.DATASETKEY, self.taxon['taxon_key'], self.start_year, self.end_year, str(poly), self.LIMIT, offset)
            resp = requests.get(url)
            results = resp.json()
            print('  Collected {0} of {1} observations'.format(results['offset'], results['count']))
            # Note spatial subsetting of points happens below (twice) as part of the conditions in the list comprehensions
            has_species = [(result['species'], Point(float(result['decimalLongitude']), float(result['decimalLatitude']))) for result in results['results'] if 'species' in result.keys()]
            observations = pd.concat([observations, gpd.GeoDataFrame({'species': [i[0] for i in has_species], 'geometry': [i[1] for i in has_species]})])

        # Estimate species counts by estimating asymptote of species-accumulation curve created when observation order is randomized
        # Final estimate is average over NUM_CURVEFITS estimates

        #count_estimate = None
        if len(observations) > 1:
            taxon_observations = list(observations.species)
            asymptotes = []
            tries = 0
            while len(asymptotes) < NUM_CURVEFITS:   # Different observation-orders give different results, so average over many
                tries += 1
                taxon_observations.sort(key=lambda x: random.random())                    # Randomize order of observations
                sac = []                                                            # Initialize species accumulation curve data
                for obs_count in range(1, len(taxon_observations)):                       # Go through observation list from beginning
                    sac.append(len(set(taxon_observations[:obs_count])))                  # and count unique species from start to index
                if len(sac) > 5 and tries <= 1000:          # Avoid letting infinite-species errors stop the process
                    try:
                        asymptotes.append(scipy.optimize.curve_fit(lambda x,a,b,c: -((a*np.exp(-b*x))+c), list(range(1, len(sac)+1)), sac)[0][2])
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
        return GeoDataFrame({'species_count': [count_estimate], 'geometry': [shapely.geometry.box(*bbox)]})
