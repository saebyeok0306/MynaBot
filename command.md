# Command 모음

## python3.10-ffmpeg 배포

1. `docker build -f Dockerfile.image -t python3.10-ffmpeg .`
2. `docker login -u <id>`
3. `docker tag python3.10-ffmpeg westreed/python3.10-ffmpeg:latest`
4. `docker push westreed/python3.10-ffmpeg:latest`