import ee
from cityscale.indicators import compute_hea_4
from cityscale.indicators import compute_acc_2
import cityscale.indicators.store as store


# import cityscale.indicators_old.compute as indicators_old
# import cityscale.indicators_old as indicators_old

service_account = 'cities-indicators_old@wri-gee.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, './keys/wri-gee-358d958ce7c6.json')

ee.Initialize(credentials)


# <editor-fold desc="Compute indicator HEA-4">
# compute indicator HEA-4

# <editor-fold desc="Compute indicator for one city">

indicator_df, indicator_geo = compute_hea_4.ComputeHea4(cities = ['BRA-Salvador'])

print(indicator_df)
print(indicator_geo)
# </editor-fold>

# <editor-fold desc="Compute indicator for multiple cities">
# Multiple cities

# indicator_df, indicator_geo = compute_hea_4.ComputeHea4(cities = ['BRA-Salvador','COD-Bukavu'])
#
# print(indicator_df)
# print(indicator_geo)

# </editor-fold>
# </editor-fold>

# <editor-fold desc="store indicator output">
# store indicator output
#
# Store indicator geo
# store.s3_upload_indicators_geo(indicator_geo = indicator_geo,
#                                s3_bucket_name = "cities-cities4forests",
#                                public = True)
# </editor-fold>




# <editor-fold desc="Compute indicator for one city">
# One city
# indicator_df, indicator_geo = compute_acc_2.ComputeAcc2(cities = ['BRA-Salvador'])
#
# print(indicator_df)
# print(indicator_geo)
# </editor-fold>