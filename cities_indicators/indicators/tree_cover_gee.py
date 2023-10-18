from cities_indicators.layers.tropical_tree_cover import TropicalTreeCover
import ee
import geemap


class TreeCoverGEE:

    def calculate(self, gdf):
        tree_cover = TropicalTreeCover().read_from_gee(gdf)
        crs = tree_cover.projection().getInfo()['crs']
        gdf.crs = crs
        boundary_geo_ee = geemap.geopandas_to_ee(gdf)

        # reduce images to get vegetation and built-up pixel counts
        pixelcounts = tree_cover.reduceRegions(boundary_geo_ee, ee.Reducer.mean().setOutputs(['TreeCoverMean']), 10)

        # convert pixel counts to area percentages and saves to FC as property
        def toPct(feat):
            meanvalue = feat.getNumber('TreeCoverMean') 
            Treepct = ee.Algorithms.If(meanvalue, meanvalue.multiply(0.01), "NA")
            return feat.set({
                'PctTreeCover': Treepct
            })

        pixelcounts = pixelcounts.map(toPct).select(['geo_id', 'PctTreeCover'])

        # store in df and append
        df = geemap.ee_to_pandas(pixelcounts)

        return gdf.set_index("index").merge(df, on='geo_id').rename(columns={'PctTreeCover': 'LND_2_percentTreeCover'})
