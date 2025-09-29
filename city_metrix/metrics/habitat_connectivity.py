import pandas as pd
import geopandas as gpd
from typing import Union
import rasterio
import shapely
import networkx as nx

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoZone, GeoExtent, WGS_CRS
from city_metrix.layers import NaturalAreas


class _HabitatConnectivity(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.indicator_name = None

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:

        CONNECTIVITY_DISTANCE = 100  # Max distance two patches can be apart and be considered connected (meter)
        MIN_PATCHSIZE = 1000  # Min patch size to be included in analysis (sq meter)
        
        zones = geo_zone.zones
        worldcover_layer = NaturalAreas().retrieve_data(GeoExtent(geo_zone))
        
        def within_distance(idx, gdf):
            connecteds = gdf.loc[[idx]].buffer(CONNECTIVITY_DISTANCE)[idx].intersects(gdf.geometry)
            return [i for i in list(connecteds.index[connecteds == True]) if not i == idx]

        result_values = []
        # Reproject polygon if needed
        if zones.crs != worldcover_layer.rio.crs:
            zones = zones.to_crs(worldcover_layer.rio.crs)
        for rownum in range(len(zones)):
            zone = zones.iloc[[rownum]]
            natarea_dataarray = worldcover_layer.rio.clip(zone.geometry, zone.crs)
            natarea_shapes = rasterio.features.shapes(natarea_dataarray, connectivity=8, transform=natarea_dataarray.rio.transform())  # Polygonize the natural-areas raster
            natarea_shapes = list(natarea_shapes)
            na_geoms = [i[0] for i in natarea_shapes if i[1] == 1]  # Only want the natural areas
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
                if self.indicator_name == 'EMS':
                    result_values.append((sum([i**2 for i in cluster_areas]) / total_area) / 10000)
                else:  # self.indicator_name == 'coherence'
                    result_values.append((sum([i**2 for i in cluster_areas]) / (total_area**2)) * 100)
            else:
                result_values.append(0)

        result = pd.DataFrame({'zone': zones.index, 'value': result_values})
        return result


class HabitatConnectivityCoherence__Percent(_HabitatConnectivity):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        self.indicator_name = 'coherence'
        self.unit = 'percent'


class HabitatConnectivityEffectiveMeshSize__Hectares(_HabitatConnectivity):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        self.indicator_name = 'EMS'
        self.unit = 'hectares'
