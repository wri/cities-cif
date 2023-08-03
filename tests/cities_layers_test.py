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


# Lst
# lst = LandSurfaceTemperature.extract_gee(city ='IDN-Jakarta' , admin_level=4)
# print(lst)


# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='C:/Users/Saif.Shabou/OneDrive - World Resources Institute/Documents/cities/keys/wri-gee-358d958ce7c6.json'

lst = LandSurfaceTemperature().extract_gee(city = City(SupportedCity.IDN_Jakarta, admin_level = 4))
print(lst)


