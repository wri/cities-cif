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

from .layer import Layer, get_utm_zone_epsg
from .esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from .urban_land_use import UrbanLandUse
from .average_net_building_height import AverageNetBuildingHeight


class BuildingClassifier(Layer):
    def __init__(self, geo_file=None, **kwargs):
        super().__init__(**kwargs)
        self.geo_file = geo_file

    def get_data_geo(self):
        buildings_sample = gpd.read_file(self.geo_file)
        buildings_sample.to_crs(epsg=4326, inplace=True)

        return buildings_sample

    def get_data_esa_reclass(self, bbox, crs):
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

        # Convert to int8 and chunk the data for Dask processing
        ulu_lulc = ulu_lulc.astype(np.int8).chunk({'x': 512, 'y': 512})

        # 1-Non-residential as default
        ulu_lulc_1m = ulu_lulc.rio.reproject(
            dst_crs=crs,
            shape=snap_to.shape,
            resampling=Resampling.nearest,
            nodata=1
        )

        return ulu_lulc_1m

    def get_data_anbh(self, bbox, crs, snap_to):
        # Load ANBH layer
        anbh_data = AverageNetBuildingHeight().get_data(bbox)

        # Chunk the data for Dask processing
        anbh_data = anbh_data.chunk({'x': 512, 'y': 512})

        anbh_1m = anbh_data.rio.reproject(
            dst_crs=crs,
            shape=snap_to.shape,
            resampling=Resampling.nearest,
            nodata=0
        )

        return anbh_1m

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
    

    # Extract values to buildings as coverage fractions
    # Extract average of pixel values to buildings
    # Reproject to local state plane and calculate area

    def extract_features(self, row, buildings_sample_1m, id_col, ulu_lulc_1m, anbh_1m):
        # 3 features:
        # majority of Urban Land Use(ULU) class
        # mean Average Net Building Height(ANBH)
        # area of the building
        mask = buildings_sample_1m == row[id_col]
        masked_ulu = ulu_lulc_1m.values[mask]

        # Extract values to buildings as coverage fractions
        # when there is no majority class, use 1-Non-residential as default
        if masked_ulu.size == 0:
            majority_ulu = 1
        else:
            unique, counts = np.unique(masked_ulu, return_counts=True)
            sorted_indices = np.argsort(-counts)  # Sort by descending order

            # Apply your specific logic
            if unique[sorted_indices[0]] != 3:
                majority_ulu = unique[sorted_indices[0]]
            elif len(sorted_indices) > 1:
                majority_ulu = unique[sorted_indices[1]]
            else:
                majority_ulu = 1  # Default to 1 non-residential

        # Extract average of pixel values to buildings
        masked_anbh = anbh_1m.values[mask]
        if masked_anbh.size == 0:
            mean_anbh = 0
        else:
            mean_anbh = np.mean(masked_anbh)

        # Reproject to local state plane and calculate area
        area_m = row.geometry.area

        return pd.Series([majority_ulu, mean_anbh, area_m])

    def building_class_tree(self):
        buildings_sample = self.get_data_geo()
        bbox = buildings_sample.reset_index().total_bounds
        crs = get_utm_zone_epsg(bbox)

        esa_1m = self.get_data_esa_reclass(bbox, crs)
        buildings_sample['Value'] = buildings_sample['ID']
        buildings_sample_1m = self.rasterize_polygon(buildings_sample, esa_1m)
        ulu_lulc_1m = self.get_data_ulu(bbox, crs, esa_1m)
        anbh_1m = self.get_data_anbh(bbox, crs, esa_1m)
        
        buildings_sample[['ULU', 'ANBH', 'Area_m']] = buildings_sample.to_crs(crs).apply(
            lambda row: self.extract_features(row, buildings_sample_1m, 'ID', ulu_lulc_1m, anbh_1m), axis=1)

        clf = DecisionTreeClassifier(max_depth=4)
        # encode labels
        buildings_sample['Slope_encoded'] = buildings_sample['Slope'].map({'low': np.int8(41), 'high': np.int8(42)})
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
