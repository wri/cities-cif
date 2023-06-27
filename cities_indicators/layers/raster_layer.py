import rioxarray
import xarray as xr

from cities_indicators.city import City


class RasterLayer:
    def read(self, city: City):
        # get the country TIF
        layer_uris = self.get_layer_uris(city)

        # read and clip to city extent
        windows = []
        for layer_uri in layer_uris:
            ds = rioxarray.open_rasterio(layer_uri)
            window = ds.rio.clip_box(*city.extent)
            windows.append(window)

        unaligned_data = xr.concat(windows)

        # make sure the boundaries align with city analysis
        city_raster = city.to_raster()
        aligned_data = unaligned_data.rio.reproject_match(city_raster).assign_coords({
            "x": city_raster.x,
            "y": city_raster.y,
        })

        return aligned_data
