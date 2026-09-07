# README

## apptainer

```
pptainer build --sandbox smriprepmeegpype:-0.19.1-dev.sif docker://ghcr.io/vferat/meegpype:smriprep-0.19.1-dev
```

## Commands

```bash
meegpype-docker fslr --atlas subparc374 --fs-license-file ...\license.txt  --nproc 2 sub-01 derivatives\meegpype\sourcedata\freesurfer ...\derivatives\wblabelling
```

```bash
meegpype-docker fslabelling --atlas Schaefer2018_200Parcels_7Networks --fs-license-file ...\license.txt  --nproc 2 sub-01 derivatives\meegpype\sourcedata\freesurfer ...\derivatives\wblabelling
```

```bash
meegpype-docker forward ...  .../derivatives/meegpype participant -w .../derivatives/meegpype/workdir  --fs-license-file ...\license.txt --participant-label sub-01 --n_cpus=12 --volume-src
```