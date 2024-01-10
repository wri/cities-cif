import xarray as xr
import ee
import numpy as np
from rasterio.enums import Resampling
from geocube.api.core import make_geocube
import pandas as pd
from shapely.geometry import CAP_STYLE, JOIN_STYLE
import geopandas as gpd
from sklearn.metrics import accuracy_score
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

from .layer import Layer, get_utm_zone_epsg
from .esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from .open_street_map import OpenStreetMap, OpenStreetMapClass
from .urban_land_use import UrbanLandUse
from .building_classifier import BuildingClassifier
from .built_up_height import BuiltUpHeight


class SmartCitiesLULC(Layer):
    def __init__(self, land_cover_class=None, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class

    def get_data(self, bbox):
        crs = get_utm_zone_epsg(bbox)

        # ESA reclass and upsample
        esa_world_cover = EsaWorldCover().get_data(bbox)

        reclass_map = {
            EsaWorldCoverClass.TREE_COVER.value: 1,
            EsaWorldCoverClass.SHRUBLAND.value: 1,
            EsaWorldCoverClass.GRASSLAND.value: 1,
            EsaWorldCoverClass.CROPLAND.value: 1,
            EsaWorldCoverClass.BUILT_UP.value: 2,
            EsaWorldCoverClass.BARE_OR_SPARSE_VEGETATION.value: 3,
            EsaWorldCoverClass.SNOW_AND_ICE.value: 4,
            EsaWorldCoverClass.PERMANENT_WATER_BODIES.value: 4,
            EsaWorldCoverClass.HERBACEOUS_WET_LAND.value: 4,
            EsaWorldCoverClass.MANGROVES.value: 4,
            EsaWorldCoverClass.MOSS_AND_LICHEN.value: 3
            # Add other mappings as needed
        }

        # Create an array of the same shape as esa_world_cover filled with default values
        reclassified_esa = np.full(esa_world_cover.shape, -1, dtype=np.int8)
        # Apply the mapping using advanced indexing
        for key, value in reclass_map.items():
            reclassified_esa[esa_world_cover == key] = value
        # Convert the NumPy array back to xarray.DataArray
        reclassified_esa = xr.DataArray(reclassified_esa, dims=esa_world_cover.dims, coords=esa_world_cover.coords)

        reclassified_esa = reclassified_esa.rio.write_crs(esa_world_cover.rio.crs, inplace=True)

        esa_1m = reclassified_esa.rio.reproject(
            dst_crs=crs,
            resolution=1,
            resampling=Resampling.nearest
        )

        def rasterize_osm(gdf, snap_to):
            raster = make_geocube(
                vector_data=gdf,
                measurements=["Value"],
                like=snap_to,
                fill=0
            ).Value

            return raster.rio.reproject_match(snap_to)


        # Open space
        open_space_osm = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE_HEAT).get_data(bbox).to_crs(crs).reset_index()
        open_space_osm['Value'] = np.int8(10)
        open_space_1m = rasterize_osm(open_space_osm, esa_1m)


        # Water
        water_osm = OpenStreetMap(osm_class=OpenStreetMapClass.WATER).get_data(bbox).to_crs(crs).reset_index()
        water_osm['Value'] = 20
        water_1m = rasterize_osm(water_osm, esa_1m)


        # Roads
        roads_osm = OpenStreetMap(osm_class=OpenStreetMapClass.ROAD).get_data(bbox).to_crs(crs).reset_index()
        roads_osm['lanes'] = pd.to_numeric(roads_osm['lanes'], errors='coerce')
        # Get the average number of lanes per highway class
        lanes = (roads_osm.drop(columns='geometry')
                 .groupby('highway')
                 # Calculate average and round up
                 .agg(avg_lanes=('lanes', lambda x: np.ceil(np.nanmean(x))))
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
        roads_osm['geometry'] = roads_osm.apply(lambda row: row['geometry'].buffer(
            row['lanes'] * 3.048,
            cap_style=CAP_STYLE.flat,
            join_style=JOIN_STYLE.mitre),
            axis=1
        )

        roads_1m = rasterize_osm(roads_osm, esa_1m)


        # TODO Building
        # Read ULU land cover, filter to city, select lulc band
        ulu_lulc = UrbanLandUse(band='lulc').get_data(bbox)
        ulu_roads = UrbanLandUse(band='road').get_data(bbox)
        # Create road mask of 50
        # Typical threshold for creating road mask 
        road_mask = ulu_roads >= 50
        ulu_lulc = ulu_lulc.where(~road_mask, 6)
        # 1-Non-residential: 0 (open space), 1 (non-res)
        # 2-Residential: 2 (Atomistic), 3 (Informal), 4 (Formal), 5 (Housing project)
        # 3-Roads: 6 (Roads)
        mapping = {0: 1, 1: 1, 2: 2, 3: 2, 4: 2, 5: 2, 6: 3}
        for from_val, to_val in mapping.items():
            ulu_lulc = ulu_lulc.where(ulu_lulc != from_val, to_val)
        
        # 1-Non-residential as default
        ulu_lulc_1m = ulu_lulc.rio.reproject(
            dst_crs=crs,
            shape=esa_1m.shape,
            resampling=Resampling.nearest,
            nodata=1
        )
        
        # Load ANBH layer
        anbh_data = BuiltUpHeight().get_data(bbox)

        anbh_1m = anbh_data.rio.reproject(
            dst_crs=crs,
            shape=esa_1m.shape,
            resampling=Resampling.nearest,
            nodata=0
        )

        building_osm = OpenStreetMap(osm_class=OpenStreetMapClass.BUILDING).get_data(bbox).to_crs(crs).reset_index()
        building_osm['Value'] = building_osm['osmid']
        building_osm_1m = rasterize_osm(building_osm, esa_1m)
        
        building_osm[['ULU', 'ANBH', 'Area_m']] = building_osm.apply(lambda row: BuildingClassifier().calc_majority_ULU_mean_ANBH_area(row, building_osm_1m, 'osmid', ulu_lulc_1m, anbh_1m), axis=1)

        # TODO
        # roof slope model
        # buildings sample classed LA for testing
        build_class = BuildingClassifier(geo_file = 'buildings-sample-classed_LA.geojson')
        clf = build_class.building_class_tree()

        plt.figure(figsize=(20, 10))
        plot_tree(clf, feature_names=['ULU', 'ANBH', 'Area_m'], class_names=['low','high'], filled=True)
        plt.show()

        # Predict and evaluate
        # y_pred = clf.predict(buildings_sample[['ULU', 'ANBH', 'Area_m']])
        # accuracy = accuracy_score(buildings_sample['Slope_encoded'], y_pred)
        # print(f"Accuracy: {accuracy}")

        building_osm['Slope'] = clf.predict(building_osm[['ULU', 'ANBH', 'Area_m']])


        # Parking
        parking_osm = OpenStreetMap(osm_class=OpenStreetMapClass.PARKING).get_data(bbox).to_crs(crs).reset_index()
        parking_osm['Value'] = 50
        parking_1m = rasterize_osm(parking_osm, esa_1m)

        # TODO
        # Combine rasters
        LULC = xr.concat([esa_1m, open_space_1m, roads_1m, water_1m, building_1m, parking_1m], dim='Value').max(dim='Value')
        # Reclass ESA water (4) to 20
        reclass_from = [1, 2, 3, 4, 10, 20, 30, 41, 42, 50]
        reclass_to = [1, 2, 3, 20, 10, 20, 30, 41, 42, 50]
        reclass_dict = dict(zip(reclass_from, reclass_to))
        LULC = LULC.copy(data=np.vectorize(reclass_dict.get)
                         (LULC.values, LULC.values))
        
        # TODO write tif
