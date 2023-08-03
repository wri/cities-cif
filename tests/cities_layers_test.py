from cities_indicators.core import get_indicators, Indicator
from cities_indicators.city import SupportedCity, City
from cities_indicators.layers.albedo import Albedo
from cities_indicators.layers.land_surface_temperature import LandSurfaceTemperature

# city
geo_name = "IDN-Jakarta"
admin_level= 4
city = SupportedCity(geo_name)

# Albedo
# albedo = Albedo().read(city=City(SupportedCity.IDN_Jakarta, admin_level=4), resolution=0.001)
# print(albedo)

# albedo = Albedo().extract_gee(city = City(SupportedCity.IDN_Jakarta, admin_level = 4))
# print(albedo)


lst = LandSurfaceTemperature().extract_gee(city = City(SupportedCity.IDN_Jakarta, admin_level = 4))
print(lst)

