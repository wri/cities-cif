
def get_data_lake_path(dataset_name, region_name, iso, admin_level):
    return f"s3://cities-indicators/{dataset_name}/{iso}/{region_name}/{admin_level}/{iso}-{region_name}-{admin_level}-{dataset_name}.tif"
