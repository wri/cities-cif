import xarray as xr
import geopandas as gpd
from shapely.geometry import Point

from city_metrix.metrix_model import Layer, GeoExtent, validate_raster_resampling_method
from . import FabDEM
from .overture_buildings_w_height import OvertureBuildingsHeight
from ..constants import GTIFF_FILE_EXTENSION


DEFAULT_SPATIAL_RESOLUTION = 1
DEFAULT_RESAMPLING_METHOD = "bilinear"


# This value was determined from a large warehouse as a worst-case example at lon/lat -122.76768,45.63313
BUILDING_INCLUSION_BUFFER_METERS = 500


class OvertureBuildingsDSM(Layer):
    GEOSPATIAL_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["city"]
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        city: city id from https://sat-io.earthengine.app/view/ut-globus
    """

    def __init__(self, city="", **kwargs):
        super().__init__(**kwargs)
        self.city = city

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method: str = DEFAULT_RESAMPLING_METHOD):
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

        # Load buildings and sub-select to ones fully contained in buffered area
        raw_buildings_gdf = OvertureBuildingsHeight(self.city).get_data(buffered_utm_bbox)
        contained_buildings_gdf = (
            raw_buildings_gdf)[raw_buildings_gdf.geometry.apply(lambda x: x.within(buffered_utm_bbox.polygon))]

        fab_dem = FabDEM().get_data(buffered_utm_bbox, spatial_resolution=spatial_resolution, resampling_method=resampling_method)

        # Stack the DataArray into a 1-D table
        dem_stacked = fab_dem.stack(points=("y", "x"))
        # Build a GeoDataFrame of those points
        pts = gpd.GeoDataFrame(
            {"dem": dem_stacked.values},
            geometry=[
                Point(x, y)
                for x, y in zip(dem_stacked["x"].values, dem_stacked["y"].values)
            ],
            crs=fab_dem.crs,
        )

        # Spatial join: find which polygon (if any) each point falls in
        pts_joined = gpd.sjoin(
            pts,
            contained_buildings_gdf[["geometry", "height"]],
            how="left",
            predicate="within",
        )
        # Keep only the first match for each point
        pts_joined = pts_joined.loc[~pts_joined.index.duplicated(keep="first")]
        pts_joined["height"] = pts_joined["height"].fillna(0)

        # Compute the mode of 'dem' for each polygon drop NaNs so we ignore points not in any polygon
        elev_modes = (
            pts_joined.dropna(subset=["index_right"])
            .groupby("index_right")["dem"]
            .agg(lambda x: x.mode().iloc[0])
        )

        # Map the elevation mode back to each point (0 for outside any polygon)
        pts_joined["elev_mode"] = (
            pts_joined["index_right"].map(elev_modes).fillna(pts_joined["dem"])
         )

        #  Compute the new elevation: building + elevation‐mode
        pts_joined["new_elev"] = pts_joined["height"] + pts_joined["elev_mode"]

        # Reshape back into the fab_dem DataArray
        result_dem = xr.DataArray(
            pts_joined["new_elev"].values.reshape(fab_dem.shape),
            coords=fab_dem.coords,
            dims=fab_dem.dims,
            name=fab_dem.name,
        )
        result_dem.attrs = fab_dem.attrs.copy()

        # Clip to original bbox without buffer
        bbox_utm = bbox.as_utm_bbox()
        result_dem = result_dem.rio.clip_box(
            minx=bbox_utm.min_x, miny=bbox_utm.min_y,
            maxx=bbox_utm.max_x, maxy=bbox_utm.max_y,
            crs=result_dem.rio.crs
        )

        return result_dem
