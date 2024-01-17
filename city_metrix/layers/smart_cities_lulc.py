import xarray as xr
import numpy as np
import pandas as pd
from shapely.geometry import CAP_STYLE, JOIN_STYLE
from sklearn.metrics import accuracy_score
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
from xrspatial.classify import reclassify
import rioxarray

from .layer import Layer, get_utm_zone_epsg, create_fishnet_grid
from .open_street_map import OpenStreetMap, OpenStreetMapClass
from .building_classifier import BuildingClassifier


class SmartCitiesLULC(Layer):
    def __init__(self, land_cover_class=None, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class

    def get_data(self, bbox):
        crs = get_utm_zone_epsg(bbox)

        # TODO
        # roof slope model
        # buildings sample classed LA for testing
        buildings_sample = BuildingClassifier(geo_file = 'buildings-sample-classed_LA.geojson')
        clf = buildings_sample.building_class_tree()

        plt.figure(figsize=(20, 10))
        plot_tree(clf, feature_names=['ULU', 'ANBH', 'Area_m'], class_names=['low','high'], filled=True)
        plt.show()

        # Predict and evaluate
        # y_pred = clf.predict(buildings_sample[['ULU', 'ANBH', 'Area_m']])
        # accuracy = accuracy_score(buildings_sample['Slope_encoded'], y_pred)
        # print(f"Accuracy: {accuracy}")

        ZONES = create_fishnet_grid(*bbox, 0.1).reset_index()
        lulc_tiles = []

        for i in range(len(ZONES)):
            print(i)
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

            # TODO
            # Combine rasters
            datasets = [esa_1m, open_space_1m, roads_1m, water_1m, building_1m, parking_1m]
            # not all raster has 'time', concatenate without 'time' dimension
            aligned_datasets = [ds.drop_vars('time', errors='ignore') for ds in datasets]
            # use chunk 512x512
            aligned_datasets = [ds.chunk({'x': 512, 'y': 512}) for ds in aligned_datasets]
            lulc = xr.concat(aligned_datasets, dim='Value').max(dim='Value')

            # Reclass ESA water (4) to 20
            reclass_from = [1, 2, 3, 4, 10, 20, 30, 41, 42, 50]
            reclass_to = [1, 2, 3, 20, 10, 20, 30, 41, 42, 50]
            lulc = reclassify(lulc, bins=reclass_from, new_values=reclass_to).astype(np.int8)

            lulc_tiles.append(lulc)
        
        lulc_mosaiced = rioxarray.merge(lulc_tiles)

        return lulc_mosaiced

        # TODO write tif
