from geopandas import GeoDataFrame, GeoSeries
import numpy as np

from city_metrix.layers.isoline import Isoline
from city_metrix.layers.world_pop import WorldPop, UrbanLandUse


def percent_population_access(zones: GeoDataFrame, cityname, amenityname, travelmode, threshold_type, threshold_value, isoline_year=2024, agesex_classes=[], informal_only=False, worldpop_year=2020, aws_profilename=None) -> GeoSeries:

    class InformalTemp(UrbanLandUse):
        def get_data(self, bbox):
            data = super().get_data(bbox)
            result = xr.where(data==3, 1, np.nan).rio.write_crs(data.crs)
            result = result.assign_attrs(**data.attrs)
            return result

    def get_accessible_population(access_features_layer, popraster_layer, zones):
        if len(access_features_layer.gdf):
            result_series = popraster_layer.mask(access_features_layer).groupby(zones).mean() * popraster_layer.mask(access_features_layer).groupby(zones).count()
        else:
            result_series = pd.Series([0] * len(zones))
        return result_series

    # cityname example: ARG-Buenos-Aires
    # amenityname is OSMclass names, in lowercase
    # travelmode is walk, bike, automobile, publictransit (only walk implemented for now)
    # threshold_type is distance or time
    # threshold_value is integer, in minutes or meters
    if informal_only:
        informal_mask = InformalTemp()
        population_layer = WorldPop(agesex_classes=agesex_classes, year=worldpop_year, masks=[informal_layer,])
    else:
        population_layer = WorldPop(agesex_classes=agesex_classes, year=worldpop_year)
    params = {
        'cityname': cityname,
        'amenityname': amenityname,
        'travelmode': travelmode,
        'threshold_type': threshold_type,
        'threshold_value': threshold_value,
        'year': isoline_year
    }
    accesszone_layer = Isoline(params, aws_profilename=aws_profilename)
    
    result_gdf = GeoDataFrame({'geometry': zones['geometry']}).set_geometry('geometry').set_crs('EPSG:4326')
    
    try:
        access_pop = get_accessible_population(accesszone_layer, population_layer, zones)
        total_pop = population_layer.groupby(zones).mean() * population_layer.groupby(zones).count()
        result = (access_pop / total_pop) * 100
        result_gdf['access_fraction'] = result
        
    except:
    # Sometimes doing entire zones gdf causes groupby to throw empty-GDF error -- workaraound is to go district-by-district
        print('Calculating district-by-district')
        
        access_fraction = []
        for idx in zones.index:
            try: # Sometimes there's still an empty-gdf error
                access_pop = get_accessible_population(accesszone_layer, population_layer, zones.loc[[zones.index[idx]]])[0]
                total_pop = (population_layer.groupby(zones.loc[[zones.index[idx]]]).mean() * population_layer.groupby(zones.loc[[zones.index[idx]]]).count())[0]
                if total_pop != 0:
                    access_fraction.append(access_pop / total_pop)
                else:
                    access_fraction.append(np.nan)
            except:
                print('Empty-GDF error for index {0}'.format(idx))
                access_fraction.append(np.nan)
        result_gdf['access_fraction'] = access_fraction
        result_gdf['access_fraction'].replace([np.inf, -np.inf], np.nan, inplace=True)
        result_gdf['access_fraction'] = result_gdf['access_fraction'] * 100
        
    return result_gdf

def percent_population_access_elderly(zones, cityname, amenityname, travelmode, threshold_type, threshold_value, isoline_year=2024, worldpop_year=2020, aws_profilename=None):
    agesex_classes=['F_60', 'F_65', 'F_70', 'F_75', 'F_80', 'M_60', 'M_65', 'M_70', 'M_75', 'M_80']
    return percent_population_access(zones=zones, cityname=cityname, amenityname=amenityname, travelmode=travelmode, threshold_type=threshold_type, threshold_value=threshold_value, isoline_year=isoline_year, agesex_classes=agesex_classes, informal_only=False, worldpop_year=worldpop_year, aws_profilename=aws_profilename)

def percent_population_access_children(zones, cityname, amenityname, travelmode, threshold_type, threshold_value, isoline_year=2024, worldpop_year=2020, aws_profilename=None):
    agesex_classes=['F_0', 'F_1', 'F_5', 'F_10', 'M_0', 'M_1', 'M_5', 'M_10']
    return percent_population_access(zones=zones, cityname=cityname, amenityname=amenityname, travelmode=travelmode, threshold_type=threshold_type, threshold_value=threshold_value, isoline_year=isoline_year, agesex_classes=agesex_classes, informal_only=False, worldpop_year=worldpop_year, aws_profilename=aws_profilename)

def percent_population_access_female(zones, cityname, amenityname, travelmode, threshold_type, threshold_value, isoline_year=2024, worldpop_year=2020, aws_profilename=None):
    agesex_classes=['F_0', 'F_1', 'F_5', 'F_10', 'F_15', 'F_20', 'F_25', 'F_30', 'F_35', 'F_40', 'F_45', 'F_50', 'F_55', 'F_60', 'F_65', 'F_70', 'F_75', 'F_80']
    return percent_population_access(zones=zones, cityname=cityname, amenityname=amenityname, travelmode=travelmode, threshold_type=threshold_type, threshold_value=threshold_value, isoline_year=isoline_year, agesex_classes=agesex_classes, informal_only=False, worldpop_year=worldpop_year, aws_profilename=aws_profilename)

def percent_population_access_informal(zones, cityname, amenityname, travelmode, threshold_type, threshold_value, isoline_year=2024, worldpop_year=2020, aws_profilename=None):
    agesex_classes=[]
    return percent_population_access(zones=zones, cityname=cityname, amenityname=amenityname, travelmode=travelmode, threshold_type=threshold_type, threshold_value=threshold_value, isoline_year=isoline_year, agesex_classes=agesex_classes, informal_only=True, worldpop_year=worldpop_year, aws_profilename=aws_profilename)