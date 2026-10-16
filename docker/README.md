For error in osvge:

```
--run "micromamba install -y -n smriprep -c conda-forge 'nodejs>=20'  && micromamba clean --all --yes" ^
```


For headless mne
```
--run "micromamba install -y -n smriprep -c conda-forge 'vtk>=9.2=*osmesa*' 'mesalib=21.2.5' && micromamba clean --all --yes" ^
```


## Missing freesurfer functions in default image:

# mritotal

If reconall falls back to mritotal to compute the tailarach registration  (quite rare), it needs the following programs to be installed in the container:
" Manual Talairach alignment may be necessary,"
mritotal
        mritotal: couldn't find program "mincresample"
        mritotal: couldn't find program "mincblur"
        mritotal: couldn't find program "volume_cog"
        mritotal: couldn't find program "minctracc"
        mritotal: couldn't find program "check_scale"
        mritotal: couldn't find program "autocrop"