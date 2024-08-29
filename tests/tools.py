import numpy as np

def post_process_layer(data, value_threshold=0.4, convert_to_percentage=True):
    """
    Applies the standard post-processing adjustment used for rendering of NDVI including masking
    to a threshold and conversion to percentage values.
    :param value_threshold: (float) minimum threshold for keeping values
    :param convert_to_percentage: (bool) controls whether NDVI values are converted to a percentage
    :return: A rioxarray-format DataArray
    """
    # Remove values less than the specified threshold
    if value_threshold is not None:
        data = data.where(data >= value_threshold)

    # Convert to percentage in byte data_type
    if convert_to_percentage is True:
        data = convert_ratio_to_percentage(data)

    return data

def convert_ratio_to_percentage(data):
    """
    Converts xarray variable from a ratio to a percentage
    :param data: (xarray) xarray to be converted
    :return: A rioxarray-format DataArray
    """

    # convert to percentage and to bytes for efficient storage
    values_as_percent = np.round(data * 100).astype(np.uint8)

    # reset CRS
    source_crs = data.rio.crs
    values_as_percent.rio.write_crs(source_crs, inplace=True)

    return values_as_percent
