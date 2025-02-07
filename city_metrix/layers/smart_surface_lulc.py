import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import CAP_STYLE, JOIN_STYLE
from shapely.geometry import box
from exactextract import exact_extract
from geocube.api.core import make_geocube
import warnings
from rasterio.enums import Resampling
from xrspatial.classify import reclassify

from .layer_geometry import GeoExtent

warnings.filterwarnings('ignore', category=UserWarning)

from .layer import Layer
from .esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from .open_street_map import OpenStreetMap, OpenStreetMapClass
from .average_net_building_height import AverageNetBuildingHeight
from .urban_land_use import UrbanLandUse
from .overture_buildings import OvertureBuildings

DEFAULT_SPATIAL_RESOLUTION = 10

class SmartSurfaceLULC(Layer):
    def __init__(self, land_cover_class=None, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        utm_crs = bbox.as_utm_bbox().crs

        # ESA world cover
        esa_world_cover = EsaWorldCover(year=2021).get_data(bbox, spatial_resolution = spatial_resolution)
        # ESA reclass and upsample
        def get_data_esa_reclass(esa_world_cover):
            reclass_map = {
                EsaWorldCoverClass.TREE_COVER.value: 1,
                EsaWorldCoverClass.SHRUBLAND.value: 1,
                EsaWorldCoverClass.GRASSLAND.value: 1,
                EsaWorldCoverClass.CROPLAND.value: 1,
                EsaWorldCoverClass.BUILT_UP.value: 2,
                EsaWorldCoverClass.BARE_OR_SPARSE_VEGETATION.value: 3,
                EsaWorldCoverClass.SNOW_AND_ICE.value: 20,
                EsaWorldCoverClass.PERMANENT_WATER_BODIES.value: 20,
                EsaWorldCoverClass.HERBACEOUS_WET_LAND.value: 20,
                EsaWorldCoverClass.MANGROVES.value: 20,
                EsaWorldCoverClass.MOSS_AND_LICHEN.value: 3
            }

            # Perform the reclassification
            reclassified_esa = reclassify(
                esa_world_cover,
                bins=list(reclass_map.keys()),
                new_values=list(reclass_map.values())
            )

            esa_1m = reclassified_esa.rio.reproject(
                dst_crs=utm_crs,
                resolution=1,
                resampling=Resampling.nearest
            )

            return esa_1m

        esa_1m = get_data_esa_reclass(esa_world_cover)


        # Open space
        open_space_osm = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE_HEAT).get_data(bbox).reset_index()
        open_space_osm['Value'] = 10


        # Water
        water_osm = OpenStreetMap(osm_class=OpenStreetMapClass.WATER).get_data(bbox).reset_index()
        water_osm['Value'] = 20


        # Roads
        roads_osm = OpenStreetMap(osm_class=OpenStreetMapClass.ROAD).get_data(bbox).reset_index()
        if len(roads_osm) > 0:
            roads_osm['lanes'] = pd.to_numeric(roads_osm['lanes'], errors='coerce')
            # Get the average number of lanes per highway class
            lanes = (roads_osm
                     .drop(columns='geometry')
                     .groupby('highway')
                     # Calculate average and round up
                     .agg(avg_lanes=('lanes', lambda x: np.ceil(np.nanmean(x)) if not np.isnan(x).all() else np.nan))
                     )
            # Handle NaN values in avg_lanes
            lanes['avg_lanes'] = lanes['avg_lanes'].fillna(2)

            # Fill lanes with avg lane value when missing
            roads_osm = roads_osm.merge(lanes, on='highway', how='left')
            roads_osm['lanes'] = roads_osm['lanes'].fillna(roads_osm['avg_lanes'])

            # Add value field (30)
            roads_osm['Value'] = 30

            # Buffer roads by lanes * 10 ft (3.048 m)
            # https://nacto.org/publication/urban-street-design-guide/street-design-elements/lane-width/#:~:text=wider%20lane%20widths.-,Lane%20widths%20of%2010%20feet%20are%20appropriate%20in%20urban%20areas,be%20used%20in%20each%20direction
            # cap is flat to the terminus of the road
            # join style is mitred so intersections are squared
            roads_osm['geometry'] = (
                roads_osm
                .apply(
                    lambda row: row['geometry']
                    .buffer(
                        row['lanes'] * 3.048 / 2,
                        cap_style=CAP_STYLE.flat,
                        join_style=JOIN_STYLE.mitre
                    ),axis=1
                )
            )
        else:
            # Add value field (30)
            roads_osm['Value'] = 30


        # Building
        # Read ULU land cover
        ulu_lulc = UrbanLandUse().get_data(bbox)
        # Reclassify ULU
        # 0-Unclassified: 0 (open space)
        # 1-Non-residential: 1 (non-res)
        # 2-Residential: 2 (Atomistic), 3 (Informal), 4 (Formal), 5 (Housing project)
        mapping = {0: 0, 1: 1, 2: 2, 3: 2, 4: 2, 5: 2}
        for from_val, to_val in mapping.items():
            ulu_lulc = ulu_lulc.where(ulu_lulc != from_val, to_val)
        ulu_lulc_1m = ulu_lulc.rio.reproject(
            dst_crs=utm_crs,
            shape=esa_1m.shape,
            resampling=Resampling.nearest,
            nodata=0
        )

        # Load ANBH layer
        anbh_data = AverageNetBuildingHeight().get_data(bbox)
        anbh_1m = anbh_data.rio.reproject_match(
            match_data_array=esa_1m,
            resampling=Resampling.nearest,
            nodata=0
        )

        # get building features
        buildings = OvertureBuildings().get_data(bbox)
        # extract ULU, ANBH, and Area_m
        buildings['ULU'] = exact_extract(ulu_lulc_1m, buildings, ["majority"], output='pandas')['majority']
        buildings['ANBH'] = exact_extract(anbh_1m, buildings, ["mean"], output='pandas')['mean']
        buildings['Area_m'] = buildings.geometry.area

        # function to classify each building
        def classify_building(building):
            # Unclassified ULU
            if building['ULU'] == 0:
                # large building = low slope
                if building['Area_m'] >= 1034:
                    return 46
                # small building & high ANBH = low slope
                elif (building['Area_m'] < 1034) & (building['ANBH'] >= 11):
                    return 46
                # small building & low ANBH = high slope
                elif (building['Area_m'] < 1034) & (building['ANBH'] < 11):
                    return 43
                else:
                    return 40

            # Residential ULU
            # residential = high slope
            elif building['ULU'] == 2:
                return 41

            # Non-residential
            elif building['ULU'] == 1:
                # small building & high ANBH = low slope
                if (building['Area_m'] < 1034) & (building['ANBH'] >= 11):
                    return 45
                # large building = low slope
                elif building['Area_m'] >= 1034:
                    return 45
                # small building & low ANBH = high slope
                elif (building['Area_m'] < 1034) & (building['ANBH'] < 11):
                    return 42
                else:
                    return 40

            # Default value
            else:
                return 40

        # classify buildings
        if len(buildings) > 0:
            buildings['Value'] = buildings.apply(classify_building, axis=1)

        # Parking
        parking_osm = OpenStreetMap(osm_class=OpenStreetMapClass.PARKING).get_data(bbox).reset_index()
        parking_osm['Value'] = 50

        # combine features: open space, water, road, building, parking
        feature_df = pd.concat(
            [open_space_osm[['geometry', 'Value']],
             water_osm[['geometry', 'Value']],
             roads_osm[['geometry', 'Value']],
             buildings[['geometry', 'Value']],
             parking_osm[['geometry', 'Value']]
             ], axis=0
        )

        # rasterize
        if feature_df.empty:
            feature_1m = xr.zeros_like(esa_1m)
        else:
            feature_1m = make_geocube(
                vector_data=feature_df,
                measurements=["Value"],
                like=esa_1m,
                fill=0
            ).Value
            feature_1m = feature_1m.rio.reproject_match(esa_1m)

        # Combine rasters
        datasets = [esa_1m, feature_1m]
        # not all raster has 'time', concatenate without 'time' dimension
        aligned_datasets = [ds.drop_vars('time', errors='ignore') for ds in datasets]
        # use chunk 512x512
        aligned_datasets = [ds.chunk({'x': 512, 'y': 512}) for ds in aligned_datasets]
        lulc = xr.concat(aligned_datasets, dim='Value').max(dim='Value').compute()

        return lulc