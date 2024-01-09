# Cities Indicator framework Developer Guide
This document serves as a guide for cities-cif developers who would like to contribute to this project. At it's core, this project intents to standardize the process of caclulating zonal statistics for city boundaries. To do so we need 3 basic components
 1. Data layers that we want to use as inputs
 2. Indicator functions that define the desired calculations
 3. City boundary files to run the indicator calculation on

## Package structure

The `City_metrix` library allows users of geospatial data to collect and apply zonal statistics on Global Geospatial Datasets for measuring sustainability indicators in urban areas.

It provides two main functionalities:
1. Extracting geospatial `layers` based on specific areas of interests (defined as geodataframe)' These data layers are collected from any cloud source (Google Earth Engine, AWS S3 public buckets, Public APIs). Two formats of data layers are handled in `city_metrix`: Rasters and vectors. 
    - Rasters data are collected and transformed into _arrays_ using `xarray` (GEE images collections are converted also into `arrays` using `xee`).
    - Vectors adata are stored as `geopandadataframe`.  
2. Measuring `indicators` using the extracted `layers` by implementing zonal statistics operations 

The main package source code is located in the `city_metrix` directory.

### Layers
The `layers` sub-directory contains the different scripts used to extract layers from various data sources. Every `layer` is defined in a separate `python` script (with the name of script referencing the name of the layer). 

Every layer is defined as a python `class`, which contains all instructions to calculate and extract the data from the global data sources. Every `layer class` should include at least a `get_data` function that will be used in the `indicators` script to collect the data based on a region of interest.

### Indicators

The indicators methods are defined in the `metrics` folder. Every indicator is implemented as a separate function in a separate file that uses the `layers` extraction defined in the `layers` sub-module.
The indicators function takes as input a `geodataframe` (defined by `zones`) and returns the indicator values.

### Cities
By default we assume you will provide the city boundary files you want to run calculations on. 

We also have and API for storing city polygons and calculated metrics in a standardized way for projects that want a system to keep track of their inputs and outputs. If you want to use that, get in touch with Saif, Tori, or Chris.

## Setup

1. Before getting started here, check out the main project [README](../README.md) file to setup your local environment and run through the tutorial to get a sense of how to use the existing functionality.

2. We keep track of all our datasets, layers, and cities in Airtable so you should make sure you have premission to add records to https://airtable.com/appDWCVIQlVnLLaW2

3. [Optional] If you want to add new cities or indicator values to the API, you will need access to our Carto account but the framework does not depend on this.


## Adding a Data layer
Hopefully we already have the layers you need in `city_metrix/layers/` and you can skip this step. If not here is the process of creating a new one.

1. Add a record in the Airtable [Datasets table](https://airtable.com/appDWCVIQlVnLLaW2/tblYpXsxxuaOk3PaZ/viwpdlQcUxqxP6R2s?blocks=hide)

    You should add a record to the Airtable table for the new dataset. There should be a formal **Name** of the data layer with the associated metadata, including **Theme**, **Data source**, **Providor**, **Spatial resolution**, etc. You should also link the record to the **Indicators** (if any) using this dataset for calculation.

2. Add a record in the Airtable [Layers table](https://airtable.com/appDWCVIQlVnLLaW2/tblS72ZH2EKJ3hy61/viw1IM6ZT6VoHSgBU?blocks=hide)

    You should add a record to the Airtable table for the new data layer. The data layer is processed data from the existing or new dataset. E.g., [esa_world_cover](../city_metrix/layers/esa_world_cover.py) is the world cover layer from ESA, and [natural_areas](../city_metrix/layers/natural_areas.py) is a reclassification of ESA world cover. The new data layer should be linked to the **Datasets** that generated it, and **Indicators** (if any) using this layer for calculation.

3. Create a Python file in [city_metrix/layers](../city_metrix/layers)

    For consistency, the Python file name should match the **Name** in the Airtable [Layers table](https://airtable.com/appDWCVIQlVnLLaW2/tblS72ZH2EKJ3hy61/viw1IM6ZT6VoHSgBU?blocks=hide). Each data layer should be a class with `__init__()` and `get_data()` functions. It could also use functions defined in [layers.py](../city_metrix/layers/layer.py) or other necessary functions.

    If the layer is from a new dataset, ideally, pull data from the source API or S3. If we need to get the data from Google Earth Engine, we are using `xee` wherever possible. 

4. Import the new layer class to [city_metrix/layers/\_\_init\_\_.py](../city_metrix/layers/__init__.py)


## Adding an Indicator
Once you have all the data layers you need as inputs, here is the process to create an indicator using them.

1. Add a record in Airtable [Indicators table](https://airtable.com/appDWCVIQlVnLLaW2/tblWcJ2qqGCFakVdF/viwM0Ckgctf3fPkn9?blocks=hide)

    You should add a record to the Airtable table for the new indicator. There should be a unique **indicator_label** of the indicator with the associated metadata, including **theme**, **indicator_legend**, **code**, **indicator_definition**, etc. You should also link the record to the **Layers** and **data_sources_link** that are used to calculate this indicator.

2. Define the indicator calculation function in a new file in [city_metrix/metrics](../city_metrix/metrics)

    Define a function for new indicator with the input of the calculation zones as a `GeoDataFrame` and output of the calculated indicators as a `Pandas Series`.


## Adding Cities
You can always have users just provide their own boudary files, but if you are working on a project where you want to provide access to a common set of city boundaries, the best option is to add them to the API

### Use a standalone `GeoDataFrame` for analysis
    
A standalone `GeoDataFrame` can be used as input zones for analysis. However, if the new cities will be part of the CIF project, you should consider converting the `GeoDataFrame` to match the current format of the [boundaries table](https://resourcewatch.carto.com/u/wri-cities/tables/boundaries/public?redirected=true) on Carto.

### Add a city to the [boundaries table](https://resourcewatch.carto.com/u/wri-cities/tables/boundaries/public?redirected=true) on Carto

Ensure the columns in the `GeoDataFrame` align with the [boundaries table](https://resourcewatch.carto.com/u/wri-cities/tables/boundaries/public?redirected=true) on Carto. Then use the `to_carto()` function in the `cartoframes` package to upload: 

```to_carto(gdf, "boundaries", if_exists='append')```


## Tests
You can run the tests by setting the credentials above and running the following:

```
cd ./tests
pytest layers.py
pytest metrics.py
```
