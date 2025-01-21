from geopandas import GeoDataFrame, GeoSeries
from pandas import Series
import ee
from city_metrix.layers import Layer, ProtectedAreas
from city_metrix.layers.layer import get_image_collection


def percent_protected_area(zones: GeoDataFrame, status=['Inscribed', 'Adopted', 'Designated', 'Established'], status_year=2024, iucn_cat=['Ia', 'Ib', 'II', 'III', 'IV', 'V', 'VI', 'Not Applicable', 'Not Assigned', 'Not Reported']) -> GeoSeries:

    class PixelAreaLayer(Layer):
        def get_data(self, bbox):
            worldpop_pixelarea_img = ee.ImageCollection('ESA/WorldCover/v200').filterBounds(ee.Geometry.BBox(*bbox)).mosaic().pixelArea()
            data = get_image_collection(
                ee.ImageCollection(worldpop_pixelarea_img),
                bbox,
                10,
                "pixel areas"
            ).area
            return data

    pa_layer = ProtectedAreas(status=status, status_year=status_year, iucn_cat=iucn_cat)
    all_pa = pa_layer.get_data(zones.total_bounds)
    if len(all_pa) == 0:  # If no protected areas intersect with AOI
        return Series([0] * len(zones))
    area_layer = PixelAreaLayer()
    total_area = area_layer.groupby(zones).sum()

    pa_areas = []
    pa_union_geom = all_pa.unary_union
    for rownum in range(len(zones)):
        if zones.iloc[[rownum]].intersects(pa_union_geom)[rownum]: # Avoid error when no mask feature intersects with zone
            row_area = area_layer.mask(pa_layer).groupby(zones.iloc[[rownum]]).sum()[0]
        else:
            row_area = 0
        pa_areas.append(row_area)

    pa_area = Series(pa_areas)
    result = 100 * pa_area / total_area
    return result