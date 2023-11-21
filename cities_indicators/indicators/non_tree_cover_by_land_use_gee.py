from ..layers.non_tropical_tree_cover import NonTropicalTreeCover
from ..layers.land_cover_class import LandCoverClass
from ..io import split_into_grids
import ee
import geemap
import pandas as pd


class NonTreeCoverByLandUseGEE:

    def calculate(self, gdf):
        non_tree_cover, non_tree_cover_scale = NonTropicalTreeCover().read_gee(gdf)
        land_cover_class = LandCoverClass().read_gee(gdf)
        boundary_geo_ee = geemap.geopandas_to_ee(gdf)

        results = []
        LULC_category = {"GreenSpace": 1, "BuildUp": 2, "Barren": 3, "PublicOpenSpace": 10,
                         "Roads": 20, "Water": 30, "LowSlopeRoof": 41, "HighSlopeRoof": 42, "Parking": 50}

        # Function to split a list into batches
        def split_list(input_list, chunk_size):
            for i in range(0, len(input_list), chunk_size):
                yield input_list[i:i + chunk_size]
        
        # gridSize = maxPixels default[1e9]/(1 degree[100km]/spatial resolution[m])^2 keep one decimal point to ceil
        gridSize = ee.Number(1e9).divide(ee.Number(100000).divide(non_tree_cover_scale).pow(2)).multiply(10).floor().add(1).divide(10)

        # Modify gridSize based on desired grid size
        grids = split_into_grids(boundary_geo_ee.geometry(), gridSize)

        if len(grids.getInfo()) == 1:
            for cat, idx in LULC_category.items():
                # Mask the land cover image by the current class
                current_class_mask = land_cover_class.eq(idx)

                # Use the mask to extract the non_tree_cover values of the current class
                non_tree_values_of_class = non_tree_cover.updateMask(
                    current_class_mask)

                # Calculate mean non_tree_cover of the current class
                mean = non_tree_values_of_class.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=boundary_geo_ee.geometry(),
                    scale=non_tree_cover_scale,  # adjust scale based on resolution
                    maxPixels=1e13
                ).get('b1')

                meanpct = ee.Algorithms.If(ee.Number(mean), ee.Number(mean).multiply(0.01), "NA").getInfo()
                results.append((f"percentTreeCover{cat}", meanpct))
        else:
            for cat, idx in LULC_category.items():
                sumpct_list = []
                sumone_list = []

                for grid in grids.getInfo():
                    # Mask the land cover image by the current class
                    current_class_mask = land_cover_class.clip(grid).eq(idx)
                    # Use the mask to extract the non_tree_cover values of the current class
                    non_tree_values_of_class = non_tree_cover.clip(grid).updateMask(current_class_mask)
                    # Calculate mean non_tree_cover of the current class
                    sumtree = non_tree_values_of_class.reduceRegion(
                        reducer=ee.Reducer.sum(),
                        geometry=grid,
                        scale=non_tree_cover_scale,  # adjust scale based on resolution
                        maxPixels=1e13
                    ).get('b1')
                    sumpct = ee.Algorithms.If(ee.Number(sumtree), ee.Number(sumtree).multiply(0.01), "NA")

                    maskedOnes = ee.Image.constant(1).clip(grid).updateMask(non_tree_values_of_class.mask())
                    sumone = maskedOnes.reduceRegion(
                        reducer=ee.Reducer.sum(),
                        geometry=grid,
                        scale=non_tree_cover_scale,
                        maxPixels=1e13
                    ).get('constant')
                    sumone = ee.Algorithms.If(ee.Number(sumone), ee.Number(sumone), "NA")

                    sumpct_list.append(sumpct)
                    sumone_list.append(sumone)
                
                if len(sumpct_list)>30:
                    # Split the list into batches
                    batches = list(split_list(sumpct_list, 30))
                    sum_pct = 0
                    # Process each batch
                    for batch in batches:
                        # Filter out "NA" values, sum the batch, and add the result to the running total
                        batch_sum = ee.Number(ee.List(batch).filter(ee.Filter.neq('item', "NA")).reduce(ee.Reducer.sum())).getInfo()
                        sum_pct += batch_sum
                    
                    # Split the list into batches
                    batches = list(split_list(sumone_list, 30))
                    sum_one = 0
                    # Process each batch
                    for batch in batches:
                        # Filter out "NA" values, sum the batch, and add the result to the running total
                        batch_sum = ee.Number(ee.List(batch).filter(ee.Filter.neq('item', "NA")).reduce(ee.Reducer.sum())).getInfo()
                        sum_one += batch_sum

                    meanpct = sum_pct/sum_one

                else:
                    meanpct = ee.Number(ee.List(sumpct_list).filter(ee.Filter.neq('item', "NA")).reduce(ee.Reducer.sum())).divide(
                        ee.Number(ee.List(sumone_list).filter(ee.Filter.neq('item', "NA")).reduce(ee.Reducer.sum()))).getInfo()
                    # meanpct = sum(item for item in sumpct_list if item != "NA")/sum(item for item in sumone_list if item != "NA")
                results.append((f"percentTreeCover{cat}", meanpct))

        df = pd.DataFrame(results, columns=["Category", "MeanValue"])
        wide_df = df.set_index("Category").T
        wide_df.reset_index(drop=True, inplace=True)

        return pd.concat([gdf, wide_df], axis=1)
