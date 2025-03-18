from geopandas import GeoDataFrame
from shapely import wkt
from xarray import DataArray


def get_rounded_gdf_geometry(source_data, precision):
    if isinstance(source_data, GeoDataFrame):
        # Make a copy to avoid modifying the original GeoDataFrame
        rounded_gdf = source_data.copy()
    elif isinstance(source_data, DataArray):
        rounded_gdf = _convert_xdatarrray_to_gdf(source_data)
    else:
        raise Exception("Source format not supported.")

    # Apply rounding to each geometry in the GeoDataFrame
    rounded_gdf['geometry'] = rounded_gdf['geometry'].apply(
        lambda geom: wkt.loads(get_rounded_geometry(geom, precision))
    )
    return rounded_gdf


def get_rounded_geometry(geom, precision):
    return wkt.dumps(geom, rounding_precision=precision)


def _convert_xdatarrray_to_gdf(dataarray: DataArray):
    import geopandas as gpd
    from shapely.geometry import Point

    # Extract coordinates
    y = dataarray['y'].values
    x = dataarray['x'].values

    # Create a list of shapely Points
    geometry = [Point(x, y) for x, y in zip(x, y)]

    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(geometry=geometry)
    return gdf

