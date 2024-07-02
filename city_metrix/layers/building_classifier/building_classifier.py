import xarray as xr
import ee
import numpy as np
from rasterio.enums import Resampling
from geocube.api.core import make_geocube
import pandas as pd
import geopandas as gpd
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
from xrspatial.classify import reclassify
from exactextract import exact_extract
import pickle

from ..layer import Layer, get_utm_zone_epsg
from ..esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from ..urban_land_use import UrbanLandUse
from ..average_net_building_height import AverageNetBuildingHeight
from ..open_street_map import OpenStreetMap, OpenStreetMapClass
from ..open_buildings import OpenBuildings


class BuildingClassifier(Layer):
    def __init__(self, geo_file='V2-building-class-data.geojson', **kwargs):
        super().__init__(**kwargs)
        self.geo_file = geo_file

    def get_data_geo(self):
        buildings_sample = gpd.read_file(self.geo_file)
        buildings_sample.to_crs(epsg=4326, inplace=True)

        return buildings_sample

    def get_data_esa_reclass(self, bbox, crs):
        # ESA reclass and upsample
        esa_world_cover = EsaWorldCover(year=2021).get_data(bbox)

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
        reclassified_esa = reclassify(esa_world_cover, bins=list(reclass_map.keys()), new_values=list(reclass_map.values()))

        # Convert to int8 and chunk the data for Dask processing
        reclassified_esa = reclassified_esa.astype(np.int8).chunk({'x': 512, 'y': 512})

        reclassified_esa = reclassified_esa.rio.write_crs(esa_world_cover.rio.crs, inplace=True)

        esa_1m = reclassified_esa.rio.reproject(
            dst_crs=crs,
            resolution=1,
            resampling=Resampling.nearest
        )

        return esa_1m

    def get_data_ulu(self, bbox, crs, snap_to):
        # Read ULU land cover, filter to city, select lulc band
        ulu_lulc = UrbanLandUse(band='lulc').get_data(bbox)
        ###### ulu_roads = UrbanLandUse(band='road').get_data(bbox)
        ####### Create road mask of 50
        ####### Typical threshold for creating road mask
        ####### road_mask = ulu_roads >= 50
        ####### ulu_lulc = ulu_lulc.where(~road_mask, 6)
        # 0-Unclassified: 0 (open space)
        # 1-Non-residential: 0 (open space), 1 (non-res)
        # 2-Residential: 2 (Atomistic), 3 (Informal), 4 (Formal), 5 (Housing project)
        ####### 3-Roads: 6 (Roads)
        mapping = {0: 0, 1: 1, 2: 2, 3: 2, 4: 2, 5: 2}
        for from_val, to_val in mapping.items():
            ulu_lulc = ulu_lulc.where(ulu_lulc != from_val, to_val)

        # Convert to int8 and chunk the data for Dask processing
        ulu_lulc = ulu_lulc.astype(np.int8).chunk({'x': 512, 'y': 512})

        ####### 1-Non-residential as default
        # 0-Unclassified as nodata 
        ulu_lulc_1m = ulu_lulc.rio.reproject(
            dst_crs=crs,
            shape=snap_to.shape,
            resampling=Resampling.nearest,
            nodata=0
        )

        return ulu_lulc_1m

    def get_data_anbh(self, bbox, snap_to):
        # Load ANBH layer
        anbh_data = AverageNetBuildingHeight().get_data(bbox)

        # Chunk the data for Dask processing
        anbh_data = anbh_data.chunk({'x': 512, 'y': 512})

        # Use reproject_match, because reproject would raise OneDimensionalRaster with shape (1,1)
        anbh_1m = anbh_data.rio.reproject_match(
            match_data_array=snap_to,
            resampling=Resampling.nearest,
            nodata=0
        )

        return anbh_1m

    def get_data_buildings(self, bbox, crs):
        # OSM buildings
        building_osm = OpenStreetMap(osm_class=OpenStreetMapClass.BUILDING).get_data(bbox).to_crs(crs).reset_index(drop=True)
        # Google-Microsoft Open Buildings Dataset buildings
        openbuilds = OpenBuildings(country='USA').get_data(bbox).to_crs(crs).reset_index(drop=True)
        
        # Intersect buildings and keep the open buildings that don't intersect OSM buildings
        intersect_buildings = gpd.sjoin(building_osm, openbuilds, how='inner', predicate='intersects')
        openbuilds_non_intersect = openbuilds.loc[~openbuilds.index.isin(intersect_buildings.index)]
        
        buildings = pd.concat([building_osm['geometry'], openbuilds_non_intersect['geometry']], ignore_index=True).reset_index()
        # Get rid of any 3d geometries that cause a problem
        buildings = buildings[~buildings['geometry'].apply(lambda geom: 'Z' in geom.geom_type)]

        # Value not start with 0
        buildings['Value'] = buildings['index'] + 1

        return buildings
    
    def rasterize_polygon(self, gdf, snap_to):
        if gdf.empty:
            raster = np.full(snap_to.shape, 0, dtype=np.int8)
            raster = xr.DataArray(raster, dims=snap_to.dims, coords=snap_to.coords)

            return raster.rio.write_crs(snap_to.rio.crs, inplace=True)

        raster = make_geocube(
            vector_data=gdf,
            measurements=["Value"],
            like=snap_to,
            fill=np.int8(0)
        ).Value

        return raster.rio.reproject_match(snap_to)
    

    def building_classifier_tree(self):
        buildings_sample = self.get_data_geo()
        
        # # Building sample 'V2-building-class-data.geojson' has extracted data and saved in geojson,
        # # so no need for steps below
        # # Step 1: Get raster data
        # bbox = buildings_sample.reset_index().total_bounds
        # crs = get_utm_zone_epsg(bbox)
        # esa_1m = BuildingClassifier().get_data_esa_reclass(bbox, crs)
        # ulu_lulc_1m = self.get_data_ulu(bbox, crs, esa_1m)
        # anbh_1m = self.get_data_anbh(bbox, esa_1m)
        # # Step 2: Extract 3 features for buildings:
        # # 2.1 majority of Urban Land Use(ULU) class
        # # 2.2 mean Average Net Building Height(ANBH)
        # # 2.3 area of the building
        # buildings_sample['ULU'] = exact_extract(ulu_lulc_1m, buildings_sample, ["majority"], output='pandas')['majority']
        # buildings_sample['ANBH'] = exact_extract(anbh_1m, buildings_sample, ["mean"], output='pandas')['mean']
        # buildings_sample['Area_m'] = buildings_sample.geometry.area

        # TODO: classifier parameters
        clf = DecisionTreeClassifier(max_depth=5)
        # encode labels
        buildings_sample['Slope_encoded'] = buildings_sample['Slope'].map({'low': np.int8(42), 'high': np.int8(40)})

        # Select these rows for the training set
        build_train = buildings_sample[buildings_sample['Model']=='training']

        clf.fit(build_train[['ULU', 'ANBH', 'Area_m']], build_train['Slope_encoded'])

        # save decision tree classifier
        with open('building_classifier.pkl','wb') as f:
            pickle.dump(clf, f)

        # # Check decision tree and accuracy
        # # Select the remaining rows for the testing set
        # build_test = buildings_sample[buildings_sample['Model']=='testing']
        # plt.figure(figsize=(20, 10))
        # plot_tree(clf, feature_names=['ULU', 'ANBH', 'Area_m'], class_names=['low','high'], filled=True)
        # plt.show()
        # # Predict and evaluate
        # y_pred = clf.predict(build_train[['ULU', 'ANBH', 'Area_m']])
        # accuracy = accuracy_score(build_train['Slope_encoded'], y_pred)
        # print(f"Training Accuracy: {accuracy}")
        # len(build_train[build_train['Slope']==build_train['pred']])/len(build_train)
        # y_pred = clf.predict(build_test[['ULU', 'ANBH', 'Area_m']])
        # accuracy = accuracy_score(build_test['Slope_encoded'], y_pred)
        # print(f"Test Accuracy: {accuracy}")
        # len(build_test[build_test['Slope']==build_test['pred']])/len(build_test)
