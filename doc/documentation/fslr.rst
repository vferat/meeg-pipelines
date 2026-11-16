.. include:: ../links.inc

.. _fslr:

fsLR labelling pipeline
=======================

The ``fslr`` pipeline projects an atlas defined on the fsLR 32k surface on a FreeSurfer
subject. The labels are first resampled from fsLR to ``fsaverage`` with
`Connectome Workbench`_ (adaptive barycentric, area-corrected), then mapped to the
subject's surfaces with FreeSurfer's ``mri_surf2surf``. It produces a cortical
parcellation (one ``.annot`` file per hemisphere), the corresponding volumetric
segmentation, and a lookup table.

Quick start
-----------

.. code-block:: console

   $ meegpype-wrapper fslr sub-01 \
         /path/to/derivatives/meegpype/sourcedata/freesurfer \
         /path/to/derivatives/fslr \
         --atlas subparc374 \
         -w /path/to/work \
         --fs-license-file /path/to/license.txt

The first three arguments are the subject identifier (the ``sub-`` prefix is added if
missing), the FreeSurfer subjects directory containing that subject's ``recon-all``
outputs, and the output directory.

Available atlases
-----------------

.. list-table::
   :header-rows: 1

   * - ``--atlas``
     - Description
   * - ``subparc374``
     - The ``subparc374`` cortical atlas, shipped with meegpype.

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
   :path: fslr

API
---

The pipeline is built from
:func:`~meegpype.workflows.anat.wb_labelling.generate_wb_labelling_workflow`.
