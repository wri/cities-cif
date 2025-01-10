import ee

from .layer import Layer

class CanopyCoverageByPercentage(Layer):
    """
    Attributes:
        height: int 1..10 min canopy height to count as covered
    """


    def __init__(self, percentage=33, height=5, **kwargs):
        super().__init__(**kwargs)
        if not (type(percentage)==int) and (percentage >= 0) and (percentage <=100):
            raise ValueError('percentage must be integer 0 through 100')
        if not height in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
            raise ValueError('height must be integer 1 through 10')
        self.percentage = percentage
        self.height = height

    def get_data(self, bbox):
        region = ee.Geometry.BBox(bbox)
        coverage_ic = ee.ImageCollection(f"projects/wri-datalab/canopycoverpct/canopycover_{self.percentage}pct_{self.height}m").filterBounds(region)
        data = get_image_collection(
            coverage_ic,
            bbox,
            1,
            "Canopy coverage"
        ).Map
        return data
