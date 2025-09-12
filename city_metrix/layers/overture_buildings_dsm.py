# optimized batch with max footprint
# overture_buildings_dsm_without_gpu5
import xarray as xr
import numpy as np
from rasterio.features import rasterize
from city_metrix.metrix_model import Layer, GeoExtent, validate_raster_resampling_method
from . import FabDEM
from ..constants import GTIFF_FILE_EXTENSION
from .overture_buildings_w_height import OvertureBuildingsHeight
from ..metrix_dao import extract_bbox_aoi
from ..ut_globus_city_handler.ut_globus_city_handler import search_for_ut_globus_city_by_contained_polygon

DEFAULT_SPATIAL_RESOLUTION = 1
DEFAULT_RESAMPLING_METHOD = 'bilinear'

# This value was determined from a large warehouse as a worst-case example at lon/lat -122.76768,45.63313
BUILDING_INCLUSION_BUFFER_METERS = 500

class OvertureBuildingsDSM(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["city"]
    PROCESSING_TILE_SIDE_M = 5000
    # time to first tile = 1 min for 1k tile
    # tile-size testing for Teresina
    # 0. 5k =  51:41 min (run mode)
    # 1. 10k =  min (run mode) -- memory issue
    """
    Attributes:
        city: city id from https://sat-io.earthengine.app/view/ut-globus
    """
    def __init__(self, city="", **kwargs):
        super().__init__(**kwargs)
        self.city = city

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method:str=DEFAULT_RESAMPLING_METHOD):
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        # Minimize the probability that buildings will bridge tile boundaries and thereby sample elevations for
        # only part of the full footprint by: 1. buffering out AOI, 2. filtering buildings to contained buildings,
        # 3. masking buffered DEM by footprint and determining elevation of footprint, 4. masking unbuffered DEM
        # with footprint, 5. add footprint elevation to unbuffered DEM.
        # Population of the unbuffered DEM ensures that AOI is correct.
        building_buffer = BUILDING_INCLUSION_BUFFER_METERS
        buffered_utm_bbox = bbox.buffer_utm_bbox(building_buffer)

        if self.city == '' or self.city is None:
            bbox_polygon = bbox.as_geographic_bbox().polygon
            self.city = search_for_ut_globus_city_by_contained_polygon(bbox_polygon)

        # Load buildings and sub-select to ones fully contained in buffered area
        buffered_buildings_gdf = OvertureBuildingsHeight(self.city).get_data(bbox=buffered_utm_bbox)

        buffered_dem = FabDEM().get_data(buffered_utm_bbox, spatial_resolution=1, resampling_method='bilinear')

        # Ensure CRS matches
        buffered_buildings_gdf = buffered_buildings_gdf.to_crs(buffered_dem.rio.crs)

        # Unique ID per building
        buffered_buildings_gdf["b_id"] = np.arange(len(buffered_buildings_gdf))

        # === RASTERIZE BUILDING IDs ===
        print("Rasterizing building IDs...")
        building_id_raster = rasterize(
            [(geom, b_id) for geom, b_id in zip(buffered_buildings_gdf.geometry, buffered_buildings_gdf["b_id"])],
            out_shape=buffered_dem.shape,
            transform=buffered_dem.rio.transform(),
            fill=-1,
            dtype="int32"
        )

        # Convert to DataArray
        building_id_da = xr.DataArray(
            building_id_raster,
            dims=buffered_dem.dims,
            coords=buffered_dem.coords
        )

        # Mask DEM where buildings exist
        masked_dem = buffered_dem.where(building_id_da != -1)

        # Group by building ID and compute max elevation
        max_elevs = masked_dem.groupby(building_id_da).max()

        # Add building height
        buffered_buildings_gdf["max_elev"] = buffered_buildings_gdf["b_id"].map(max_elevs.to_series())
        buffered_buildings_gdf["final_elev"] = buffered_buildings_gdf["max_elev"] + buffered_buildings_gdf["height"]

        # Rasterize final elevation
        final_shapes = [(geom, elev) for geom, elev in zip(buffered_buildings_gdf.geometry, buffered_buildings_gdf["final_elev"])]
        building_elev_raster = rasterize(
            final_shapes,
            out_shape=buffered_dem.shape,
            transform=buffered_dem.rio.transform(),
            fill=0,
            dtype="float32"
        )

        # Convert to DataArray
        building_da = xr.DataArray(
            building_elev_raster,
            dims=buffered_dem.dims,
            coords=buffered_dem.coords
        )

        # Merge with DEM to create DSM
        dsm_da = buffered_dem.where(building_da == 0, building_da)
        result_dsm = dsm_da.rio.write_crs(buffered_dem.rio.crs)
        result_dsm.attrs["crs"] = buffered_dem.rio.crs

        # Trim back to original AOI
        result_dsm = extract_bbox_aoi(result_dsm, bbox)

        return result_dsm

