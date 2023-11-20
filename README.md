# cities-cif

## Dependencies
### Conda
`conda env create -f environment.yml`

## Credentials
To run the module, you need to a GEE-enabled GCP service account to read and write data.

Set the following environment variables:
- GOOGLE_APPLICATION_CREDENTIALS: The path of GCP credentials JSON file containing your private key.
- GOOGLE_APPLICATION_USER: The email for your GCP user.
- GCS_BUCKET: The GCS bucket to read and write data from. 

For example, you could set the following in your `~/.zshrc` file:

```
export GCS_BUCKET=gee-exports
export GOOGLE_APPLICATION_USER=developers@citiesindicators.iam.gserviceaccount.com
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials/file
```

## How to contribute
Create a Pull request

You can run the tests by setting the credentials above and running the following:

```
cd ./tests
pytest cities_indicators_test.py
```