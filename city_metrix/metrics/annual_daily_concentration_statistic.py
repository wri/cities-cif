from geopandas import GeoDataFrame, GeoSeries
import numpy as np
from affine import Affine

from city_metrix.layers import Layer, Cams, CamsSpecies
from city_metrix.layers.layer_geometry import GeoExtent


class CamsAnnual(Cams):
    def __init__(self, start_date="2023-01-01", end_date="2023-12-31", species=[], statname='mean', **kwargs):
        super().__init__(start_date=start_date, end_date=end_date, species=species, **kwargs)
        self.statname = statname

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None):
        cams = super().get_data(bbox)
        cams_daily = cams.resample({'valid_time': '1D'}).mean()

        if self.statname == 'mean':
            cams_annual = cams_daily.resample({'valid_time': '1Y'}).mean().squeeze("valid_time")
        elif self.statname == 'max':
            cams_annual = cams_daily.resample({'valid_time': '1Y'}).max().squeeze("valid_time")
        else:
            raise Exception(f'Unsupported stat type {self.statname}')
        
        cams_annual = cams_annual.transpose('variable', 'y', 'x')
        
        min_lon, min_lat, max_lon, max_lat = bbox.as_geographic_bbox().bounds
        transform = Affine.translation(min_lon, max_lat) * Affine.scale(0.25, -0.25)
        cams_annual.rio.write_transform(transform, inplace=True)
        cams_annual.rio.write_crs("EPSG:4326", inplace=True)
        cams_annual = cams_annual.rio.reproject(bbox.as_utm_bbox().crs)

        # var_names = cams_annual.coords["variable"].values
        # values = cams_annual.values[:, 0, 0]
        # var_dict = dict(zip(var_names, values))
    
        return cams_annual


def annual_daily_concentration_statistic(
    zones: GeoDataFrame,
    species=[],
    statname='mean'  # statname is one of 'mean', 'max'
) -> GeoSeries:
    
    bbox = GeoExtent(zones.total_bounds, zones.crs.srs)
    cams_annual = CamsAnnual(species=species, statname=statname).get_data(bbox)

    if statname == 'mean':
        annual_daily_concentration = cams_annual.groupby(zones).mean()
    elif statname == 'max':
        annual_daily_concentration = cams_annual.groupby(zones).max()
    else:
        raise Exception(f'Unsupported stat type {statname}')

    return annual_daily_concentration
