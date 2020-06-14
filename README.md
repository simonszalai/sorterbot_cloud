# SorterBot Cloud
*Note: This repository is still work in progress!*

Inference engine for the SorterBot project, which contains the neural networks and other compute-heavy tasks needed for image processing. It can be run locally as a Docker container, and can be easily deployed to AWS ECS by using the provided GitHub Action.

### Architecture
#### Part 1: Object Recognition
This part of the Inference engine is called once for every image taken by the camera. After the image is taken, it is sent directly to the Inference engine as raw bytes. The image then is used as the input of the [Detectron2](https://github.com/facebookresearch/detectron2) object recognition network, which outputs the coordinates of the recognized objects. Finally the coordinates are saved to the PostgreSQL database. After all the images in a session have been processed, a trigger is sent to activate the Vectorizer network, which is explained in the next paragraph.

![Alt SorterBot Cloud Object Recognition Diagram](./media/object_recognition_diagram.svg)
*<p align="center">Figure 1: Diagram of the Object Recognizer ([Full Diagram](https://www.figma.com/file/OWlAFKX1pEIHMfKRnWXOpQ/SorterBot?node-id=0%3A1))</p>*

#### Part 2: Vectorizer
After the above mentioned trigger is received, all the objects are loaded from the database that belong to the current session. First, the coordinates relative to the frames of their respective images are converted to absolute polar coordinates, relative to the robotic arm. Since one object often shows up on multiple images, duplicates needs to be filtered. Coordinates of objects that show up multiple times are replaced with the averages of the positions. 

Next, the images are loaded from disk, and every object gets cropped around their bounding boxes. These cropped images are converted to tensors and used as inputs to the Vectorizer network, which is a ResNet18 network pretrained on ImageNet. For efficiency, the images are processed in a batch. The outputs of the layer before the last are copied, so each image is represented as a 512 dimensional vector. The network also classifies the images as object or container.

The image vectors and the number of containers are used as the inputs of the K-Means clustering algorithm. The images are grouped to as many clusters as many containers were found.

Lastly, based on the pairings computed above, commands are generated which are directly executable by the robotic arm.

![Alt SorterBot Cloud Vectorizer Diagram](./media/vectorizer_diagram.svg)
*<p align="center">Figure 2: Diagram of the Vectorizer ([Full Diagram](https://www.figma.com/file/OWlAFKX1pEIHMfKRnWXOpQ/SorterBot?node-id=0%3A1))</p>*

### Development Locally

1. Build Docker Image
  
    #### Option A: With sample model weights
    In case you want to start the service without training your own model, there are sample weights (`weights/model_final.pth`) committed to the repository using Git LFS. If you want to use those, build the Docker image with the following command (make sure to `cd` to the root folder of the repository, or change the . to the correct path):
    ```
    docker build -t sorterbot_cloud .
    ```

    #### Option B: With your own trained model weights
    If you want to provide your own trained weights stored in a private S3 bucket, you need to build the image with a command like this:
    ```
    DOCKER_BUILDKIT=1 docker build -t sorterbot_cloud --secret id=aws_config,src=[ABS_PATH_TO_AWS_CONFIG] --secret id=aws_credentials,src=[ABS_PATH_TO_AWS_CREDS] --build-arg WEIGHTS_URL=[S3_URL_OF_WEIGHTS] .
    ```

    - `DOCKER_BUILDKIT=1` enables the experimental Docker feature that is needed to mount secrets at build time.

    - The two `--secret` flags will make sure that the AWS credentials stored in your local system will be available when building the image (so you can use them to authenticate with S3 when downloading the weights), but will not end up in the built image, potentially compromising your AWS account in case you push the image to a public repository. As for `ABS_PATH_TO_AWS_CONFIG` and `ABS_PATH_TO_AWS_CREDS`, you need to provide the absolute paths to the `config` and `credentials` files in your `~/.aws` folder. (Create an AWS IAM user with S3 access and access keys, and run `aws configure` in case you don't have the above mentioned files.)

    - With the optional `AWS_PROFILE` build argument, you can specify which AWS profile to use for authentication with S3, for example by adding `--build-arg AWS_PROFILE=myprofile`. If you omit this, the default profile will be used. This can be useful if you already have AWS credentials configured in your system and you don't want to overwrite them.

    - Lastly, for the `WEIGHTS_URL` build argument, you need to provide the URL from which the weights will be downloaded. The IAM user you specified need to have read access to the object you are referencing here. The structure is the following: `s3://[BUCKET_NAME]/[PATH_TO_OBJECT]`. For example: `s3://sorterbot-weights/model_final.pth`.

    Full example:
    ```
    DOCKER_BUILDKIT=1 docker build -t sorterbot_cloud --secret id=aws_config,src=/Users/user1/.aws/config --secret id=aws_credentials,src=/Users/user1/.aws/credentials --build-arg MODEL_URL=s3://sorterbot-weights/model_final.pth .
    ```

1. For the logs to be sent over HTTP to the Control Panel, you need to specify the Control Panel host as the `CONTROL_PANEL_HOST` environment variable. If you are on Mac, you can use `docker.for.mac.host.internal:8000`, but if you are on Linux, you need to find the IP Address of your container. To do that:
   1. Start the SorterBot Control Panel container as described in the [Control Panel's README](https://github.com/simonszalai/sorterbot_control).
   1. After your Control Panel container started, run `docker ps`, and copy the CONTAINER ID of the Docker container that runs the Control Panel.
   1. Run `docker inspect [CONTAINER ID]`, and in the output, find `NetworkSettings.Networks.bridge.IPAddress`. Assign this IP to the `CONTROL_PANEL_HOST` environment variable.

2. Run Docker Image
   
    You can run the image in 3 modes: *local*, *aws-dev*, and *production*. This container behaves the same way in *aws-dev* and *production* modes, but in *local* mode, the created pictures will not be uploaded to S3. You can specify the mode by setting the `MODE` environment variable to one of the values mentioned above.

    To run the image, you need to provide PostgreSQL credentials. To do that, construct a connection string, assign it to the `PG_CONN` environment variable, either directly with an `-e` flag when running the image, or by saving it to a file and referencing that file with the `--env-file` flag. Use the following format:
    ```
    postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DB_NAME]
    ```
    For example if you are using AWS RDS:
    ```
    postgresql://postgres:mypassword@sorterbot-postgres.cvhafdtrehs4.eu-central-1.rds.amazonaws.com:5432/sorterbot
    ```
    You need to set `--shm-size` to a relatively big value, like 8G to avoid the Docker image running out of shared memory.

    #### *local* mode

    For development, it is useful to specify a volume, so you don't have to rebuild your docker container to pick up changes. You can do that by the `-v` flag, as shown in the example below.

    Full example:
    ```
    docker run -p 6000:6000 -v ${PWD}:/sorterbot_cloud --env-file .env --shm-size 8G sorterbot_cloud:latest
    ```
    This command works if run from the root of this project `(sorterbot_cloud)`, if you run it from another location, make sure to change the path in the -v flag, before the :. 

    #### *aws-dev* mode
  
    If you are running the container in *aws-dev* mode, you need to make available your `.aws` folder within the container. Within that folder, the configured 'default' profile has to provide full S3 access, and also the `ssm:GetParameter` permission. To do that, specify another volume: `-v ~/.aws:/root/.aws`. That makes the full example the following:
    ```
    docker run -p 6000:6000 -v ${PWD}:/sorterbot_cloud -v ~/.aws:/root/.aws --env-file .env --shm-size 8G sorterbot_cloud:latest
    ```
    
    #### *production* mode
    Only used in production, see the section below.

### Deploy to Production
You can deploy SorterBot Cloud to AWS as part of the SorterBot solution. Please refer to the [Production section of the SorterBot Installer](https://github.com/simonszalai/sorterbot_installer#production) repository's README.

### Run Tests locally
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

### Generate Documentation
1. Install Sphinx and the RTD theme using pip:
    ```
    pip install sphinx sphinx-rtd-theme
    ```
1. Run the bash script to build the documentation HTML (from `docs` folder):
    ```
    ./build_docs.sh
    ```
1. The built HTML page will be saved in the `docs` folder, where GitHub Pages can automatically serve it. Commit the built files, push them, and you can access the documentation page at `https://[GITHUB_USER_NAME].github.io/sorterbot_cloud`
1. In case you want to clear the built files, you can do that by running the following command in the `docs` folder:
    ```
    ./clear_docs.sh
    ```
