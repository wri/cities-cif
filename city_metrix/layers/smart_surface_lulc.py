import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import CAP_STYLE, JOIN_STYLE
from shapely.geometry import box
import psutil
from exactextract import exact_extract
import pickle
import importlib.resources as pkg_resources
import warnings
warnings.filterwarnings('ignore',category=UserWarning)

from .layer import Layer, get_utm_zone_epsg, create_fishnet_grid, MAX_TILE_SIZE
from .open_street_map import OpenStreetMap, OpenStreetMapClass
from .overture_buildings import OvertureBuildings
from ..models.building_classifier.building_classifier import BuildingClassifier


class SmartSurfaceLULC(Layer):
    def __init__(self, land_cover_class=None, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class

    def get_data(self, bbox):
        crs = get_utm_zone_epsg(bbox)

        # load building roof slope classifier
        with pkg_resources.files('city_metrix.models.building_classifier').joinpath('building_classifier.pkl').open('rb') as f:
            clf = pickle.load(f)

        # ESA world cover
        esa_1m = BuildingClassifier().get_data_esa_reclass(bbox, crs)

        # Open space
        open_space_osm = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE_HEAT).get_data(bbox).to_crs(crs).reset_index()
        open_space_osm['Value'] = np.int8(10)


        # Water
        water_osm = OpenStreetMap(osm_class=OpenStreetMapClass.WATER).get_data(bbox).to_crs(crs).reset_index()
        water_osm['Value'] = np.int8(20)


        # Roads
        roads_osm = OpenStreetMap(osm_class=OpenStreetMapClass.ROAD).get_data(bbox).to_crs(crs).reset_index()
        if len(roads_osm) > 0:
            roads_osm['lanes'] = pd.to_numeric(roads_osm['lanes'], errors='coerce')
            # Get the average number of lanes per highway class
            lanes = (roads_osm.drop(columns='geometry')
                    .groupby('highway')
                    # Calculate average and round up
                    .agg(avg_lanes=('lanes', lambda x: np.ceil(np.nanmean(x)) if not np.isnan(x).all() else np.NaN))
                    )
            # Handle NaN values in avg_lanes
            lanes['avg_lanes'] = lanes['avg_lanes'].fillna(2)

            # Fill lanes with avg lane value when missing
            roads_osm = roads_osm.merge(lanes, on='highway', how='left')
            roads_osm['lanes'] = roads_osm['lanes'].fillna(roads_osm['avg_lanes'])

            # Add value field (30)
            roads_osm['Value'] = np.int8(30)

            # Buffer roads by lanes * 10 ft (3.048 m)
            # https://nacto.org/publication/urban-street-design-guide/street-design-elements/lane-width/#:~:text=wider%20lane%20widths.-,Lane%20widths%20of%2010%20feet%20are%20appropriate%20in%20urban%20areas,be%20used%20in%20each%20direction
            # cap is flat to the terminus of the road
            # join style is mitred so intersections are squared
            roads_osm['geometry'] = roads_osm.apply(lambda row: row['geometry'].buffer(
                row['lanes'] * 3.048,
                cap_style=CAP_STYLE.flat,
                join_style=JOIN_STYLE.mitre),
                axis=1
            )
        else:
            # Add value field (30)
            roads_osm['Value'] = np.int8(30)


        # Building
        ulu_lulc_1m = BuildingClassifier().get_data_ulu(bbox, crs, esa_1m)
        anbh_1m = BuildingClassifier().get_data_anbh(bbox, esa_1m)
        # get building features
        buildings = OvertureBuildings().get_data(bbox).to_crs(crs)
        # extract ULU, ANBH, and Area_m
        buildings['ULU'] = exact_extract(ulu_lulc_1m, buildings, ["majority"], output='pandas')['majority']
        buildings['ANBH'] = exact_extract(anbh_1m, buildings, ["mean"], output='pandas')['mean']
        buildings['Area_m'] = buildings.geometry.area
        # classify buildings
        unclassed_buildings = buildings[buildings['ULU'] == 0]
        classed_buildings = buildings[buildings['ULU'] != 0]
        
        if len(classed_buildings) > 0:
            classed_buildings['Value'] = clf.predict(classed_buildings[['ULU', 'ANBH', 'Area_m']])
            # Define conditions and choices
            case_when_class = [
                # "residential" & "high"
                (classed_buildings['Value'] == 40) & (classed_buildings['ULU'] == 2),
                # "non-residential" & "high"
                (classed_buildings['Value'] == 40) & (classed_buildings['ULU'] == 1),
                # "residential" & "low"
                (classed_buildings['Value'] == 42) & (classed_buildings['ULU'] == 2),
                # "non-residential" & "low"
                (classed_buildings['Value'] == 42) & (classed_buildings['ULU'] == 1)
            ]
            case_when_value = [40, 41, 42, 43]
            classed_buildings['Value'] = np.select(case_when_class, case_when_value, default=44)
            unclassed_buildings['Value'] = 44
            buildings = pd.concat([classed_buildings, unclassed_buildings])
        else:
            buildings['Value'] = 44


        # Parking
        parking_osm = OpenStreetMap(osm_class=OpenStreetMapClass.PARKING).get_data(bbox).to_crs(crs).reset_index()
        parking_osm['Value'] = np.int8(50)


        # combine features: open space, water, road, building, parking
        feature_df = pd.concat([open_space_osm[['geometry','Value']], water_osm[['geometry','Value']], roads_osm[['geometry','Value']], buildings[['geometry','Value']], parking_osm[['geometry','Value']]], axis=0)
        feature_1m = BuildingClassifier().rasterize_polygon(feature_df, esa_1m)

        # Combine rasters
        datasets = [esa_1m, feature_1m]
        # not all raster has 'time', concatenate without 'time' dimension
        aligned_datasets = [ds.drop_vars('time', errors='ignore') for ds in datasets]
        # use chunk 512x512
        aligned_datasets = [ds.chunk({'x': 512, 'y': 512}) for ds in aligned_datasets]
        lulc = xr.concat(aligned_datasets, dim='Value').max(dim='Value')
        lulc = lulc.compute()

        return lulc
