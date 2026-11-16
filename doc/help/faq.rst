.. include:: ../links.inc

.. _faq:

Frequently asked questions
==========================

How do I resume a run that crashed?
-----------------------------------

Run the same command again with the same working directory (``-w``). Nipype reuses the
results of the steps that already completed and restarts from the step that failed.
Without ``-w``, the ``forward`` pipeline uses a new temporary working directory at each
run and starts over.

FreeSurfer complains about a missing or invalid license
-------------------------------------------------------

Pass the path to your license file with ``--fs-license-file``. The file is mounted in
the container at ``/opt/freesurfer/license.txt``. A license can be requested for free
on the `FreeSurfer license page <FreeSurfer license_>`_.

The pipeline fails while looking for the fiducials
--------------------------------------------------

The ``forward`` pipeline needs the ``AnatomicalLandmarkCoordinates`` field in the JSON
sidecar of a T1w image (see :ref:`inputs`). Add it with the ``landmarks`` argument of
:func:`mne_bids.write_anat`.

The pipeline is killed without a clear error
--------------------------------------------

The container most likely ran out of memory. Increase the memory available to the
container engine (on Docker Desktop: *Settings → Resources*) or reduce the number of
parallel processes with ``--nprocs``.

Where are the TemplateFlow templates stored?
--------------------------------------------

sMRIPrep downloads spatial templates from `TemplateFlow`_. The ``forward`` command
keeps them in a persistent cache, ``$TEMPLATEFLOW_HOME`` or
``~/.cache/templateflow`` by default, so they are not downloaded again at each run.
Use ``--templateflow-dir`` to choose another folder, for instance a shared folder on a
cluster.

``recon-all`` stops at the Talairach registration
-------------------------------------------------

In rare cases, FreeSurfer falls back to ``mritotal`` to compute the Talairach
registration. ``mritotal`` depends on MINC tools (``mincresample``, ``mincblur``, …)
which are not included in the container image, so this step fails. Check the quality
of the T1w image; if the problem persists, please open an issue (see :ref:`help`).
