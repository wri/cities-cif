import ee

# read tml data

def read_tml():

    print("Load Tree Mosaic Land data")
    TML = ee.ImageCollection('projects/wri-datalab/TML')
    TreeCoverImg = TML.reduce(ee.Reducer.mean()).rename('b1')
    TreeCovergt0 = TreeCoverImg.updateMask(TreeCoverImg.gt(0))

    TreeDataMask = TreeCoverImg.unmask(-99).neq(-99)

    return (TreeCoverImg, TreeCovergt0, TreeDataMask)

# Test
# TreeCoverImg, TreeCovergt0, TreeDataMask = read_tml()
# print(TreeCoverImg.getInfo())