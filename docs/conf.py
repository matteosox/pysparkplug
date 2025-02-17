"""
Configuration file for the Sphinx documentation builder.

For a full list of confiuration options, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import datetime
import doctest
import importlib.metadata
import os
import sys

from packaging.version import Version

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Setup sys.path so we can import other modules
sys.path.append(REPO_ROOT)

from docs import linkcode  # noqa: E402

# -- Project information -----------------------------------------------------

project = "PySparkplug"
author = "Matt Fay"
copyright = f"2023-{datetime.datetime.now().year}, {author}"

# The full version, including alpha/beta/rc tags
release = importlib.metadata.version("pysparkplug")
_version = Version(release)
version = f"{_version.major}.{_version.minor}.{_version.micro}"

# -- General configuration ---------------------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ["templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# Pygments style to use for highlighting when the CSS media query
# (prefers-color-scheme: dark) evaluates to true.
pygments_dark_style = "monokai"

# Sphinx warns about all references where the target cannot be found, except
# those explicitly ignored.
nitpicky = True
nitpick_ignore = [
    ("py:class", "pysparkplug._payload._Cmd"),
    ("py:class", "pysparkplug._payload._Data"),
    ("py:class", "pysparkplug._payload.Birth"),
    ("py:class", "pysparkplug._payload.Payload"),
    ("py:class", "pysparkplug._strenum.StrEnum"),
    ("py:class", "sparkplug_b_pb2.Metric"),
    ("py:class", "sparkplug_b_pb2.MetaData"),
    ("py:class", "ssl._SSLMethod"),
]

# -- Extension configuration -------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "notfound.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinxext.opengraph",
]

# Document everything in __all__
autosummary_ignore_module_all = False

# Show typehints as content of the function or method The typehints of
# overloaded functions or methods will still be represented in the
# signature.
autodoc_typehints = "description"

# A dictionary for users defined type aliases that maps a type name to
# the full-qualified object name.
autodoc_type_aliases = {}

# Add links to modules and objects in the Python standard library documentation
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "paho.mqtt": ("https://eclipse.dev/paho/files/paho.mqtt.python/html/", None),
}

# Default flags for testing `doctest` directives used by the
# `sphinx.ext.doctest` Sphinx extension
doctest_default_flags = doctest.DONT_ACCEPT_TRUE_FOR_1 | doctest.ELLIPSIS

# Auto-generate Header Anchors
myst_heading_anchors = 4

# We don't need warnings about non-consecutive header level
suppress_warnings = ["myst.header"]

# The `sphinx.ext.linkcode` extension returns the URL to source code
# corresponding to the object referenced.
linkcode_resolve = linkcode.linkcode_resolve

# sphinxext-opengraph settings
ogp_site_url = "https://pysparkplug.mattefay.com"
ogp_site_name = f"PySparkplug {release}"
ogp_image = "https://pysparkplug.mattefay.com/en/stable/static/logo.png"
ogp_image_alt = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "furo"
html_theme_options = {
    "sidebar_hide_name": True,
}

# Path to the logo placed at the top of the sidebar
html_logo = "static/logo.png"

html_title = f"PySparkplug {release}"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["static"]

# Hide link to each page's source file in the footer.
html_show_sourcelink = False

# -- Build the readme --------------------------------------------------------


def build_readme() -> None:
    """Copy README.md over, in the process adding doctests"""
    name = "README.md"
    with open(os.path.join(REPO_ROOT, name), encoding="utf-8") as source:
        readme = source.read()

    dest_dir = os.path.join(REPO_ROOT, "docs", "build")
    try:
        os.mkdir(dest_dir)
    except FileExistsError:
        pass

    with open(os.path.join(dest_dir, name), "w", encoding="utf-8") as dest:
        dest.write(readme.replace("```python\n>>> ", "```{doctest}\n>>> "))


build_readme()
