For error in osvge:

```
--run "micromamba install -y -n smriprep -c conda-forge 'nodejs>=20'  && micromamba clean --all --yes" ^
```


For headless mne
```
--run "micromamba install -y -n smriprep -c conda-forge 'vtk>=9.2=*osmesa*' 'mesalib=21.2.5' && micromamba clean --all --yes" ^
```