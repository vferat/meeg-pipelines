.. include:: ../links.inc

.. _fslabelling:

FreeSurfer labelling pipeline
=============================

The ``fslabelling`` pipeline parcellates a FreeSurfer subject with a surface-based
classifier atlas (FreeSurfer ``.gcs`` files shipped with meegpype). It produces one
``.annot`` file per hemisphere, the corresponding volumetric segmentation, and a lookup
table.

Quick start
-----------

.. code-block:: console

   $ meegpype-wrapper fslabelling sub-01 \
         /path/to/derivatives/meegpype/sourcedata/freesurfer \
         /path/to/derivatives/fslabelling \
         --atlas Schaefer2018_200Parcels_7Networks \
         -w /path/to/work \
         --fs-license-file /path/to/license.txt

The first three arguments are the subject identifier (the ``sub-`` prefix is added if
missing), the FreeSurfer subjects directory containing that subject's ``recon-all``
outputs, and the output directory. ``--atlas`` and ``--fs-license-file`` are required.

Available atlases
-----------------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - ``--atlas``
     - Description
   * - ``desikan_killiany``
     - Desikan-Killiany atlas :footcite:p:`DesikanEtAl2006`.
   * - ``DKTatlas40``
     - Desikan-Killiany-Tourville atlas :footcite:p:`KleinTourville2012`.
   * - ``Schaefer2018_<N>Parcels_<K>Networks``
     - Schaefer 2018 atlas :footcite:p:`SchaeferEtAl2018`, with ``N`` in 100, 200,
       …, 1000 parcels and ``K`` in 7 or 17 networks, e.g.
       ``Schaefer2018_400Parcels_17Networks``.
   * - ``Yeo2011_7Networks``, ``Yeo2011_17Networks``
     - Yeo 2011 resting-state networks :footcite:p:`YeoEtAl2011`.

Outputs
-------

.. code-block:: text

   <output_dir>/
   ├── logs/<date>_<time>/
   └── sub-01/
       └── anat/        # lh/rh annotations, volumetric segmentation and lookup table

Command-line reference
----------------------

.. argparse::
   :module: meegpype_wrapper.entrypoint
   :func: get_parser
   :prog: meegpype-wrapper
   :path: fslabelling

API
---

The pipeline is built from
:func:`~meegpype.workflows.anat.fs_individual_atlas.generate_fs_individual_labelling_workflow`.

References
----------

.. footbibliography::
