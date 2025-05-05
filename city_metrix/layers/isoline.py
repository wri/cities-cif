import geopandas as gpd
import shapely
import urllib
from math import floor
from .layer import Layer
from .layer_geometry import GeoExtent, construct_city_aoi_json, get_utm_zone_from_latlon_point
from .world_pop import WorldPop, WorldPopClass
from .urban_land_use import UrbanLandUse
from geocube.api.core import make_geocube

BUCKET_NAME = 'wri-cities-indicators'
PREFIX = 'devdata/inputdata'
DEFAULT_SPATIAL_RESOLUTION = 10
WORLDPOP_SPATIAL_RESOLUTION = 100
INFORMAL_CLASS = 3

class AccessibleRegion(Layer):
    def __init__(self, city_id='KEN-Nairobi', level='adminbound', amenity='jobs', travel_mode='walk', threshold=15, unit='minutes', buffered_and_simplified=False, dissolved=True, **kwargs):
        super().__init__(**kwargs)
        self.city_id = city_id
        self.level = level
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.buffered_and_simplified = buffered_and_simplified
        self.dissolved = dissolved

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        url = f'https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{PREFIX}/{self.amenity}__{self.city_id}__{self.level}__{self.travel_mode}__{self.threshold}__{self.unit}.geojson'
        print(f'Attempting to retrieve isoline file from {url}', end=' ')
        try:
            gdf = gpd.read_file(url)
            print('(Succeeded)')
        except urllib.error.HTTPError:
            raise Exception(f"Isoline file {url} does not exist.")
        iso_gdf = gpd.GeoDataFrame({'is_accessible': [1] * len(gdf), 'geometry': gdf.to_crs('EPSG:4326')['geometry']}).to_crs('EPSG:4326').set_crs('EPSG:4326').set_geometry('geometry')
        if iso_gdf.crs in ('EPSG:4326', 'epsg:4326'):
            total_bounds = iso_gdf.total_bounds
            center_point = shapely.Point((total_bounds[0] + total_bounds[2]) / 2, (total_bounds[1] + total_bounds[3]) / 2)
            utm_epsg = get_utm_zone_from_latlon_point(center_point)
            iso_gdf = iso_gdf.to_crs(utm_epsg).set_crs(utm_epsg)
        if self.buffered_and_simplified:
            poly_list = [shapely.simplify(p.buffer(0.1), tolerance=10) for p in iso_gdf.geometry]  # Buffer and simplify
        else:
            poly_list = [p.buffer(0.1) for p in iso_gdf.geometry]
        uu = shapely.unary_union(shapely.MultiPolygon(poly_list))
        if self.dissolved:
            shorter_gdf = gpd.GeoDataFrame({'accessible': [1], 'geometry': uu}).dissolve().set_crs(utm_epsg)
        else:
            shorter_gdf = gpd.GeoDataFrame({'accessible': [1] * len(poly_list), 'geometry': poly_list}).set_crs(utm_epsg)
        shorter_gdf = shorter_gdf.to_crs('EPSG:4326').set_crs('EPSG:4326')
        return shorter_gdf

class AccessibleCount(Layer):
    def __init__(self, city_id='KEN-Nairobi', level='adminbound', amenity='jobs', travel_mode='walk', threshold=15, unit='minutes', align_to=None, **kwargs):
        super().__init__(**kwargs)
        self.city_id = city_id
        self.level = level
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.buffered_and_simplified = False
        self.dissolved = False
        self.align_to = align_to

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        iso_layer = AccessibleRegion(city_id=self.city_id, amenity=self.amenity, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit, buffered_and_simplified=self.buffered_and_simplified, dissolved=self.dissolved)
        iso_gdf = iso_layer.get_data(bbox)
        if len(iso_gdf) == 1 and type(iso_gdf.iloc[0].geometry) == shapely.geometry.polygon.Polygon: # only one simple-polygon isoline
            dissected_gdf = GeoDataFrame({'poly_id': [0], 'geometry': [iso_gdf.iloc[0].geometry]}).set_crs('EPSG:4326')
        else:
            # Collect individual boundary linestrings of each isoline polygon
            iso_eachboundary = [iso_gdf.iloc[rownum]['geometry'].boundary for rownum in range(len(iso_gdf))]
            iso_boundarylinesmulti = [i for i in iso_eachboundary if i is not None]
            iso_boundarylines = []
            for i in iso_boundarylinesmulti:
                if type(i) == shapely.geometry.linestring.LineString:
                    iso_boundarylines.append(i)
                else:
                    for j in list(i.geoms):
                        iso_boundarylines.append(j)
            iso_bl_gdf = gpd.GeoDataFrame({'idx': range(len(iso_boundarylines)), 'geometry': iso_boundarylines})
            print("Converted isoline polygons into boundary multilines")
            # Dissolve all linestrings into large multilinestring, and polygonize into "dissected polygons"

            iso_dissected_polys = shapely.polygonize(list(iso_bl_gdf.dissolve().geometry[0].geoms))
            print("Creating gdf of dissected polygons")
            dissected_gdf = gpd.GeoDataFrame({'poly_id': range(len(list(iso_dissected_polys.geoms))), 'geometry': list(iso_dissected_polys.geoms)}).set_crs('EPSG:4326')
        # For each dissected polygon, find how many of the original isoline polys contain the centroid
        # This is the number of amenity points are accessible within the dissected polygon
        print("Counting original isoline polygons that intersect with each dissected polygon")
        count_amenities = dissected_gdf.centroid.within(iso_gdf.iloc[[0]].geometry[iso_gdf.index[0]]) * 1  # This is a Series storing running sum, a vector with num rows == num of dissected polys
        print("|==" + "============INCLUSION=TESTS" + ("=" * 71) + "|")
        print(" ", end="")
        progress = 0
        for iso_idx in range(1, len(iso_gdf)):  # Iterate through all original isoline polys: test dissected polys to see whether centroids are included in isoline poly, add to running sum Series
            if floor(100 * iso_idx / len(iso_gdf)) > progress:
                progress = floor(100 * iso_idx / len(iso_gdf))
                print("X", end="")
            count_amenities = count_amenities + (dissected_gdf.centroid.within(iso_gdf.iloc[[iso_idx]].geometry[iso_gdf.index[iso_idx]]) * 1)
        print("X")
        dissected_gdf['count'] = count_amenities
        if self.align_to is None:
            raster = make_geocube(
                vector_data=dissected_gdf[['geometry', 'count']].to_crs(bbox.as_utm_bbox().crs),
                measurements=["count"],
                resolution=(-spatial_resolution, spatial_resolution),
            )
        else:
            raster = make_geocube(
                vector_data=dissected_gdf[['geometry', 'count']].to_crs(bbox.as_utm_bbox().crs),
                measurements=["count"],
                like=self.align_to
            )
        return raster.to_array(dim='count').squeeze()

class AccessibleCountPopWeighted(Layer):
    def __init__(self, city_id='KEN-Nairobi', level='adminbound', amenity='jobs', travel_mode='walk', threshold=15, unit='minutes', worldpop_agesex_classes=[], worldpop_year=2020, informal_only=False, **kwargs):
        super().__init__(**kwargs)
        self.city_id = city_id
        self.level = level
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.buffered_and_simplified = False
        self.dissolved = False
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.worldpop_year = worldpop_year
        self.informal_only = informal_only

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=WORLDPOP_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        population_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year)
        if self.informal_only:
            informal_layer = UrbanLandUse(return_value=INFORMAL_CLASS)
            population_layer.masks.append(informal_layer)
        population_data = population_layer.get_data(bbox, spatial_resolution=spatial_resolution)
        count_layer = AccessibleCount(city_id=self.city_id, amenity=self.amenity, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit, align_to=population_data)
        count_data = count_layer.get_data(bbox, spatial_resolution=WORLDPOP_SPATIAL_RESOLUTION)
        utm_crs = bbox.as_utm_bbox().crs
        data = count_data * (population_data / population_data.mean()).rio.write_crs(utm_crs)
        return data