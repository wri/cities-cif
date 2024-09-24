import xarray as xr
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection


class LandCoverGlad(Layer):
    """
    Attributes:
        year: year used for data retrieval
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, year=2020, spatial_resolution=30, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        data = get_image_collection(
            ee.ImageCollection(ee.Image(f'projects/glad/GLCLU2020/LCLUC_{self.year}')),
            bbox,
            self.spatial_resolution,
            "GLAD Land Cover"
        ).b1

        return data


class LandCoverSimplifiedGlad(Layer):
    """
    Attributes:
        year: year used for data retrieval
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, year=2020, spatial_resolution=30, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        glad = LandCoverGlad(year=self.year, spatial_resolution=self.spatial_resolution).get_data(bbox)
        # Copy the original data
        data = glad.copy(deep=True)

        # Assign values based on ranges and conditions
        data = data.where(glad != 0, 0)  # If glad == 0, assign 0
        # If glad between 1 and 24, assign 1
        data = data.where((glad < 1) | (glad > 24), 1)
        # If glad between 25 and 41, assign 2
        data = data.where((glad < 25) | (glad > 41), 2)
        # If glad between 42 and 48, assign 3
        data = data.where((glad < 42) | (glad > 48), 3)
        # If glad between 100 and 124, assign 4
        data = data.where((glad < 100) | (glad > 124), 4)
        # If glad between 125 and 148, assign 5
        data = data.where((glad < 125) | (glad > 148), 5)
        # If glad between 200 and 207, assign 6
        data = data.where((glad < 200) | (glad > 207), 6)
        # data = data.where(glad != 254, 6)  # Assign 6 if glad == 254
        data = data.where(glad != 241, 7)  # If glad == 241, assign 7
        data = data.where(glad != 244, 8)  # If glad == 244, assign 8
        data = data.where(glad != 250, 9)  # If glad == 250, assign 9
        data = data.where(glad != 255, 10)  # If glad == 255, assign 10

        return data


class LandCoverHabitatGlad(Layer):
    """
    Attributes:
        year: year used for data retrieval
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, year=2020, spatial_resolution=30, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        simplified_glad = LandCoverSimplifiedGlad(year=self.year, spatial_resolution=self.spatial_resolution).get_data(bbox)
        # Copy the original data
        data = simplified_glad.copy(deep=True)

        # Apply the conditions individually to avoid overwriting
        data = data.where(simplified_glad != 0, 0)  # Where glad == 0, set to 0
        # Where glad is between 1 and 6, set to 1
        data = data.where((simplified_glad < 1) | (simplified_glad > 6), 1)
        data = data.where(simplified_glad < 7, 0)  # Where glad >= 7, set to 0

        return data


class LandCoverHabitatChangeGlad(Layer):
    """
    Attributes:
        start_year: baseline year for habitat change
        end_year: target year for habitat change
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, start_year=2000, end_year=2020, spatial_resolution=30, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        habitat_glad_start = LandCoverHabitatGlad(year=self.start_year, spatial_resolution=self.spatial_resolution).get_data(bbox)
        habitat_glad_end = LandCoverHabitatGlad(year=self.end_year, spatial_resolution=self.spatial_resolution).get_data(bbox)

        # Class 01: Became habitat between start year and end year
        class_01 = ((habitat_glad_start == 0) & (habitat_glad_end == 1))
        # Class 10: Became non-habitat between start year and end year
        class_10 = ((habitat_glad_start == 1) & (habitat_glad_end == 0))

        # Initialize the habitat change DataArray with zeros
        habitatchange = xr.full_like(habitat_glad_start, 0)
        # Set values 1 for class_01 (became habitat between start year and end year)
        habitatchange = habitatchange.where(~class_01, other=1)
        # Set values 10 for class_10 (became non-habitat between start year and end year)
        habitatchange = habitatchange.where(~class_10, other=10)

        return habitatchange