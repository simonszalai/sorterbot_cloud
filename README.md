# SorterBot
A deep learning project to control a robotic arm which can place small metallic objects into containers

### Run API locally
From root folder
```
python3 src/main.py
```

### Build Docker Image
```
DOCKER_BUILDKIT=1 docker build -t sorterbot_cloud --secret id=aws_config,src=/Users/simon/.aws/config --secret id=aws_credentials,src=/Users/simon/.aws/credentials .
```

### Run Docker Image
```
docker run -p 6000:6000 -v /Users/simon/dev/sorterbot_cloud:/sorterbot_cloud -v ~/.aws:/root/.aws--shm-size 8G sorterbot_cloud:latest
sudo docker run -p 6000:6000 -v /home/simon/dev/sorterbot_cloud:/sorterbot_cloud -v ~/.aws:/root/.aws --shm-size 8G sorterbot_cloud:latest
```

### Run Tests
From root folder
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
