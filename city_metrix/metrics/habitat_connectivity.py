import pandas as pd
import geopandas as gpd
from typing import Union
from city_metrix.metrix_model import Metric, GeoZone, GeoExtent, WGS_CRS
from city_metrix.layers import NaturalAreas
from city_metrix.constants import CSV_FILE_EXTENSION
import numpy as np
import rasterio
import shapely

import networkx as nx

class _HabitatConnectivity(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  indicator_name: str, **kwargs):
        super().__init__(**kwargs)
        self.indicator_name == indicator_name

    def get_metric(self,
                geo_zone: GeoZone,
                spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:

        def within_distance(idx, gdf):
            connecteds = gdf.loc[[idx]].buffer(CONNECTIVITY_DISTANCE)[idx].intersects(gdf.geometry)
            return [i for i in list(connecteds.index[connecteds==True]) if not i == idx]

        CONNECTIVITY_DISTANCE = 100    # Max distance two patches can be apart and be considered connected (meter)
        MIN_PATCHSIZE = 1000    # Min patch size to be included in analysis (sq meter)
        worldcover_layer = NaturalAreas()
        
        result = []
        zones = geo_zone.zones
        for rownum in range(len(zones)):
            zone = zones.iloc[[rownum]]
            natarea_dataarray = worldcover_layer.get_data(GeoExtent(bbox=(*zone.total_bounds), crs=WGS_CRS)
            natarea_shapes = rasterio.features.shapes(natarea_dataarray, connectivity=8, transform=natarea_dataarray.rio.transform())  # Polygonize the natural-areas raster
            natarea_shapes = list(natarea_shapes)
            na_geoms = [i[0] for i in natarea_shapes if i[1]==1]  # Only want the natural areas
            na_gdf = gpd.GeoDataFrame({'id': range(len(na_geoms)), 'geometry': [shapely.Polygon(j['coordinates'][0]) for j in na_geoms]})
            na_gdf = na_gdf.loc[na_gdf.area > MIN_PATCHSIZE]
            
            connected = {
                i: within_distance(i, na_gdf) for i in na_gdf.index
            }
            
            # Find clusters from connected pairs
            edges = []
            for k in connected:
                for i in connected[k]:
                    edges.append((k, i))
            G = nx.Graph()
            G.add_nodes_from(list(na_gdf.index))
            G.add_edges_from(edges)
            clusters = nx.connected_components(G)
            # Calculate indicator
            total_area = na_gdf.area.sum()
            cluster_areas = []
            for i in clusters:
                cluster_areas.append(sum([na_gdf.loc[[j]]['geometry'].area[j] for j in i]))
            if total_area > 0:
                result.append(sum([i**2 for i in cluster_areas]) / (total_area**({'EMS': 1, 'coherence': 2}[indicator_name])))
            else:
                result.append(0)
                
        return pd.Series(result)

class HabitatConnectivityEffectiveMeshSize__Hectares(_HabitatConnectivity):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        self.indicator_name = 'EMS'

class HabitatConnectivityCoherence__Percent(_HabitatConnectivity):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        self.indicator_name = 'coherence'

