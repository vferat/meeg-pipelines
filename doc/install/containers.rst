.. include:: ../links.inc

.. _containers:

Using the container directly
============================

``meegpype-wrapper`` is a thin layer over the container engine. If you prefer to call
Docker or Apptainer yourself, for instance from a job script on a cluster, this page
shows what the wrapper does under the hood. The wrapper prints the full command it runs,
which is a good starting point.

Pull the image
--------------

.. tab-set::

   .. tab-item:: Docker

      .. code-block:: console

         $ docker pull ghcr.io/vferat/meeg-pipelines:main

   .. tab-item:: Apptainer

      Build a local ``.sif`` file once, and reuse it for all runs:

      .. code-block:: console

         $ apptainer build meegpype.sif docker://ghcr.io/vferat/meeg-pipelines:main

Mount points
------------

The pipeline commands inside the container (``meegpype-forward``, ``meegpype-fslr`` and
``meegpype-fslabelling``) receive paths *inside* the container. The wrapper mounts your
folders on the following locations:

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - Host folder
     - Container path
     - Used by
   * - BIDS dataset
     - ``/data``
     - ``forward``
   * - FreeSurfer subjects directory
     - ``/subjects_dir``
     - ``fslr``, ``fslabelling``
   * - Output directory
     - ``/out``
     - all
   * - Working directory
     - ``/scratch``
     - all
   * - FreeSurfer license file
     - ``/opt/freesurfer/license.txt``
     - all
   * - TemplateFlow cache
     - ``/opt/templateflow``
     - ``forward``

Example: forward pipeline
-------------------------

.. tab-set::

   .. tab-item:: Docker

      .. code-block:: console

         $ docker run --rm \
               -v /path/to/bids:/data \
               -v /path/to/derivatives:/out \
               -v /path/to/work:/scratch \
               -v ~/.cache/templateflow:/opt/templateflow \
               -e TEMPLATEFLOW_HOME=/opt/templateflow \
               -v /path/to/license.txt:/opt/freesurfer/license.txt \
               ghcr.io/vferat/meeg-pipelines:main \
               meegpype-forward /data /out participant --work-dir /scratch \
               --participant-label 01 --volume-src

   .. tab-item:: Apptainer

      With Apptainer, the image entrypoint is not run automatically: call
      ``/usr/local/bin/entrypoint.sh`` explicitly, as it sets up the environment
      (FreeSurfer, headless rendering for the reports).

      .. code-block:: console

         $ apptainer exec --cleanenv --containall --writable-tmpfs \
               -B /path/to/bids:/data \
               -B /path/to/derivatives:/out \
               -B /path/to/work:/scratch \
               -B ~/.cache/templateflow:/opt/templateflow \
               --env TEMPLATEFLOW_HOME=/opt/templateflow \
               -B /path/to/license.txt:/opt/freesurfer/license.txt \
               --env FS_LICENSE=/opt/freesurfer/license.txt \
               meegpype.sif \
               /usr/local/bin/entrypoint.sh \
               meegpype-forward /data /out participant --work-dir /scratch \
               --participant-label 01 --volume-src

Development images
------------------

To build the image yourself, see :ref:`contributing`.
