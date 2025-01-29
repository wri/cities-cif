from city_metrix.layers import NaturalAreas

from geopandas import GeoDataFrame, GeoSeries
from pandas import Series

import numpy as np
import rasterio
import shapely

import networkx as nx

def habitat_connectivity(zones: GeoDataFrame) -> GeoSeries:

    def within_distance(idx, gdf):
        connecteds = gdf.loc[[idx]].buffer(CONNECTIVITY_DISTANCE)[idx].intersects(gdf.geometry)
        return [i for i in list(connecteds.index[connecteds==True]) if not i == idx]

    CONNECTIVITY_DISTANCE = 100    # Max distance two patches can be apart and be considered connected (meter)
    MIN_PATCHSIZE = 1000    # Min patch size to be included in analysis (sq meter)
    worldcover_layer = NaturalAreas()
    
    result = []
    for rownum in range(len(zones)):
        zone = zones.iloc[[rownum]]
        natarea_dataarray = worldcover_layer.get_data(zone.total_bounds)
        g = rasterio.features.shapes(natarea_dataarray, connectivity=8, transform=natarea_dataarray.rio.transform())  # Polygonize the natural-areas raster
        g_list = list(g)
        na_list = [i[0] for i in g_list if i[1]==1]  # Only want the natural areas
        na_gdf = GeoDataFrame({'id': range(len(na_list)), 'geometry': [shapely.Polygon(j['coordinates'][0]) for j in na_list]})
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
            result.append(sum([i**2 for i in cluster_areas]) / (total_area**2))
        else:
            result.append(0)
            
    return Series(result)