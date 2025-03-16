from shapely import wkt


def get_rounded_gdf_geometry(gdf_data, precision):
    # Make a copy to avoid modifying the original GeoDataFrame
    rounded_gdf = gdf_data.copy()
    # Apply rounding to each geometry in the GeoDataFrame
    rounded_gdf['geometry'] = rounded_gdf['geometry'].apply(
        lambda geom: wkt.loads(wkt.dumps(geom, rounding_precision=precision))
    )
    return rounded_gdf
