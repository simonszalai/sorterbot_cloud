### Build Docker Image
docker build -t sorterbot_api .

### Run Docker Image
docker run -p 6000:6000 -v /Users/simonszalai/dev/sorterbot/api:/api --shm-size 8G sorterbot_api:latest