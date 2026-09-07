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

### Forward pipeline

#### Docker

The minimal command to run the pipeline is:
```bash
meegpype-wrapper forward PATH_TO_BIDS OUTPUT_DIR participant -w WORKING_DIR --volume-src --fs-license-file PATH_TO_FREESURFER_LICENSE_FILE
```
where:
- `PATH_TO_BIDS` is the path to the BIDS dataset
- `OUTPUT_DIR` is the path to the output directory where the results will be stored
- `WORKING_DIR` is the path to the working directory where intermediate files will be stored [optional]
- `PATH_TO_FREESURFER_LICENSE_FILE` is the path to the FreeSurfer license file needed to run the FreeSurfer commands.

Additional parameters can be added to the command:
- `--participant-label`: to specify the participant(s) to process (default: all participants)
- `--nprocs`: to specify the number of processes to use (default: 1)
- `--surface-src` instead of `--volume-src`: to use surface source space instead of volume source space.
- `--pos`: when using a volume source space ( `--volume-src` flag), define the grid spacing in millimeters (default: 5mm).


#### Apptainer

The command syntax is the same as the docker one, with the addition of the ``--apptainer`` flag:
```bash
meegpype-wrapper forward --apptainer PATH_TO_BIDS OUTPUT_DIR participant -w WORKING_DIR --volume-src --fs-license-file PATH_TO_FREESURFER_LICENSE_FILE
```


### Labelling pipelines

### Docker

```bash
meegpype-wrapper fslr --atlas subparc374 --fs-license-file ...\license.txt  --nproc 2 sub-01 derivatives\meegpype\sourcedata\freesurfer ...\derivatives\wblabelling
```

```bash
meegpype-wrapper fslabelling --atlas Schaefer2018_200Parcels_7Networks --fs-license-file ...\license.txt  --nproc 2 sub-01 derivatives\meegpype\sourcedata\freesurfer ...\derivatives\wblabelling
```

```bash
meegpype-wrapper forward ...  .../derivatives/meegpype participant -w .../derivatives/meegpype/workdir  --fs-license-file ...\license.txt --participant-label sub-01 --n_cpus=12 --volume-src
```