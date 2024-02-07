import xarray as xr
import numpy as np
import pandas as pd
from shapely.geometry import CAP_STYLE, JOIN_STYLE
from sklearn.metrics import accuracy_score
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
from xrspatial.classify import reclassify
import rioxarray
import psutil
import warnings
warnings.filterwarnings('ignore',category=UserWarning)

from .layer import Layer, get_utm_zone_epsg, create_fishnet_grid
from .open_street_map import OpenStreetMap, OpenStreetMapClass
from .building_classifier import BuildingClassifier


from cartoframes.auth import set_default_credentials
from cartoframes import read_carto
def read_carto_city(city_name: str):
    set_default_credentials(username='wri-cities', api_key='default_public')
    city_df = read_carto(f"SELECT * FROM smart_surfaces_urban_areas WHERE name10 = '{city_name}'")
    return city_df

columbia = read_carto_city('Columbia_SC')
bbox = columbia.reset_index().total_bounds

class SmartCitiesLULC(Layer):
    def __init__(self, land_cover_class=None, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class

    def get_data(self, bbox):
        crs = get_utm_zone_epsg(bbox)

        # TODO: roof slope model
        # buildings sample classed LA for testing
        buildings_sample = BuildingClassifier(geo_file = 'buildings-sample-classed_LA.geojson')
        clf = buildings_sample.building_class_tree()

        ZONES = create_fishnet_grid(*bbox, 0.1).reset_index()
        # Initialize a dictionary to hold counts of unique lulc types
        unique_lulc_counts = {}
        total_count = 0

        for i in range(len(ZONES)):
            process = psutil.Process()
            print(f'tile: {i}, memory: {process.memory_info().rss/10 ** 9} GB')

            bbox = ZONES.iloc[[i]].total_bounds

            esa_1m = BuildingClassifier().get_data_esa_reclass(bbox, crs)

            # Open space
            open_space_osm = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE_HEAT).get_data(bbox).to_crs(crs).reset_index()
            open_space_osm['Value'] = np.int8(10)
            open_space_1m = BuildingClassifier().rasterize_polygon(open_space_osm, esa_1m)


            # Water
            water_osm = OpenStreetMap(osm_class=OpenStreetMapClass.WATER).get_data(bbox).to_crs(crs).reset_index()
            water_osm['Value'] = np.int8(20)
            water_1m = BuildingClassifier().rasterize_polygon(water_osm, esa_1m)


            # Roads
            roads_osm = OpenStreetMap(osm_class=OpenStreetMapClass.ROAD).get_data(bbox).to_crs(crs).reset_index()
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

            roads_1m = BuildingClassifier().rasterize_polygon(roads_osm, esa_1m)


            # Building
            ulu_lulc_1m = BuildingClassifier().get_data_ulu(bbox, crs, esa_1m)
            anbh_1m = BuildingClassifier().get_data_anbh(bbox, crs, esa_1m)
            
            building_osm = OpenStreetMap(osm_class=OpenStreetMapClass.BUILDING).get_data(bbox).to_crs(crs).reset_index()
            building_osm['Value'] = building_osm['osmid']
            building_osm_1m = BuildingClassifier().rasterize_polygon(building_osm, esa_1m)
            building_osm[['ULU', 'ANBH', 'Area_m']] = building_osm.apply(lambda row: BuildingClassifier().extract_features(row, building_osm_1m, 'osmid', ulu_lulc_1m, anbh_1m), axis=1)

            building_osm['Value'] = clf.predict(building_osm[['ULU', 'ANBH', 'Area_m']])
            building_1m = BuildingClassifier().rasterize_polygon(building_osm, esa_1m)


            # Parking
            parking_osm = OpenStreetMap(osm_class=OpenStreetMapClass.PARKING).get_data(bbox).to_crs(crs).reset_index()
            parking_osm['Value'] = np.int8(50)
            parking_1m = BuildingClassifier().rasterize_polygon(parking_osm, esa_1m)

            # osm_df = pd.concat([open_space_osm[['geometry','Value']], water_osm[['geometry','Value']], roads_osm[['geometry','Value']], building_osm[['geometry','Value']], parking_osm[['geometry','Value']]], axis=0)
            # osm_1m = BuildingClassifier().rasterize_polygon(osm_df, esa_1m)

            # Combine rasters
            datasets = [esa_1m, open_space_1m, roads_1m, water_1m, building_1m, parking_1m]
            # datasets = [esa_1m, osm_1m]
            # not all raster has 'time', concatenate without 'time' dimension
            aligned_datasets = [ds.drop_vars('time', errors='ignore') for ds in datasets]
            # use chunk 512x512
            aligned_datasets = [ds.chunk({'x': 512, 'y': 512}) for ds in aligned_datasets]
            lulc = xr.concat(aligned_datasets, dim='Value').max(dim='Value')

            # Reclass ESA water (4) to 20
            reclass_from = [1, 2, 3, 4, 10, 20, 30, 41, 42, 50]
            reclass_to = [1, 2, 3, 20, 10, 20, 30, 41, 42, 50]
            lulc = reclassify(lulc, bins=reclass_from, new_values=reclass_to).astype(np.int8)

            # Flatten the array as a 1D array
            flattened_array = lulc.values.flatten()
            # Count occurrences of each unique value
            values, counts = np.unique(flattened_array, return_counts=True)
            # Update the dictionary with counts, summing counts for existing keys (unique lulc)
            for value, count in zip(values, counts):
                if value in unique_lulc_counts:
                    unique_lulc_counts[value] += count
                else:
                    unique_lulc_counts[value] = count
            # Update total pixel count
            total_count += flattened_array.size
    
        lulc_area_pct = {key: value/total_count for key, value in unique_lulc_counts.items()}

        return lulc_area_pct
