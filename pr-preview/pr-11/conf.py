# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from __future__ import annotations  # c.f. PEP 563, PEP 649

import inspect
import subprocess
import sys
from datetime import date
from importlib import import_module
from typing import TYPE_CHECKING

from intersphinx_registry import get_intersphinx_mapping
from sphinx_gallery.sorting import FileNameSortKey

import meegpype

if TYPE_CHECKING:
    from typing import Optional

# -- project information ---------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "meegpype"
author = "Victor Ferat"
copyright = f"{date.today().year}, {author}"
release = meegpype.__version__
package = meegpype.__name__
gh_url = "https://github.com/vferat/meeg-pipelines"
gh_pages_url = "https://vferat.github.io/meeg-pipelines/"

# -- general configuration -------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "5.0"

# The document name of the “root” document, that is, the document that contains the root
# toctree directive.
root_doc = "index"

# Add any Sphinx extension module names here, as strings. They can be extensions coming
# with Sphinx (named "sphinx.ext.*") or your custom ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinx.ext.mathjax",
    "nipype.sphinxext.apidoc",
    "nipype.sphinxext.documenter",
    "sphinxcontrib.bibtex",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_gallery.gen_gallery",
    "sphinx_issues",
    "myst_parser",
    "sphinxarg.ext",
    "sphinxcontrib.apidoc",
    "nipype.sphinxext.plot_workflow",
]

# -- apidoc (one page per module, like niworkflows) ------------------------------------
apidoc_module_dir = "../meegpype"
apidoc_output_dir = "api"
apidoc_excluded_paths = [
    "commands",
    "data",
    "utils",
    "conftest.py",
    "_version.py",
    "**/tests",
]
apidoc_template_dir = "_templates/apidoc"
apidoc_separate_modules = True
apidoc_module_first = True
apidoc_extra_args = ["-d 1", "-T"]

# -- nipype workflow graphs ------------------------------------------------------------
plot_formats = [("png", 100)]
wf_graph_options = {"graph2use": "orig", "simple_form": True}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# Sphinx will warn about all references where the target cannot be found.
nitpicky = True
nitpick_ignore = []
# Nipype internals that are not in its inventory.
nitpick_ignore_regex = [
    (r"py:.*", r"nipype\.interfaces\..*"),
    ("py:obj", "command"),
]

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = [f"{package}."]

# The name of a reST role (builtin or Sphinx extension) to use as the default role, that
# is, for text marked up `like this`. This can be set to 'py:obj' to make `filter` a
# cross-reference to the Python function “filter”.
default_role = "py:obj"

# list of warning types to suppress
suppress_warnings = ["config.cache", "app.add_directive"]

# -- options for HTML output -----------------------------------------------------------
html_css_files = [
    "css/style.css",
]
html_permalinks_icon = "🔗"
html_show_sphinx = False
html_static_path = ["_static"]
html_theme = "pydata_sphinx_theme"
html_title = project

version_match = "dev" if "dev" in release else release

# Documentation to change footer icons:
# https://pradyunsg.me/furo/customisation/footer/#changing-footer-icons
html_theme_options = {
    "switcher": {
    "json_url": f"{gh_pages_url}dev/_static/switcher.json",
    "version_match": version_match,
    },
    "navbar_end": ["theme-switcher", "version-switcher"],
    "footer_start": ["copyright"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": gh_url,
            "icon": "fab fa-github-square",
        },
    ],
}

# -- autosummary -----------------------------------------------------------------------
autosummary_generate = True

# -- autodoc ---------------------------------------------------------------------------
autodoc_typehints = "none"
autodoc_member_order = "groupwise"
autodoc_warningiserror = True
autoclass_content = "class"

# -- intersphinx -----------------------------------------------------------------------
intersphinx_mapping = get_intersphinx_mapping(
    packages={"matplotlib", "mne", "numpy", "pandas", "python", "scipy"}
)
intersphinx_mapping["nipype"] = ("https://nipype.readthedocs.io/en/latest/", None)
intersphinx_timeout = 5

# -- sphinx-issues ---------------------------------------------------------------------
issues_github_path = gh_url.split("https://github.com/")[-1]

# -- autosectionlabels -----------------------------------------------------------------
autosectionlabel_prefix_document = True

# -- napoleon --------------------------------------------------------------------------
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = False
# Render nipype-style sections like numpy "Parameters".
napoleon_custom_sections = [
    ("Inputs", "Parameters"),
    ("Outputs", "Parameters"),
    ("Attributes", "Parameters"),
    ("Mandatory Inputs", "Parameters"),
    ("Optional Inputs", "Parameters"),
]

# -- sphinxcontrib-bibtex --------------------------------------------------------------
bibtex_bibfiles = ["./references.bib"]

# -- sphinx.ext.linkcode ---------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html


def linkcode_resolve(domain: str, info: dict[str, str]) -> Optional[str]:
    """Determine the URL corresponding to a Python object.

    Parameters
    ----------
    domain : str
        One of 'py', 'c', 'cpp', 'javascript'.
    info : dict
        With keys "module" and "fullname".

    Returns
    -------
    url : str | None
        The code URL. If None, no link is added.
    """
    if domain != "py":
        return None  # only document python objects

    # retrieve pyobject and file
    try:
        module = import_module(info["module"])
        pyobject = module
        for elt in info["fullname"].split("."):
            pyobject = getattr(pyobject, elt)
        fname = inspect.getsourcefile(pyobject).replace("\\", "/")
    except Exception:
        # Either the object could not be loaded or the file was not found.
        # For instance, properties will raise.
        return None

    # retrieve start/stop lines
    source, start_line = inspect.getsourcelines(pyobject)
    lines = "L%d-L%d" % (start_line, start_line + len(source) - 1)

    # create URL
    if "dev" in release:
        branch = "main"
    else:
        return None  # alternatively, link to a maint/version branch
    fname = fname.rsplit(f"/{package}/")[1]
    url = f"{gh_url}/blob/{branch}/{package}/{fname}#{lines}"
    return url


# -- sphinx-gallery --------------------------------------------------------------------
if sys.platform.startswith("win"):
    try:
        subprocess.check_call(["optipng", "--version"])
        compress_images = ("images", "thumbnails")
    except Exception:
        compress_images = ()
else:
    compress_images = ("images", "thumbnails")

sphinx_gallery_conf = {
    "backreferences_dir": "generated/backreferences",
    "compress_images": compress_images,
    "doc_module": (f"{package}",),
    "examples_dirs": ["../tutorials"],
    "exclude_implicit_doc": {},  # set
    "filename_pattern": r"\d{2}_",
    "gallery_dirs": ["generated/tutorials"],
    "line_numbers": False,
    "plot_gallery": "True",  # str, to enable overwrite from CLI without warning
    "reference_url": {f"{package}": None},
    "remove_config_comments": True,
    "show_memory": True,
    "within_subsection_order": FileNameSortKey,
}

# -- linkcheck -------------------------------------------------------------------------
linkcheck_anchors = False  # saves a bit of time
linkcheck_timeout = 15  # some can be quite slow
linkcheck_retries = 3
linkcheck_ignore = []  # will be compiled to regex

# -- sphinx_copybutton -----------------------------------------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
