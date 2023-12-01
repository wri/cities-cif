import xarray as xr

from .layer import Layer
from .. import EsaWorldCover, EsaWorldCoverClass
import numpy as np


class NaturalAreas(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox):
        esa_world_cover = EsaWorldCover().get_data(bbox)
        reclass_map = {
            EsaWorldCoverClass.TREE_COVER.value: 1,
            EsaWorldCoverClass.SHRUBLAND.value: 1,
            EsaWorldCoverClass.GRASSLAND.value: 1,
            EsaWorldCoverClass.CROPLAND.value: 0,
            EsaWorldCoverClass.BUILT_UP.value: 0,
            EsaWorldCoverClass.BARE_OR_SPARSE_VEGETATION.value: 0,
            EsaWorldCoverClass.SNOW_AND_ICE.value: 0,
            EsaWorldCoverClass.PERMANENT_WATER_BODIES.value: 0,
            EsaWorldCoverClass.HERBACEOUS_WET_LAND.value: 1,
            EsaWorldCoverClass.MANGROVES.value: 1,
            EsaWorldCoverClass.MOSS_AND_LICHEN.value: 1
            # Add other mappings as needed
        }

        reclassified_data = xr.apply_ufunc(
            np.vectorize(lambda x: reclass_map.get(x, x)),
            esa_world_cover,
            vectorize=True
        )

        return reclassified_data
