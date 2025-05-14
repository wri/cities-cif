import xarray as xr
import geopandas as gpd
from shapely.geometry import Point

from city_metrix.metrix_model import Layer, GeoExtent, validate_raster_resampling_method
from .nasa_dem import NasaDEM
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

        # Minimize the probability that buildings will bridge tile boundaries and therefor sample elevations for
        # only part of the full footprint by 1. buffering out the selection area, 2. filtering to contained buildings,
        # and 3. clipping back to the original selection area
        building_buffer = BUILDING_INCLUSION_BUFFER_METERS
        buffered_utm_bbox = bbox.buffer_utm_bbox(building_buffer)

        # Load buildings and sub-select to ones fully contained in buffered area
        raw_buildings_gdf = OvertureBuildingsHeight(self.city).get_data(buffered_utm_bbox)
        contained_buildings_gdf = (
            raw_buildings_gdf)[raw_buildings_gdf.geometry.apply(lambda x: x.within(buffered_utm_bbox.polygon))]

        DEM = NasaDEM().get_data(buffered_utm_bbox, spatial_resolution=spatial_resolution, resampling_method=resampling_method)

        # Stack the DataArray into a 1-D table
        DEM_stacked = DEM.stack(points=("x", "y"))
        # Build a GeoDataFrame of those points
        pts = gpd.GeoDataFrame(
            {"dem": DEM_stacked.values},
            geometry=[
                Point(x, y)
                for x, y in zip(DEM_stacked["x"].values, DEM_stacked["y"].values)
            ],
            crs=DEM.crs,
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

        # Reshape back into the DEM DataArray
        DEM_updated = xr.DataArray(
            pts_joined["new_elev"].values.reshape(DEM.shape),
            coords=DEM.coords,
            dims=DEM.dims,
            name=DEM.name,
        )

        # Clip back to the original AOI
        west, south, east, north = bbox.as_utm_bbox().bounds
        longitude_range = slice(west, east)
        latitude_range = slice(south, north)
        clipped_data = DEM_updated.sel(x=longitude_range, y=latitude_range)

        return clipped_data
