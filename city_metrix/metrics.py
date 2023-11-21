from city_metrix.layers import Albedo, EsaWorldCoverClass, EsaWorldCover, LandSurfaceTemperature, TropicalTreeCover


def built_land_without_tree_cover(zones):
    built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    tree_cover = TropicalTreeCover(min_tree_cover=0)

    built_land = built_up_land.groupby(zones).count()
    tree_cover_in_built_land = tree_cover.mask(built_up_land).groupby(zones).count()

    percent_tree_cover_in_built_up_land = 1 - (tree_cover_in_built_land.fillna(0) / built_land)
    return percent_tree_cover_in_built_up_land


def tree_cover(zones):
    return TropicalTreeCover().groupby(zones).mean()


def surface_reflectivity(zones, start_time, end_time, albedo_threshold):
    built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    albedo = Albedo(start_time=start_time, end_time=end_time, threshold=albedo_threshold)

    built_land = built_up_land.groupby(zones).count()
    built_albedo = albedo.mask(built_land).groupby(zones).count()

    return built_albedo / built_land


def high_land_surface_temperature(zones):
    indicator = LandSurfaceTemperature(hottest_90_days=True).groupby(zones).mean()
    return indicator