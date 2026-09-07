# Development


## Docker image(s)

1. Generate the docker file
```
cd ./docker
.\generate_dockerfile.bat
```

2. Build the docker image
```
docker build -t ghcr.io/vferat/meeg-pipelines:smriprep-0.19.1-dev .   
```

3. [Optional] Push the docker image to GitHub Container Registry
```
docker push ghcr.io/vferat/meeg-pipelines:smriprep-0.19.1-dev
```