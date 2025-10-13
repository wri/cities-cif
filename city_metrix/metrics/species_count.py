import random
import scipy
import numpy as np
import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION, WGS_CRS
from city_metrix.layers import SpeciesObservations, GBIFTaxonClass, EsaWorldCover, EsaWorldCoverClass
from city_metrix.metrix_model import Metric, GeoZone, GeoExtent

NUM_CURVEFITS = 200


def _species_count_estimate(all_observations, zone):
    # Estimate species counts by estimating asymptote of species-accumulation curve created when observation order is randomized
    # Final estimate is average over NUM_CURVEFITS estimates

    observations = all_observations.loc[all_observations.intersects(zone.geometry.iloc[0])]

    if len(observations) >= 10:
        taxon_observations = list(observations.species)
        asymptotes = []
        tries = 0
        # Different observation-orders give different results, so average over many
        while (len(asymptotes) < NUM_CURVEFITS):
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
                break
        if -1 in asymptotes:
            count_estimate = np.nan
        else:
            count_estimate = -round(np.mean(asymptotes))

    else:
        count_estimate = np.nan

    return count_estimate

class _NumberSpecies(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["taxon", "start_year", "end_year"]


    def __init__(
        self, **kwargs
    ):
        super().__init__(**kwargs)
        self.taxon = None
        self.start_year = None
        self.end_year = None
        self.mask_layer = None
        self.unit = 'species'


    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:

        bbox = GeoExtent(geo_zone)
        utm_crs = bbox.as_utm_bbox().crs
        city_id = geo_zone.city_id
        geo_level = ['adminbound', 'urbextbound'][int(geo_zone.aoi_id=='urban_extent')]
        speciesobservations_obj = SpeciesObservations(city_id=city_id, geo_level=geo_level, taxon=self.taxon, start_year=self.start_year, end_year=self.end_year, mask_layer=self.mask_layer)
        species_observations = speciesobservations_obj.get_data(bbox=bbox)

        zones_utm = geo_zone.zones.to_crs(utm_crs)
        results = []
        for rownum in range(len(zones_utm)):
            print(f'{city_id} {self.taxon.value["taxon"]} {rownum}/{len(zones_utm)}')
            results.append(_species_count_estimate(species_observations, zones_utm.iloc[[rownum]]))


        result = pd.DataFrame({'zone': zones_utm.index, 'value': results})

        return result


class BirdRichness__Species(_NumberSpecies):
    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.taxon = GBIFTaxonClass.BIRDS
        self.start_year = start_year
        self.end_year = end_year


class ArthropodRichness__Species(_NumberSpecies):
    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.taxon = GBIFTaxonClass.ARTHROPODS
        self.start_year = start_year
        self.end_year = end_year


class VascularPlantRichness__Species(_NumberSpecies):
    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.taxon = GBIFTaxonClass.VASCULAR_PLANTS
        self.start_year = start_year
        self.end_year = end_year


class BirdRichnessInBuiltUpArea__Species(_NumberSpecies):
    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.mask_layer = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        self.taxon = GBIFTaxonClass.BIRDS
        self.start_year = start_year
        self.end_year = end_year
