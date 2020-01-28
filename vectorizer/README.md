### Build Docker Image
docker build vectorizer:latest

### Run Docker Image
docker run -v /Users/simonszalai/dev/sorterbot/vectorizer:/vectorizer --shm-size 8G vectorizer:latest