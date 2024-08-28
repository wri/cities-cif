# Pull Request Review

There are 4 options for doing code review
## Github
1. Go to https://github.com/wri/cities-cif/pulls and find the PR you want to review
2. Use Github's web based interface to review the code changes, make inline comments, and submit the review. See https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request for more details.

NOTE: This does not allow you to run the code, so is not the prefered approach, especially for more complicated changes.

## Colab
1. Open a new Colab notebook at https://colab.new/
2. Install the package from the branch you want to review with `!pip install git+https://github.com/wri/cities-cif@[branch-name]` replaceing `[branch-name]` with the branch you want to review. e.g `!pip install git+https://github.com/wri/cities-cif@feature/max_dsm` for the `feature/max_dsm` branch. https://github.com/wri/cities-cif/tree/feature/max_dsm
3. Run the code to test that it works as expected
4. Use the Github PR UI (as described above) to submit your review.

See https://drive.google.com/drive/u/0/folders/1W5VxN_7_WdjnX64SgI5SxAnJW9hhigA_ for examples

## Codespace
In progress.

## Local
1. Check out the branch locally
2. Run the code to test that it works as expected
3. Use the Github PR UI (as described above) to submit your review.


