from cityscale.layers import tree_mosaic_land
from cityscale.layers import esa_world_cover
from cityscale.layers import open_space

service_account = 'cities-indicators@wri-gee.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, './keys/wri-gee-358d958ce7c6.json')

ee.Initialize(credentials)


# read tml
# TreeCoverImg, TreeCovergt0, TreeDataMask = tree_mosaic_land.read_tml()
# print(TreeCoverImg.getInfo())


# read esa - builtup
# builtup, WCprojection, esaScale = esa_world_cover.read_esa(land_class="builtup")
# print(builtup.getInfo())

# read open space
openspace_geo, openspace_geo_ee = open_space.read_open_space(geo_name = 'BRA-Salvador')
print(openspace_geo)