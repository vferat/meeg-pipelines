.. include:: ../links.inc

.. _forward:

Forward model pipeline
======================

The forward pipeline goes from raw MEG recordings and anatomical MRI in a BIDS dataset
to the files needed for source imaging with MNE-Python: Maxwell-filtered data, the
MEG ↔ MRI transformation, the BEM model, the source space and the forward solution,
together with an HTML report per session.

Quick start
-----------

.. code-block:: console

   $ meegpype-wrapper forward /path/to/bids /path/to/derivatives/meegpype participant \
         --participant-label 01 \
         -w /path/to/work \
         --volume-src \
         --fs-license-file /path/to/license.txt \
         --nprocs 8

Use ``--engine apptainer`` to run with Apptainer instead of Docker. The input dataset
must follow the conventions described in :ref:`inputs`.

Processing steps
----------------

The following steps are run for each participant.

1. **Anatomical preprocessing** with `sMRIPrep`_: brain extraction, spatial
   normalization to ``MNI152NLin2009cAsym`` and ``fsaverage5``, and FreeSurfer
   ``recon-all``. The FreeSurfer subjects directory is
   ``<output_dir>/sourcedata/freesurfer``; ``fsaverage`` is copied in it.
2. **Fiducials**: the anatomical landmarks of the T1w sidecar are moved to the
   FreeSurfer space of the participant
   (:func:`~meegpype.workflows.anat.fiducials.init_fiducials_wf`).
3. **BEM surfaces** (:func:`~meegpype.workflows.anat.bem.generate_bem_workflow`),
   selected with ``--bem-method``:

   - ``basic`` (default): the brain, inner skull, outer skull and outer skin surfaces
     from the FreeSurfer watershed algorithm (:func:`mne.bem.make_watershed_bem`);
   - ``refined``: the brain and inner skull surfaces are instead derived from the
     FreeSurfer brain mask (marching cubes, smoothing, decimation to 5120 triangles,
     then expansion by 1 mm and 2 mm). The outer skull and skin still come from the
     watershed algorithm.

   A single-layer BEM model (inner skull, conductivity 0.3 S/m) is computed from
   these surfaces.
4. **Source space**, selected with ``--surface-src`` and/or ``--volume-src``
   (pass at least one):

   - surface: ``oct6`` spacing on the white matter surface;
   - volume: a grid with ``--pos`` mm spacing (default: 5 mm), restricted to the
     cerebral and cerebellar cortex, thalamus, putamen, pallidum, hippocampus,
     amygdala and nucleus accumbens of both hemispheres;
   - both flags: the two source spaces are combined.
5. **Maxwell filtering**, for each session
   (:func:`~meegpype.workflows.meg.maxwell.init_maxwell_wf`): head positions are
   estimated from the cHPI coils, cHPI and line noise are filtered, noisy and flat
   channels are detected with :func:`mne.preprocessing.find_bad_channels_maxwell`,
   and every run is Maxwell filtered (tSSS with a 30 s window and a 0.98 correlation
   limit, with movement compensation). All runs of a session are transformed to a
   common head position, the average across runs. The empty-room recording is
   processed with the same settings.
6. **Coregistration**: the MEG ↔ MRI transformation is fitted on the fiducials, then
   refined with ICP on the digitized head shape points (points further than 5 mm from
   the scalp are excluded).
7. **Forward solution** computed from the Maxwell-filtered measurement info, the
   coregistration, the BEM model and the source space.
8. **Report**: an :class:`mne.Report` showing the Maxwell-filtered data, the head
   positions, the coregistration and the forward solution.

Outputs
-------

.. code-block:: text

   <output_dir>/
   ├── logs/<date>_<time>/              # Nipype logs and workflow graph
   ├── sourcedata/
   │   └── freesurfer/                  # FreeSurfer subjects directory
   │       ├── fsaverage/
   │       └── sub-01/                  # recon-all outputs and BEM surfaces (bem/)
   └── sub-01/
       ├── anat/                        # preprocessed T1w, brain mask and transforms
       └── ses-01/
           └── meg/                     # Maxwell-filtered runs and empty-room,
                                        # forward.fif and the HTML report

For datasets without sessions, the ``meg`` folder is directly in ``sub-01/``.

The ``sourcedata/freesurfer`` folder can be used as input to the :ref:`fslr` and
:ref:`fslabelling` pipelines.

Command-line reference
----------------------

.. argparse::
   :module: meegpype_wrapper.entrypoint
   :func: get_parser
   :prog: meegpype-wrapper
   :path: forward
