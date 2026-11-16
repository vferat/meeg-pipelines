.. include:: ../links.inc

.. _inputs:

Preparing the input dataset
===========================

The ``forward`` pipeline takes a `BIDS`_ dataset as input. The dataset is indexed with
`PyBIDS`_ and the MEG files are matched with `MNE-BIDS <mne bids_>`_, so a dataset
written with :func:`mne_bids.write_raw_bids` and :func:`mne_bids.write_anat` is the
easiest way to get started.

What the pipeline looks for
---------------------------

For each participant (``sub-<label>``), optionally split in sessions (``ses-<label>``):

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - File
     - Required
     - Notes
   * - ``anat/*_T1w.nii[.gz]``
     - yes
     - All T1-weighted images are passed to sMRIPrep and FreeSurfer.
   * - ``anat/*_T1w.json`` with ``AnatomicalLandmarkCoordinates``
     - yes
     - The LPA, nasion and RPA fiducials, in voxel coordinates of that T1w image.
       They initialize the MEG ↔ MRI coregistration. Use the ``landmarks`` argument
       of :func:`mne_bids.write_anat` to write them.
   * - ``anat/*_T2w.nii[.gz]``, ``anat/*_FLAIR.nii[.gz]``
     - no
     - Used by FreeSurfer to refine the pial surface when available.
   * - ``meg/*_meg.fif``
     - yes
     - Every MEG FIF recording of the session, except ``task-noise`` recordings and
       ``acq-crosstalk`` files. Each run is processed and Maxwell filtered.
   * - ``meg/*_acq-crosstalk_meg.fif``, ``meg/*_acq-calibration_meg.dat``
     - recommended
     - The MEGIN cross-talk and fine-calibration files, used by the Maxwell filter.
   * - Empty-room recording
     - recommended
     - Found with :meth:`mne_bids.BIDSPath.find_empty_room` (``sub-emptyroom`` or
       the ``AssociatedEmptyRoom`` sidecar field) and processed like the
       participant data. ``sub-emptyroom`` is never processed as a participant.

.. note::

   The ``forward`` pipeline is designed for MEGIN (Elekta/Neuromag) MEG data in FIF
   format recorded with continuous head position indicators (cHPI): head positions
   are estimated from the cHPI coils for movement compensation.

Example layout
--------------

.. code-block:: text

   bids/
   ├── dataset_description.json
   ├── participants.tsv
   ├── sub-01/
   │   └── ses-01/
   │       ├── anat/
   │       │   ├── sub-01_ses-01_T1w.nii.gz
   │       │   └── sub-01_ses-01_T1w.json      # AnatomicalLandmarkCoordinates
   │       └── meg/
   │           ├── sub-01_ses-01_task-rest_meg.fif
   │           ├── sub-01_ses-01_task-rest_meg.json
   │           ├── sub-01_ses-01_acq-crosstalk_meg.fif
   │           └── sub-01_ses-01_acq-calibration_meg.dat
   └── sub-emptyroom/
       └── ses-20240101/
           └── meg/
               └── sub-emptyroom_ses-20240101_task-noise_meg.fif

Validate your dataset with the `BIDS validator`_ before running the pipeline.
