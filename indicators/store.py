def s3_upload_indicators_geo(indicator_geo, s3_bucket_name, public):
    import os
    import pandas as pd
    import boto3

    # get aws credentials
    path_credentials = os.environ['HOMEPATH'] + '/s3_keys/credentials.csv'
    aws_credentials = pd.read_csv(path_credentials)
    aws_key = aws_credentials.iloc[0]['Access key ID']
    aws_secret = aws_credentials.iloc[0]['Secret access key']

    # create s3 session
    s3 = boto3.resource(
        service_name='s3',
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret)

    cities = indicator_geo['geo_parent_name'].unique()

    for i in range(0, len(cities)):
        city = cities[i]
        print(city)

        geo_levels = indicator_geo['geo_level'].unique()

        # filter aoi level
        geo_levels_aoi = geo_levels[0]
        indicator_geo_aoi = indicator_geo[indicator_geo.geo_level == geo_levels_aoi]

        s3_file = 'data/indicators/indicators_geo/' + city + '-' + geo_levels_aoi + '.geojson'

        print("store AOI level indicators:")
        print(s3_file)

        # upload geojson file
        indicator_geo_aoi.to_file(
            f"s3://{s3_bucket_name}/{s3_file}",
            index=False,
            storage_options={
                "key": aws_key,
                "secret": aws_secret
            }
        )

        if (public == True):
            # make it public
            object_acl = s3.ObjectAcl(s3_bucket_name, s3_file)
            response = object_acl.put(ACL='public-read')

        # filter unit  level
        geo_levels_unit = geo_levels[1]
        indicator_geo_unit = indicator_geo[indicator_geo.geo_level == geo_levels_unit]

        s3_file = 'data/indicators/indicators_geo/' + city + '-' + geo_levels_unit + '.geojson'

        print("store Unit level indicators:")
        print(s3_file)

        # upload geojson file
        indicator_geo_unit.to_file(
            f"s3://{s3_bucket_name}/{s3_file}",
            index=False,
            storage_options={
                "key": aws_key,
                "secret": aws_secret
            }
        )

        if (public == True):
            # make it public
            object_acl = s3.ObjectAcl(s3_bucket_name, s3_file)
            response = object_acl.put(ACL='public-read')


