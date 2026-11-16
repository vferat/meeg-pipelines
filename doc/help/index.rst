.. include:: ../links.inc

.. _help:

Getting help
============

.. toctree::
   :hidden:

   faq

Start with the :ref:`faq`, which covers the most common problems. If your question is
not answered there, open an issue on the `GitHub issue tracker <project issues_>`_.

When reporting a problem, please include:

- the full ``meegpype-wrapper`` command you ran, and the container command it printed
  (the line starting with ``Running command:``);
- the error message, and the Nipype crash file if one was written (its path is
  printed in the error, and it can be read with ``nipypecli crash <file>``);
- the logs found in ``<output_dir>/logs/``;
- your operating system and container engine (Docker or Apptainer) with its version.
