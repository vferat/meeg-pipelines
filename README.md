# MEEG pipelines

## Installation

MEEG pipelines are shipped as a docker images and can be run using either docker or apptainer.
To simplify the usage of these pipelines, a wrapper library ``meegpype-wrapper`` is distributed with the docker image.
We recommend to use the wrapper library to run the pipelines, as it will automatically handle the docker/apptainer commands and mount the necessary volumes.

To install the wrapper library, you can use pip:

```bash
pip install -U git+https://github.com/vferat/meeg-pipelines.git#subdirectory=wrapper
```

## Usage

Check the [USE.md](USE.md) file for usage instructions.

## Development

### Create docker file
```bash
generate_dockerfile.sh
```

```cmd
generate_dockerfile.bat
```

### Generate docker image

```cmd
docker build -t meegpype:dev .
```