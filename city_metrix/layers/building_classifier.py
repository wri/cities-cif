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

from .layer import Layer, get_utm_zone_epsg
from .esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from .urban_land_use import UrbanLandUse


class BuildingClassifier(Layer):
    def __init__(self, geo_file=None, **kwargs):
        super().__init__(**kwargs)
        self.geo_file = geo_file

    def get_data(self):
        buildings_sample = gpd.read_file(self.geo_file)
        buildings_sample.to_crs(epsg=4326,inplace=True)
        bbox = buildings_sample.reset_index().total_bounds

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
        reclassified_esa = xr.apply_ufunc(
            np.vectorize(lambda x: reclass_map.get(x, x)),
            esa_world_cover,
            vectorize=True
        )

        reclassified_esa = reclassified_esa.rio.write_crs(esa_world_cover.rio.crs, inplace=True)

        esa_1m = reclassified_esa.rio.reproject(
            dst_crs=crs,
            resolution=1,
            resampling=Resampling.nearest
        )

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

        # ANBH is the average height of the built surfaces, USE THIS
        # AGBH is the amount of built cubic meters per surface unit in the cell
        # https://ghsl.jrc.ec.europa.eu/ghs_buH2023.php
        anbh = (ee.ImageCollection("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_R2023A")
                .filterBounds(ee.Geometry.BBox(*bbox))
                .select('b1')
                .mosaic()
                )
        ds = xr.open_dataset(
            ee.ImageCollection(anbh),
            engine='ee',
            scale=100,
            crs=crs,
            geometry=ee.Geometry.Rectangle(*bbox)
        )
        anbh_data = ds.b1.compute()
        # get in rioxarray format
        anbh_data = anbh_data.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})
        
        anbh_1m = anbh_data.rio.reproject(
            dst_crs=crs,
            shape=esa_1m.shape,
            resampling=Resampling.nearest,
            nodata=0
        )

        return buildings_sample, esa_1m, ulu_lulc_1m, anbh_1m, crs
    

    # Extract values to buildings as coverage fractions
    # Extract average of pixel values to buildings
    # Reproject to local state plane and calculate area
    def calc_majority_ULU_mean_ANBH_area(self, row, building_sample_1m, id_col, ulu_lulc_1m, anbh_1m):
        mask = building_sample_1m == row[id_col]
        masked_ulu = ulu_lulc_1m.values[mask]
        
        # Extract values to buildings as coverage fractions
        # when there is no majority class, use 1-Non-residential as default
        if masked_ulu.size == 0:
            majority_ULU = 1
        else:
            unique, counts = np.unique(masked_ulu, return_counts=True)
            sorted_indices = np.argsort(-counts)  # Sort by descending order
            
            # Apply your specific logic
            if unique[sorted_indices[0]] != 3:
                majority_ULU = unique[sorted_indices[0]]
            elif len(sorted_indices) > 1:
                majority_ULU = unique[sorted_indices[1]]
            else:
                majority_ULU = 1  # Default to 1 non-residential

        # Extract average of pixel values to buildings
        masked_anbh = anbh_1m.values[mask]
        if masked_anbh.size == 0:
            mean_ANBH = 0
        else:
            mean_ANBH = np.mean(masked_anbh)
        
        # Reproject to local state plane and calculate area
        Area_m = row.geometry.area

        return pd.Series([majority_ULU, mean_ANBH, Area_m])
        
        # TODO
        # roof slope model
    def rasterize_building(self, gdf, snap_to):
        raster = make_geocube(
            vector_data=gdf,
            measurements=["Value"],
            like=snap_to,
            fill=0
        ).Value

        return raster.rio.reproject_match(snap_to)
    
    def building_class_tree(self):
        buildings_sample, esa_1m, ulu_lulc_1m, anbh_1m, crs = self.get_data()
        buildings_sample['Value'] = buildings_sample['ID']
        buildings_sample_1m = self.rasterize_building(buildings_sample, esa_1m)
        buildings_sample[['ULU', 'ANBH', 'Area_m']] = buildings_sample.to_crs(crs).apply(lambda row:self.calc_majority_ULU_mean_ANBH_area(row, buildings_sample_1m, 'ID', ulu_lulc_1m, anbh_1m), axis=1)
        
        clf = DecisionTreeClassifier(max_depth=4)
        # encode labels
        buildings_sample['Slope_encoded'] = buildings_sample['Slope'].map({'low': 41, 'high': 42})
        # drop records with NA in Slope
        buildings_sample = buildings_sample.dropna(subset=['Slope'])

        clf.fit(buildings_sample[['ULU', 'ANBH', 'Area_m']], buildings_sample['Slope_encoded'])

        # plt.figure(figsize=(20, 10))
        # plot_tree(clf, feature_names=['ULU', 'ANBH', 'Area_m'], class_names=['low','high'], filled=True)
        # plt.show()

        # Predict and evaluate
        # y_pred = clf.predict(buildings_sample[['ULU', 'ANBH', 'Area_m']])
        # accuracy = accuracy_score(buildings_sample['Slope_encoded'], y_pred)
        # print(f"Accuracy: {accuracy}")

        return clf
