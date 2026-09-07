# Usage

## Forward pipeline

### Docker


The minimal command to run the pipeline is:
```bash
meegpype-wrapper forward PATH_TO_BIDS OUTPUT_DIR participant -w WORKING_DIR --volume-src --fs-license-file PATH_TO_FREESURFER_LICENSE_FILE
```

Additional parameters can be added to the command:
- `--participant-label`: to specify the participant(s) to process (default: all participants)
- `--nprocs`: to specify the number of processes to use (default: 1)
- `--surface-src`: to use surface source space instead of volume source space.
- 

### Apptainer


The command syntax is the same as the docker one, with the addition of the ``--apptainer`` flag:

```bash
meegpype-wrapper forward --apptainer PATH_TO_BIDS OUTPUT_DIR participant -w WORKING_DIR --participant-label 49 --nprocs 12 --volume-src --fs-license-file PATH_TO_FREESURFER_LICENSE_FILE
```


## Labelling pipelines

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
