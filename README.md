# SorterBot Cloud
Cloud service for the SorterBot project, which contains the neural networks and other compute-heavy tasks needed for image processing. It can be run locally as a Docker container, and can be easily deployed to AWS ECS by using the provided GitHub Action.

### Run SorterBot Cloud locally

#### Build Docker Image
##### With sample model weights
In case you want to start the service without training your own model, there are sample weights (`weights/model_final.pth`) committed to the repository using Git LFS. If you want to use those, build the Docker image with the following command:
```
docker build -t sorterbot_cloud .
```

##### With your own trained model weights
If you want to provide your own trained weights stored in a private S3 bucket, you need to build the image with a command like this:
```
DOCKER_BUILDKIT=1 docker build -t sorterbot_cloud --secret id=aws_config,src=[ABS_PATH_TO_AWS_CONFIG] --secret id=aws_credentials,src=[ABS_PATH_TO_AWS_CREDS] --build-arg WEIGHTS_URL=[S3_URL_OF_WEIGHTS] .
```

`DOCKER_BUILDKIT=1` enables the experimental feature that is needed to mount secrets at build time.

The two `--secret` flags will make sure that the AWS credentials stored in your local system will be available when building the image (so you can use them to authenticate with S3 when downloading the weights), but will not end up in the built image, potentially compromising your AWS account in case you push the image to a public repository. As `ABS_PATH_TO_AWS_CONFIG` and `ABS_PATH_TO_AWS_CREDS`, you need to provide the absolute paths to the `config` and `credentials` files in your `~/.aws` folder. (Create an AWS IAM user with access keys and run `aws configure` in case you don't have the above mentioned files.)

With the `AWS_PROFILE` build argument, you can optionally specify which AWS profile to use for authentication with S3, for example by adding `--build-arg AWS_PROFILE=myprofile`. If you omit this, the default profile will be used.

Lastly, with the `WEIGHTS_URL` build argument, you need to provide the URL from which the weights will be downloaded. The credentials you specified need to provide access to the object you are referencing here. The structure is the following: `s3://[BUCKET_NAME]/[PATH_TO_OBJECT]`. For example: `s3://sorterbot-weights/model_final.pth`.

Full example:
```
DOCKER_BUILDKIT=1 docker build -t sorterbot_cloud --secret id=aws_config,src=/Users/user1/.aws/config --secret id=aws_credentials,src=/Users/user1/.aws/credentials --build-arg MODEL_URL=s3://sorterbot-weights/model_final.pth .
```

#### Run Docker Image
To run the image, you need to provide postgres credentials, and unless you disable it, S3 credentials. You can disable S3 by setting the `DISABLE_AWS` environment variable to 1. If you disable it, the solution will still work, but the processed images will be only saved on the local disk. To provide the postgres credentials, construct a connection string, assign it to `PG_CONN` environment variable either directly with an `-e` flag when running the image, or by saving it to a file and referencing that file with the `--env-file` flag. Use the following format:
```
postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DB_NAME]
```
For example if you are using AWS RDS:
```
postgresql://postgres:mypassword@sorterbot-postgres.cvhafdtrehs4.eu-central-1.rds.amazonaws.com:5432/sorterbot
```
You need to set `--shm-size` to a relatively big value, like 8G to avoid the Docker iamge running out of memory.

For development, it is useful to specify a volume, so you don't have to restart your docker container to pick up changes. You can do that by the `-v` flag, as seen in the example below.

Full example:
```
docker run -p 6000:6000 -v ${PWD}:/sorterbot_cloud --env-file .env --shm-size 8G sorterbot_cloud:latest
```

### Deploy to AWS
You can deploy SorterBot Cloud to AWS as part of the SorterBot service, you can find instructions to do that manually here and fully automated here. (Links coming soon).

### Run Tests
From root folder
```
pytest tests
```
To enable coverage measurement:
```
pytest tests -v \
  --cov=vectorizer.vectorizer \
  --cov=vectorizer.preprocessor \
  --cov=locator.detectron
```

Detectron tests are model specific, after changing the model, the expected values have to be updated for the tests to pass.
To do that:

1. Find `exp_val_detectron` variable in file `mock_data.py`, located in the tests folder. It is a list containing tuples.
2. Make sure that there is a tuple for every test image, and the first element of the tuple corresponds to the test image's filename.
3. Uncomment the line that prints results in function `test_predict` in file `test_detectron.py` located in the tests folder.
4. Run the tests, and after they failed, copy the list of dicts under "Captured stdout call" for each test and paste the result as the second element of the tuples.
5. Rerun the tests and check if they pass.
