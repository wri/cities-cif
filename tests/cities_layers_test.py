#from cities_indicators.core import get_indicators, Indicator
from cities_indicators.city import SupportedCity, City
from cities_indicators.layers.albedo import Albedo
from cities_indicators.layers.land_surface_temperature import LandSurfaceTemperature
from cities_indicators.indicators.built_land_with_high_lst import BuiltUpHighLandSurfaceTemperature
from cities_indicators.indicators.built_land_with_high_lst_gee import BuiltUpHighLandSurfaceTemperatureGEE
# city
geo_name = "IDN-Jakarta"
admin_level= 4
city = SupportedCity(geo_name)

# Read Albedo
# albedo = Albedo().read(city=City(SupportedCity.IDN_Jakarta, admin_level=4), resolution=0.001)
# print(albedo)

# Extract albedo
# albedo = Albedo().extract_gee(city = City(SupportedCity.IDN_Jakarta, admin_level = 4))
# print(albedo)

# Extract LST
# lst = LandSurfaceTemperature().extract_gee(city = City(SupportedCity.IDN_Jakarta, admin_level = 4))
# print(lst)


# Read LST
# lst = LandSurfaceTemperature().read(city=City(SupportedCity.IDN_Jakarta, admin_level=4), resolution=0.001)
# print(lst)

# Read LST
# lst = BuiltUpHighLandSurfaceTemperature().calculate(city=City(SupportedCity.IDN_Jakarta, admin_level=4))
# print(lst.describe())

# Read LST GEE
# lst = BuiltUpHighLandSurfaceTemperatureGEE().calculate(city=City(SupportedCity.IDN_Jakarta, admin_level=4))
# print(lst.describe())

