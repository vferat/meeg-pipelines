.. include:: ../links.inc

.. _install:

Installation
============

meegpype is distributed as a container image,
``ghcr.io/vferat/meeg-pipelines:main``, which bundles every neuroimaging dependency
(FreeSurfer, ANTs, MNE-Python, Connectome Workbench, …). The recommended way to run it
is through ``meegpype-wrapper``, a lightweight Python command-line tool that builds the
``docker run`` / ``apptainer exec`` command for you: it mounts your folders in the
container, passes the FreeSurfer license, and forwards the pipeline options.

.. toctree::
   :hidden:

   containers

Requirements
------------

.. grid:: 1 1 3 3
   :gutter: 3

   .. grid-item-card:: :fab:`docker` Container engine

      `Docker`_ on a workstation, or `Apptainer`_ (formerly Singularity) on an HPC
      cluster where Docker is usually not available.

   .. grid-item-card:: :fab:`python` Python ≥ 3.9

      Only needed to install and run ``meegpype-wrapper``, which has no
      neuroimaging dependency.

   .. grid-item-card:: :fas:`key` FreeSurfer license

      FreeSurfer requires a free license file. Request one on the
      `FreeSurfer license page <FreeSurfer license_>`_.

.. note::

   The pipelines run FreeSurfer's ``recon-all`` and are memory and CPU intensive.
   Plan for several hours of compute per participant and make sure the container
   engine is allowed to use enough memory (on Docker Desktop, check
   *Settings → Resources*).

Install the wrapper
-------------------

Install ``meegpype-wrapper`` with ``pip`` directly from GitHub, ideally in a dedicated
virtual environment:

.. code-block:: console

   $ pip install -U "git+https://github.com/vferat/meeg-pipelines.git#subdirectory=wrapper"

Check that the command is available:

.. code-block:: console

   $ meegpype-wrapper --help

You do not need to download the container image yourself:

- with Docker, the ``forward`` command runs ``docker run --pull=always``, so the latest
  image is pulled automatically before each run;
- with Apptainer, the image is fetched from ``docker://ghcr.io/vferat/meeg-pipelines:main``
  and converted on the first run.

To download the image ahead of time, for instance on a machine with a fast connection,
see :ref:`containers`.

Update
------

Run the ``pip install -U`` command above again to update the wrapper. With Docker, the
image is updated at the next ``forward`` run. To update it manually:

.. code-block:: console

   $ docker pull ghcr.io/vferat/meeg-pipelines:main

Next steps
----------

Head to :ref:`pipelines` to choose a pipeline and run it on your data.
