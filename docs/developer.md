# cities-cif developer guide
This document serves as a guide for cities-cif developers to add new indicators and/or new cities to the module. It provides a structured checklist and detailed steps. 

## Checklist
1. Check if the city referenced is in the cities list
    * If **No**, check #2
    * If **Yes**, check #3
2. Check if the city boundary follow the current boundaries `GeoDataFrame` structure
    * If **No**, go to step #1, then check #3
    * If **Yes**, go to step #2, then check #3
3. Check if the needed layers have been extracted
    * If **No**, go to step #3, then step #4
    * If **Yes**, go to step #4

## Steps
1. Use a standalone `GeoDataFrame` for analysis
    
    A standalone `GeoDataFrame` can be used as input zones for analysis. However, if the new cities will be part of the CIF project, you should consider converting the `GeoDataFrame` to match the current format of the [boundaries table](https://resourcewatch.carto.com/u/wri-cities/tables/boundaries/public?redirected=true) on Carto, then follow [step #2](#step-2). 

2. <a id="step-2"></a>Add a city to the [boundaries table](https://resourcewatch.carto.com/u/wri-cities/tables/boundaries/public?redirected=true) on Carto
    
    Ensure the columns in the `GeoDataFrame` align with the [boundaries table](https://resourcewatch.carto.com/u/wri-cities/tables/boundaries/public?redirected=true) on Carto. Then use the `to_carto()` function in the `cartoframes` package to upload: 

    ```to_carto(gdf, "boundaries", if_exists='append')```

3. Add a new data layer 
* Add a record in the Airtable [Datasets table](https://airtable.com/appDWCVIQlVnLLaW2/tblYpXsxxuaOk3PaZ/viwpdlQcUxqxP6R2s?blocks=hide)

    You should add a record to the Airtable table for the new dataset. There should be a formal **Name** of the data layer with the associated metadata, including **Theme**, **Data source**, **Providor**, **Spatial resolution**, etc. You should also link the record to the **Indicators** (if any) using this dataset for calculation.

* Add a record in the Airtable [Layers table](https://airtable.com/appDWCVIQlVnLLaW2/tblS72ZH2EKJ3hy61/viw1IM6ZT6VoHSgBU?blocks=hide)

    You should add a record to the Airtable table for the new data layer. The data layer is processed data from the existing or new dataset. E.g., [esa_world_cover](https://github.com/wri/cities-cif/blob/main/city_metrix/layers/esa_world_cover.py) is the world cover layer from ESA, and [natural_areas](https://github.com/wri/cities-cif/blob/main/city_metrix/layers/natural_areas.py) is a reclassification of the ESA world cover. The new data layer should be linked to the **Datasets** that generated it, and **Indicators** (if any) using this layer for calculation.

* Create a Python file in [city_metrix/layers](https://github.com/wri/cities-cif/tree/main/city_metrix/layers)

    For consistency, the Python file name should match the **Name** in the Airtable [Layers table](https://airtable.com/appDWCVIQlVnLLaW2/tblS72ZH2EKJ3hy61/viw1IM6ZT6VoHSgBU?blocks=hide). Each data layer should be a class with `__init__()` and `get_data()` functions. It could also have functions that defined in the [layers.py](https://github.com/wri/cities-cif/blob/main/city_metrix/layers/layer.py) or other necessary functions.

    If the layer is from a new dataset, ideally, pull data from the source API or S3. If the we need to get the data from Google Earth Engine, we are using `xee` wherever possible. 

* Import the new layer class to [city_metrix/layers/\_\_init\_\_.py](https://github.com/wri/cities-cif/blob/main/city_metrix/layers/__init__.py)


4. Add a new indicator
* Add a record in Airtable [Indicators table](https://airtable.com/appDWCVIQlVnLLaW2/tblWcJ2qqGCFakVdF/viwM0Ckgctf3fPkn9?blocks=hide)

    You should add a record to the Airtable table for the new indicator. There should be a unique **indicator_label** of the indicator with the associated metadata, including **theme**, **indicator_legend**, **code**, **indicator_definition**, etc. You should also link the record to the **Layers** and **data_sources_link** that are used to calculate this indicator.

* Define the indicator calculation function in [city_metrix/metrics.py](https://github.com/wri/cities-cif/blob/main/city_metrix/metrics.py)

    Define a function for new indicator with input of the calculation zones as `GeoDataFrame` and output of the calculated indicators as `Pandas Series`.


# Package structure

The `City_metrix` library allows users of geospatial data to collect and apply zonal statistics on Global Geospatial Datasets for measuring sustainability indicators in urban areas.
It provides two main functionalities:
- Extracting geospatial `layers` based on specific areas of interests (defined as geodataframe)' These data layers are collected from any cloud source (Google Earth Engine, AWS S3 public buckets, Public APIs). Two formats of data layers are handled in `city_metrix`: Rasters and vectors. Rasters data are collected and transformed into _arrays_ using `xarray` (GEE images collections are converted also into `arrays` using `xee`) and vectors adata are stored as `geopandadataframe`.  
- Measuring `indicators` using the extracted `layers` by implementing zonal statistics operations 

The main package source code is located in `city_metrix` directory.

## Layers
The `layers` sub-directory contains the different scripts used to extract layers from various data sources. Every `layer` is defined in a separate `python` script (with the name of script referencing the name of the layer). 

Every layer is defined as a python `class`, which contains all instructions to calculate and extract the data from the global data sources. Every `layer class` should include at least a `get_data` function that will be used in the `indicators` script to collect the data based on a region of interest.

## Indicators

The indicators methods are defined in `metrics.py` file. Every indicator is implemented as separate function that uses the `layers` extraction defined in the `layers` sub-module.
The indicators function take as input a `geodataframe` (defined by `zones`) and returns the indicator values.

