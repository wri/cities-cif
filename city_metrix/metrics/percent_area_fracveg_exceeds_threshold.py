    def fracVeg(geom, thresh, vegpctl, soilpctl):
        results = calcFr(geom, thresh, vegpctl)
        ndviImage = ee.Image(results.get('ndviImage'))
        vegNDVI = results.getNumber('vegNDVI')
        soilNDVI = results.getNumber('soilNDVI')

        if vegNDVI is None or soilNDVI is None:
            return None

        Fr = ndviImage.subtract(soilNDVI).divide(vegNDVI.subtract(soilNDVI)).pow(2).rename('Fr')

        thresholdFrac = Fr.gte(thresh).reduceRegion({
              'reducer': ee.Reducer.mean(),
              'geometry': centerRegion,
              'scale': 10,
              'crs': 'EPSG:4326',
              'maxPixels': 1000000000000
        }).getInfo().Fr
        return {'img': Fr, 'threshold_fraction': thresholdFrac}