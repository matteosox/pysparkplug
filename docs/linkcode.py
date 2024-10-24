"""Python module with single public linkcode_resolve function"""

import importlib.metadata
import inspect
import os
import shlex
import subprocess
import sys

from packaging.version import Version

import pysparkplug


def linkcode_resolve(domain: str, info: dict[str, str]) -> str | None:
    """
    linkcode Sphinx extension uses this function to map objects to be
    documented to external URLs where the code is kept, in our case
    github. Read more at:
    https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html
    """
    if domain != "py":
        raise ValueError(f"Not currently documenting {domain}, only Python")

    if not info["module"]:
        return None

    modname = info["module"]
    fullname = info["fullname"]

    rel_url = _get_rel_url(modname, fullname)
    blob = _get_blob()

    return f"https://github.com/matteosox/pysparkplug/blob/{blob}/src/pysparkplug/{rel_url}"


def _get_blob() -> str:
    version_str = importlib.metadata.version("pysparkplug")
    version = Version(version_str)
    if version.is_devrelease or version.is_postrelease:
        return _get_git_sha()
    return f"v{version_str}"


def _get_git_sha() -> str:
    completed_process = subprocess.run(
        shlex.split("git rev-parse --short HEAD"),
        check=True,
        text=True,
        capture_output=True,
    )
    return completed_process.stdout.strip()


def _get_rel_url(modname: str, fullname: str) -> str:
    """Get the relative url given the module name and fullname"""
    obj = sys.modules[modname]
    for part in fullname.split("."):
        try:
            obj = getattr(obj, part)
        except AttributeError:
            # When documenting instance attributes, they are not defined on the class,
            # so just reference the class
            pass

    # strip decorators, which would resolve to the source of the decorator
    # possibly an upstream bug in getsourcefile, bpo-1764286
    obj = inspect.unwrap(obj)  # type: ignore[arg-type]

    # Can only get source files for some Python objects
    source_file = None
    try:
        source_file = inspect.getsourcefile(obj)
    except TypeError:
        source_file = sys.modules[modname].__file__
    finally:
        if source_file is None:
            rel_path = ""
        else:
            rel_path = os.path.relpath(
                source_file, start=os.path.dirname(pysparkplug.__file__)
            )

    # Can only get source lines for some Python objects
    try:
        source, lineno = inspect.getsourcelines(obj)
    except TypeError:
        linespec = ""
    else:
        linespec = f"#L{lineno}-L{lineno + len(source) - 1}"

    return f"{rel_path}{linespec}"
