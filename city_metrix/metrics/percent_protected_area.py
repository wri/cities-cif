from geopandas import GeoDataFrame, GeoSeries
from pandas import Series
import ee
from city_metrix.layers import Layer, ProtectedAreas, EsaWorldCover
from city_metrix.layers.layer import get_image_collection


def percent_protected_area(
    zones: GeoDataFrame,
    status=['Inscribed', 'Adopted', 'Designated', 'Established'],
    status_year=2024,
    iucn_cat=['Ia', 'Ib', 'II', 'III', 'IV', 'V', 'VI', 'Not Applicable', 'Not Assigned', 'Not Reported']
) -> GeoSeries:

    world_cover = EsaWorldCover(year=2021)
    protect_area = ProtectedAreas(status=status, status_year=status_year, iucn_cat=iucn_cat)

    protect_area_in_world_cover = world_cover.mask(protect_area).groupby(zones).count()
    world_cover_counts = world_cover.groupby(zones).count()

    return 100 * protect_area_in_world_cover.fillna(0) / world_cover_counts
