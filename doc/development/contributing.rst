.. include:: ../links.inc

.. _contributing:

Contributing
============

Repository layout
-----------------

``meegpype/interfaces``
   `Nipype`_ interfaces wrapping MNE-Python, FreeSurfer, Connectome Workbench and
   custom functions.
``meegpype/workflows``
   Reusable Nipype workflows built from the interfaces.
``meegpype/pipelines`` and ``meegpype/commands``
   The full pipelines and their command-line entry points (``meegpype-forward``,
   ``meegpype-fslr``, ``meegpype-fslabelling``), run inside the container.
``wrapper``
   The ``meegpype-wrapper`` package, which runs the pipeline commands in Docker or
   Apptainer.
``docker``
   Files used to generate and build the container image.
``doc`` and ``tutorials``
   This documentation.

Development setup
-----------------

1. Fork `the repository <project github_>`_ on GitHub, clone your fork, and add the
   main repository as the ``upstream`` remote:

   .. code-block:: console

      $ git clone git@github.com:<your-username>/meeg-pipelines.git
      $ cd meeg-pipelines
      $ git remote add upstream git@github.com:vferat/meeg-pipelines.git

2. Install meegpype and the wrapper in editable mode, in a dedicated environment:

   .. code-block:: console

      $ pip install -e ".[all]"
      $ pip install -e ./wrapper

   The pipelines themselves need FreeSurfer, ANTs and the other neuroimaging tools
   bundled in the container; running them outside the container is not supported.

3. Install the `pre-commit`_ hooks, which run ``ruff``, ``isort``, ``codespell``,
   ``pydocstyle`` and other linters on each commit:

   .. code-block:: console

      $ pre-commit install

4. Create a branch from an up-to-date ``main`` for each pull request:

   .. code-block:: console

      $ git switch main
      $ git pull upstream main
      $ git switch -c my-feature

Running the tests
-----------------

.. code-block:: console

   $ pytest meegpype

Building the documentation
--------------------------

The documentation is built with `Sphinx`_. Building the workflow graphs requires
`Graphviz`_.

.. code-block:: console

   $ pip install -e ".[doc]" ./wrapper
   $ make -C doc html
   $ make -C doc view

``make html`` turns warnings into errors, as the continuous integration does, so fix
any warning before opening a pull request.

Building the container image
----------------------------

The image is based on a fork of the `sMRIPrep`_ image, which includes the FreeSurfer
tools missing from the default sMRIPrep image.

1. Generate the ``Dockerfile`` at the root of the repository with `Neurodocker`_. Run
   the script from the root of the repository:

   .. code-block:: console

      $ ./docker/generate_dockerfile.sh   # docker\generate_dockerfile.bat on Windows

2. Build the image, from the root of the repository:

   .. code-block:: console

      $ docker build -t ghcr.io/vferat/meeg-pipelines:dev .

Changelog
---------

Add an entry describing your change to ``doc/changes/latest.rst``, in the section
that matches its type, and add yourself to ``doc/changes/authors.inc`` if this is your
first contribution.
