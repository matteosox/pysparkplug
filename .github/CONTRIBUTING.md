# Contributor Guide

## Getting started

We use Docker as a clean, reproducible development environment within which to build, test, generate docs, and so on. As long as you have a modern version of Docker, you should be able to run all developer workflows. That's it! Of course, running things natively isn't a supported/maintained thing.

## Tests

_TL;DR: Run `./nox.sh` to run the full suite of tests._

### Black Code Formatting

_TL;DR: Run `./nox.sh -s black` to test your code's formatting._

We use [Black](https://black.readthedocs.io/en/stable/index.html) for code formatting. To format your code, run `./nox.sh -s fix` to get all your spaces in a row. Black configuration can be found in the `pyproject.toml` file at the root of the repo.

### isort Import Ordering

_TL;DR: Run `./nox.sh -s isort` to test your code's imports._

For import ordering, we use [isort](https://pycqa.github.io/isort/). To get imports ordered correctly, run `./nox.sh -s fix`. isort configuration can be found in the `pyproject.toml` file at the root of the repo.

### Pylint Code Linting

_TL;DR: Run `./nox.sh -s pylint` to lint your code._

We use [Pyint](https://pylint.pycqa.org/en/latest/) for Python linting (h/t Itamar Turner-Trauring from his site [pythonspeed](https://pythonspeed.com/articles/pylint/) for inspiration). To lint your code, run `./nox.sh -s pylint`. In addition to showing any linting errors, it will also print out a report. Pylint configuration can be found in the `pylintrc` file at the root of the repo.

Pylint is setup to lint the `src`, `test/unit_tests` and `docs` directories, along with `noxfile.py`. To add more modules or packages for linting, edit the `pylint` test found in `noxfile.py`.

### Mypy Static Type Checking

_TL;DR: Run `./nox.sh -s mypy` to type check your code._

We use [Mypy](https://mypy.readthedocs.io/en/stable/) for static type checking. To type check your code, run `./nox.sh -s mypy`. Mypy configuration can be found in the `pyproject.toml` file at the root of the repo.

Mypy is setup to run on the `src` and`test/unit_tests`, along with `noxfile.py` and `docs/linkcode.py`. To add more modules or packages for type checking, edit the `mypy` test found in `noxfile.py`.

### Unit Tests

_TL;DR: Run `./nox.sh -s unit_tests-3.10 -- fast` to unit test your code quickly._

While we use [`unittest`](https://docs.python.org/3/library/unittest.html) to write unit tests, we use [`pytest`](https://docs.pytest.org/) for running them. To unit test your code, run `./nox.sh -s unit_tests-3.10 -- fast`. This will run unit tests in Python 3.10 only, without any coverage reporting overhead. To run the tests across all supported versions of Python, run `./nox.sh -s unit_tests`, which will also generate coverage reports which can be aggregated using `./nox.sh -s coverage`.

`pytest` is setup to discover tests in the `test/unit_tests` directory. All test files must match the pattern `test*.py`. `pytest` configuration can be found in the `pyproject.toml` file at the root of the repo. To add more directories for unit test discovery, edit the `testpaths` configuration option.

### Test Coverage

_TL;DR: Run `./nox.sh -s coverage` after running the unit tests with coverage to test the coverage of the unit test suite._

We use [Coverage.py](https://coverage.readthedocs.io/en/coverage-5.5/) to test the coverage of the unit test suite. This will print any coverage gaps from the full test suite. Coverage.py configuration can be found in the `pyproject.toml` file at the root of the repo.

### Documentation Tests

_TL;DR: Run `./nox.sh -s docs` to build and test the documentation._

See [below](#documentation) for more info on the documentation build process. In addition to building the documentation, the `test/docs.sh` shell script uses Sphinx's [`doctest`](https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html) builder to ensure the documented output of usage examples is accurate. Note that the `README.md` file's ` ```python` code sections are transformed into `{doctest}` directives by `docs/conf.py` during the documentation build process. This allows the `README.md` to render code with syntax highlighting on Github & [PyPI](https://pypi.org) while still ensuring accuracy using `doctest`.

### Packaging Tests

_TL;DR: Run `./nox.sh -s packaging` to build and test the package._

We use [`build`](https://pypa-build.readthedocs.io/en/latest/) to build source distributions and wheels. We then use [`check-wheel-contents`](https://github.com/jwodder/check-wheel-contents) to test for common errors and mistakes found when building Python wheels. Finally, we use [`twine check`](https://twine.readthedocs.io/en/latest/#twine-check) to check whether or not `pysparkplug`'s long description will render correctly on [PyPI](https://pypi.org). To test the package build, run `./nox.sh -s packaging`. While there is no configuration for `build` or `twine`, the configuration for `check-wheel-contents` can be found in the `pyproject.toml` file at the root of the repo.

## Requirements

### Package Dependencies

_TL;DR: `pysparkplug`'s dependencies are defined in `requirements/requirements.txt`_

We use the [hatch-requirements-txt](https://github.com/repo-helper/hatch-requirements-txt) Hatch extension to define `pysparkplug`'s dependenices dynamically in a separate file, specifically `requirements/requirements.txt`.

### Nox Session Dependencies

_TL;DR: Run `./nox.sh -s update_requirements` to update the requirements of each nox session._

We use [nox](https://nox.thea.codes/en/stable/) to define developer workflows in Python. Each nox session has its own Python virtual environment and set of pinned requirements associated with it. We want these statically defined so developer workflows are reproducible. To do this, we generate a `requirements/{session_name}.txt` file for each session by running `./nox.sh --session update_requirements`, which uses `pip-compile`.

To control which packages are installed, manually edit `requirements/{session_name}.in`. This gives us both a flexible way to describe dependencies while still achieving reproducible builds. Inspired by [this](https://hynek.me/articles/python-app-deps-2018/) and [this](https://pythonspeed.com/articles/pipenv-docker/).

### Note on Hashes

While using [hashes](https://pip.pypa.io/en/stable/cli/pip_install/#hash-checking-mode) would be nice, different platforms, e.g. Apple's ARM vs Intel's x86, sometimes require different wheels with different hashes. This is true despite ensuring a consistent Linux OS in Docker sadly. In the spirit of enabling a diverse ecosystem of developers with different machines, I've kept hashing off.

## Documentation

_TL;DR: To build and test the documentation, run `./nox.sh -s docs`._

We use [Sphinx](https://www.sphinx-doc.org/en/master/index.html) for documentation site generation. To build the documentation, run `./nox.sh -s docs`. To view it, open `docs/build/html/index.html` in your browser.

Sphinx configuration can be found in `docs/conf.py`. It is setup to generate pages based on what it finds in the `toctree` directive in `docs/index.md`. To add new pages, add them to the table of contents with that directive.

### API Reference

The "API Reference" page is mostly auto-generated using the [`autodoc`](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html), [`autosummary`](https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html), [`intersphinx`](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html), and [`linkcode`](https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html) Sphinx extensions. Classes, functions, decorators, and so on need to be added manually to the `docs/api.rst` file, but once included, the entries are auto-generated using type annotations and docstrings.

### Docstring Formatting

We use the [`napoleon`](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html) Sphinx extension to enable docstring formats other than Sphinx's default, rather unreadable format. Instead, we use [Google's docstring standard](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings). Types and defaults should not be referenced in the docstring, instead included in annotations.

### Auto-generated Github Links

We use the [`linkcode`](https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html) Sphinx extension to add links to Github on the API Reference page. The code for mapping Python objects to links can be found in the `docs/linkcode.py` Python module.

### Changelog

We document changes in the `CHANGELOG.md` file. This project adheres to the [keep a changelog](https://keepachangelog.com/en/1.0.0/) standard. Before committing changes that impact users, make sure to document features added, changed, deprecated, removed, fixed, or security-related changes to the "## Unreleased" section.

### Publishing Documentation

We use [Read the Docs](https://docs.readthedocs.io/en/stable/index.html) for building and publishing `pysparkplug`'s documentation. Its Github integration makes this process seamless. Read the Docs configuration can be found in the `.readthedocs.yaml` file at the root of the repo.

While documentation for the `pysparkplug` package is generated and hosted by Read the Docs, the documentation can be found at a custom domain: [pysparkplug.mattefay.com](https://pysparkplug.mattefay.com). You can read more about this [here](https://docs.readthedocs.io/en/stable/custom_domains.html).

## Releasing

### Release Process

Every push to the `main` branch on Github generates a draft release on Github. To publish a release, one should:

1.) If creating a final release (i.e. not a pre-release), create and merge a pull request that updates the `CHANGELOG.md` such that the released changes section is renamed from "## Unreleased" to "## {MAJOR.MINOR.MICRO} (YYYY-MM-DD)"

2.) Review the draft release. Update the tag for the draft release to the version you want to release with a prefixed v, i.e. "v{MAJOR.MINOR.MICRO}", and add any additional notes as you see fit. Publish it. This will trigger the `release` Github Action, which will publish to [PyPI](https://pypi.org).

3.) After confirming that the release on Github look good, as does the package on [PyPI](https://pypi.org), if this was a final release (i.e. you updated the `CHANGELOG.md`) create and merge a new pull request that creates a new "## Unreleased" section at the top of the `CHANGELOG.md`. This should have new, empty sections for Added, Changed, Deprecated, Removed, Fixed, and Security.

### Determining the Version

`pysparkplug` is versioned according to [PEP 440](https://www.python.org/dev/peps/pep-0440/). The type of final release (major, minor, or micro) should be determined by the types of unreleased changes in the changelog. Any "Removed" changes call for a major release (increment the major digit, minor and micro reset to 0). "Added" changes call for a minor release (increment the minor digit, micro set to 0). Otherwise, a "micro" release is called for (increment the micro digit only).

Intermediate versions between releases are incremented with `dev` and taken care of by [`hatch-vcs`](https://github.com/ofek/hatch-vcs).

## Continuous Integration & Continuous Deployment

We use Github actions to run our CI/CD pipeline on every pull request. The configuration can be found in `.github/workflows/cicd.yaml`. That said, every step of every job can also be run locally.

### Main

This is the "main" job, which consists of running the test suite, creating a draft release, and publishing the package to [TestPyPI](https://test.pypi.org).

### OS Compatibility

Using Github Actions' [build matrix feature](https://docs.github.com/en/actions/learn-github-actions/managing-complex-workflows#using-a-build-matrix), we're able to run unit tests on MacOS, Windows, & Linux, for each supported version of Python.

### Publish

A separate `publish` workflow is configured in `.github/workflows/publish.yaml`. This workflow publishes the package to [PyPI](https://pypi.org), and is triggered by a Github release being published.

## Pull Requests

The `main` branch has [branch protections](https://help.github.com/en/github/administering-a-repository/about-protected-branches) turned on in Github, requiring one reviewer to approve a PR before merging. We also use the code owners feature to specify who can approve certain PRs. As well, merging a PR requires status checks (Read the Docs along with both CI/CD jobs) to complete successfully.

When naming a branch, please use the syntax `username/branch-name-here`. If you plan to collaborate with others on that branch, use `team/branch-name-here`.

## Future Work

- Better unit testing
- 100% test coverage
- Doctest
- Improve README.md
- Integration testing
- Primary host usecase
- Edge Node
    - Aliases
    - Rebirth
    - Multiple MQTT server support
    - Drop datatypes
    - Report by exception logic
    - Device metric polling
- data types
    - Template types
    - Metadata
    - Properties
    - DataSet types
    - Array types
- MQTT v5
- Historian/analytics (just listens)
- Refactor all of `_payload.py`.
- Refactor `_datatype.py` for better type annotation.
- Add validation for correct combinations of group_id, edge_node_id, etc. to `Topic.__init__`.
