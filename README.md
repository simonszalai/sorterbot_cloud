# SorterBot
A deep learning project to control a robotic arm which can place small metallic objects into containers

### Run API locally
From root folder
```
python3 src/api.py
```

### Build Docker Image
```
docker build -t sorterbot_cloud .
```

### Run Docker Image
```
docker run -p 6000:6000 -v /Users/simonszalai/dev/sorterbot_cloud:/sorterbot_cloud --shm-size 8G sorterbot_cloud:latest
```

### Run Tests
From folder 'src'
```
python3 -m pytest
```
