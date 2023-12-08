from pystac_client import Client
import rioxarray
import xarray as xr
import ee
import numpy as np
from rasterio.enums import Resampling
from geocube.api.core import make_geocube
import pandas as pd
from shapely.geometry import CAP_STYLE, JOIN_STYLE

from .layer import Layer, get_utm_zone_epsg
from .esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from .open_street_map import OpenStreetMap
from .urban_land_use import UrbanLandUse


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


        # OSM tags
        open_space_tag = {'leisure': ['park', 'nature_reserve', 'common', 'playground', 'pitch', 'track', 'garden', 'golf_course', 'dog_park', 'recreation_ground', 'disc_golf_course'],
                          'boundary': ['protected_area', 'national_park', 'forest_compartment', 'forest']}
        water_tag = {'water': True,
                     'natural': ['water'],
                     'waterway': True}
        roads_tag = {'highway': ["residential", "service", "unclassified", "tertiary", "secondary", "primary", "turning_circle", "living_street", "trunk", "motorway", "motorway_link", "trunk_link",
                                 "primary_link", "secondary_link", "tertiary_link", "motorway_junction", "turning_loop", "road", "mini_roundabout", "passing_place", "busway"]}
        building_tag = {'building': True}
        parking_tag = {'amenity': ['parking'],
                       'parking': True}

        def rasterize_osm(gdf, snap_to):
            raster = make_geocube(
                vector_data=gdf,
                measurements=["Value"],
                like=esa_1m,
                fill=0
            ).Value

            return raster.rio.reproject_match(snap_to)


        # Open space
        open_space_osm = OpenStreetMap(osm_tag=open_space_tag).get_data(bbox).to_crs(crs).reset_index()
        open_space_osm['Value'] = 10
        open_space_1m = rasterize_osm(open_space_osm, esa_1m)


        # Water
        water_osm = OpenStreetMap(osm_tag=water_tag).get_data(bbox).to_crs(crs).reset_index()
        water_osm['Value'] = 20
        water_1m = rasterize_osm(water_osm, esa_1m)


        # Roads
        roads_osm = OpenStreetMap(osm_tag=roads_tag).get_data(bbox).to_crs(crs).reset_index()
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

        # np.unique(ulu_lulc_1m.values)

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
        # # get in rioxarray format
        anbh_data = anbh_data.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})
        
        anbh_1m = anbh_data.rio.reproject(
            dst_crs=crs,
            shape=esa_1m.shape,
            resampling=Resampling.nearest,
            nodata=0
        )

        building_osm = OpenStreetMap(osm_tag=building_tag).get_data(bbox).to_crs(crs).reset_index()
        building_osm['Value'] = building_osm['osmid']  # 41 42
        building_osm_1m = rasterize_osm(building_osm, esa_1m)

        # Extract values to buildings as coverage fractions
        # Extract average of pixel values to buildings
        # Reproject to local state plane and calculate area
        def calc_majority_ULU_mean_ANBH_area(row):
            mask = building_osm_1m == row['osmid']
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
        
        building_osm[['ULU', 'ANBH', 'Area_m']] = building_osm.apply(calc_majority_ULU_mean_ANBH_area, axis=1)

        # TODO
        # roof slope model

        # Parking
        parking_osm = OpenStreetMap(osm_tag=parking_tag).get_data(bbox).to_crs(crs).reset_index()
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
