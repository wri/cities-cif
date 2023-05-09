import ee


# read esa data
def read_esa(land_class):
    print("Load ESA World cover data")

    WC = ee.ImageCollection("ESA/WorldCover/v100")
    WorldCover = WC.first()

    WCprojection = WC.first().projection()
    esaScale = WorldCover.projection().nominalScale()

    if (land_class == "all"):
        esa_data = WorldCover
    elif (land_class == "builtup"):
        esa_data = WorldCover.eq(50)

    return (esa_data, WCprojection, esaScale)