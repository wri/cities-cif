from cities_indicators.layers.non_tropical_tree_cover import NonTropicalTreeCover
from cities_indicators.layers.land_cover_class import LandCoverClass
import ee
import geemap
import pandas as pd


class NonTreeCoverByLandUseGEE:

    def calculate(self, gdf):
        non_tree_cover = NonTropicalTreeCover().read_gee(gdf)
        land_cover_class = LandCoverClass().read_gee(gdf)
        boundary_geo_ee = geemap.geopandas_to_ee(gdf)

        results = []
        LULC_category = {"GreenSpace": 1, "BuildUp": 2, "Barren": 3, "PublicOpenSpace": 10,
                         "Roads": 20, "Water": 30, "LowSlopeRoof": 41, "HighSlopeRoof": 42, "Parking": 50}

        for cat, idx in LULC_category.items():
            # Mask the land cover image by the current class
            current_class_mask = land_cover_class.eq(idx)

            # Use the mask to extract the non_tree_cover values of the current class
            non_tree_values_of_class = non_tree_cover.updateMask(current_class_mask)

            # Calculate mean non_tree_cover of the current class
            mean = non_tree_values_of_class.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=boundary_geo_ee.geometry(),
                scale=10,  # adjust scale based on resolution
                maxPixels=1e13
            ).get('b1')
            meanpct = ee.Algorithms.If(ee.Number(mean), ee.Number(mean).multiply(0.01), "NA").getInfo()

            results.append((f"percentTreeCover{cat}", meanpct))

        df = pd.DataFrame(results, columns=["Category", "MeanValue"])
        wide_df = df.set_index("Category").T
        wide_df.reset_index(drop=True, inplace=True)

        return pd.concat([gdf, wide_df], axis=1)
