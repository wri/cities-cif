import xarray as xr

from .layer import Layer
from .esa_world_cover import EsaWorldCover, EsaWorldCoverClass
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

        # Create an array of the same shape as esa_world_cover filled with default values
        reclassified_data = np.full(esa_world_cover.shape, -1, dtype=np.int8)
        # Apply the mapping using advanced indexing
        for key, value in reclass_map.items():
            reclassified_data[esa_world_cover == key] = value
        # Convert the NumPy array back to xarray.DataArray
        reclassified_data = xr.DataArray(reclassified_data, dims=esa_world_cover.dims, coords=esa_world_cover.coords)

        reclassified_data = reclassified_data.rio.write_crs(esa_world_cover.rio.crs, inplace=True)

        return reclassified_data
