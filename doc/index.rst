:html_theme.sidebar_secondary.remove:

.. include:: ./links.inc

.. title:: meegpype

meegpype
========

.. rst-class:: h4 text-center font-weight-light my-4

   Containerized, BIDS-based pipelines for M/EEG source modeling, built on
   `MNE-Python <mne stable_>`_, `FreeSurfer`_, `sMRIPrep`_ and `Nipype`_.

meegpype turns a `BIDS`_ dataset into MEG forward models and individual cortical
parcellations with a single command. All dependencies (FreeSurfer, ANTs, MNE-Python,
Connectome Workbench, …) are shipped in a Docker image, so the only things you need
on your machine are a container engine and the small ``meegpype-wrapper`` command-line
tool.

.. code-block:: console

   $ pip install -U "git+https://github.com/vferat/meeg-pipelines.git#subdirectory=wrapper"
   $ meegpype-wrapper forward /path/to/bids /path/to/derivatives participant \
         --participant-label 01 --volume-src --fs-license-file /path/to/license.txt

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: :fas:`download` Install
      :link: install/index
      :link-type: doc

      Requirements, the FreeSurfer license, and how to install the
      ``meegpype-wrapper`` and the container image.

   .. grid-item-card:: :fas:`diagram-project` Pipelines
      :link: documentation/index
      :link-type: doc

      What each pipeline does, which inputs it expects, how to run it, and what it
      writes to the output directory.

   .. grid-item-card:: :fas:`code` API reference
      :link: api/index
      :link-type: doc

      The Nipype interfaces and workflows the pipelines are built from, for
      reuse in your own workflows.

   .. grid-item-card:: :fas:`life-ring` Get help
      :link: help/index
      :link-type: doc

      Frequently asked questions, troubleshooting, and where to report a bug.

.. toctree::
   :hidden:

   Install <install/index>
   Documentation <documentation/index>
   API Reference <api/index>
   Get Help <help/index>
   Development <development/index>
