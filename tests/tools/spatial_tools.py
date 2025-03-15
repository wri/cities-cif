from shapely import wkt


def get_rounded_gdf_geometry(gdf_data, precision):
    # Make a copy to avoid modifying the original GeoDataFrame
    rounded_gdf = gdf_data.copy()
    # Apply rounding to each geometry in the GeoDataFrame
    rounded_gdf['geometry'] = rounded_gdf['geometry'].apply(
        lambda geom: wkt.loads(get_rounded_geometry(geom, precision))
    )
    return rounded_gdf


def get_rounded_geometry(geom, precision):
    return wkt.dumps(geom, rounding_precision=precision)
