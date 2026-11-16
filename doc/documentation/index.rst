.. include:: ../links.inc

.. _pipelines:

Pipelines
=========

meegpype provides three pipelines, all run with ``meegpype-wrapper <pipeline>``:

.. grid:: 1 1 3 3
   :gutter: 3

   .. grid-item-card:: Forward model
      :link: forward
      :link-type: ref

      ``meegpype-wrapper forward``

      From a BIDS dataset with MEG and anatomical MRI to Maxwell-filtered MEG data,
      a coregistration, a BEM model, a source space and a forward solution.

   .. grid-item-card:: fsLR labelling
      :link: fslr
      :link-type: ref

      ``meegpype-wrapper fslr``

      Project an atlas defined on the fsLR surface (e.g. ``subparc374``) on a
      FreeSurfer subject.

   .. grid-item-card:: FreeSurfer labelling
      :link: fslabelling
      :link-type: ref

      ``meegpype-wrapper fslabelling``

      Parcellate a FreeSurfer subject with a classifier atlas (Desikan-Killiany,
      DKT, Schaefer 2018, Yeo 2011).

The labelling pipelines start from a FreeSurfer subjects directory, such as the one
produced by the forward pipeline. A typical analysis therefore runs ``forward`` first,
then one of the labelling pipelines on its ``sourcedata/freesurfer`` folder.

.. toctree::
   :hidden:

   inputs
   forward
   fslr
   fslabelling
   ../generated/tutorials/index

Common options
--------------

The following concepts are shared by all pipelines.

Output directory
   Where the results are written. It is created if it does not exist. Each run also
   writes its Nipype logs to ``<output_dir>/logs/<date>_<time>/``.

Working directory (``-w`` / ``--work-dir``)
   Where Nipype stores the intermediate results of every step. Results found in the
   working directory are reused, so **always pass the same working directory to
   resume a run that crashed or to re-run a pipeline with different options**:
   only the steps affected by the change are recomputed. For ``forward``, a temporary
   folder is used when this option is omitted, so nothing is reused between runs. Once
   you are satisfied with the outputs, the working directory can be deleted.

Number of processes (``--nprocs``)
   Maximum number of processes run in parallel by Nipype (default: 1). Aliases:
   ``--nthreads``, ``--n-cpus``, ``--n_cpus``.

FreeSurfer license (``--fs-license-file``)
   Path to your FreeSurfer license file, mounted in the container (see :ref:`install`).

Container engine (``--engine``, ``forward`` only)
   ``docker`` (default) or ``apptainer``. The ``fslr`` and ``fslabelling`` commands
   currently only support Docker; see :ref:`containers` to run them with Apptainer.

Additional arguments
   Options that the wrapper does not know are passed unchanged to the pipeline
   command inside the container.
