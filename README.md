# SorterBot
A deep learning project to control a robotic arm which can place small metallic objects into containers

### Run API locally
From root folder
```
python3 src/main.py
```

### Build Docker Image
```
DOCKER_BUILDKIT=1 docker build -t sorterbot_cloud --secret id=aws_credentials,src=aws_credentials .
```

### Run Docker Image
```
docker run -p 6000:6000 -v /Users/simon/dev/sorterbot_cloud:/sorterbot_cloud --shm-size 8G sorterbot_cloud:latest
sudo docker run -p 6000:6000 -v /home/simon/dev/sorterbot_cloud:/sorterbot_cloud --shm-size 8G sorterbot_cloud:latest
```

### Run Tests
From folder 'src'
```
pytest tests -v \
  --cov=vectorizer.vectorizer \
  --cov=vectorizer.preprocessor \
  --cov=locator.detectron
```
