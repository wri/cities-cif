# cities-cif


## Dependencies
### Conda
`conda env create -f environment.yml`




## Credentials
In order to run all of the indicator calculations in the repo you need 5 sets of credentials. Get in touch with one of the contributors to this repo and they can help get you set up.
    1. An Airtable account with access to https://airtable.com/appDWCVIQlVnLLaW2 if you want to add new Cities and Indicators in the API. This is currently required to calculate indicators for a city.
    2. A GEE account to read source data: Put `wri-gee-358d958ce7c6.json` in the repo folder.
    3. A GCP account to write data from GEE to: Put `gcsCIFcredential.json` in the repo folder.
    4. An AWS account to write out data layers to S3: Make sure you have a `~/.aws/credentials` let us know your aws username. We can make sure you have the proper access
    5. A Carto account to store city polygons and indicator values: Create an environmental variable called `CARTO_API_KEY`
