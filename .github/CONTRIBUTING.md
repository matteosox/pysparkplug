# Contributor Guide

## Getting started

We use
- [`uv`](https://docs.astral.sh/uv/) as a Python project and package manager
- [`just`](https://just.systems/) as a command runner
- [`git`](https://git-scm.com/) as a distributed version control system

That should be all you need to install!

## Tests

_TL;DR: Run `just` to run the full suite of tests._

Note: any of the following commands run with the pinned Python version in `.python-version`, but can be run with a custom version, e.g. `UV_PYTHON=3.13 just test`.

### Code Formatting

_TL;DR: Run `just format` to format Python code in this repo._

We use [ruff](https://docs.astral.sh/ruff/) to auto-format the Python code in this repo so you don't have to.

### Code Linting

_TL;DR: Run `just lint` to lint Python code in this repo._

We use [ruff](https://docs.astral.sh/ruff/) to lint the Python code in this repo.

### Type Checking

_TL;DR: Run `just typecheck` to check the types of the Python code in this repo._

We use [pyright](https://microsoft.github.io/pyright/#/) to check the types of the Python code in this repo.

### Unit Tests

_TL;DR: Run `just unit-test` to run Python unit tests._

We use [pytest](https://docs.pytest.org/en/stable/) to run unit tests, but mostly write them with Python's built-in unittesting module, i.e. [unittest](https://docs.python.org/3/library/unittest.html). You might want to run a subset of unit tests, which you can do! Here's some examples:
- Specific test: `just unit-test test/unit_tests/test_topic.py::TestTopic::test_complete_wildcard`
- Specific test class: `just unit-test test/unit_tests/test_topic.py::TestTopic`
- Specific test file: `just unit-test test/unit_tests/test_topic.py`

All args are simply passed to `pytest`, so go to town!

### Coverage

_TL;DR: Run `just coverage` to run coverage analysis of the Python unit test suite across all supported versions of Python._

We use [coverage](https://coverage.readthedocs.io/en) to test the code coverage of our Python unit test suite. This command runs the unit test suite with each version of Python supported, combining before reporting the results.

Note: this does not get run by `just test` and is not part of CI, only to help developers track coverage on the OS of their local development environment.

### Documentation Tests

_TL;DR: Run `just docs` to build & test the documentation._

See [below](#documentation) for more info on the documentation build process. In addition to building the documentation, this uses Sphinx's [`doctest`](https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html) builder to ensure the documented output of usage examples is accurate. Note that the `README.md` file's ` ```python` code sections are transformed into `{doctest}` directives by `docs/source/conf.py` during the documentation build process. This allows the `README.md` to render code with syntax highlighting on Github & PyPI while still ensuring accuracy using `doctest`.

### Packaging Tests

_TL;DR: Run `just packaging` to test the package build._

We use [`uv`](https://docs.astral.sh/uv/) to build source distributions and wheels. We then use [`check-wheel-contents`](https://github.com/jwodder/check-wheel-contents) to test for common errors and mistakes found when building Python wheels. Finally, we use [`twine check`](https://twine.readthedocs.io/en/latest/#twine-check) to check whether or not `pysparkplug`'s long description will render correctly on PyPI.

## Documentation

_TL;DR: To build the documentation website, run `just docs`._

We use [Sphinx](https://www.sphinx-doc.org/en/master/index.html) for documentation site generation. To view them, open `docs/build/html/index.html` in your browser.

Sphinx will only generate pages that have changed since your last build, but isn't perfect at this determination, so you may need to clear out your `docs/build` directory to start fresh. Sphinx configuration can be found in `docs/source/conf.py`.

Sphinx is setup to generate pages based on what it finds in the `toctree` directive in `docs/source/index.md`. To add new pages, add them to the table of contents with that directive.

### API Reference

The "API Reference" page is auto-generated using the [`autodoc`](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html), [`autosummary`](https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html), [`intersphinx`](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html), and [`linkcode`](https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html) Sphinx extensions. These pages and sub-pages are auto-generated using type annotations and docstrings.

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

Every push to the `main` branch on Github generates a draft release on Github and publishes a `dev` version to [TestPyPI](https://test.pypi.org). To publish a release, one should:

1.) Finalize any documentation in the `CHANGELOG.md` if this is a "final" release, i.e. not a dev or pre-release (alpha, beta, rc1, rc2, etc.). The released changes section should have the format "## {MAJOR.MINOR.MICRO} (YYYY-MM-DD)"

2.) Review the draft release. Update the tag for the draft release to the version you want to release with a prefixed v, i.e. "v{MAJOR.MINOR.MICRO}", and add any additional notes as you see fit. Publish it. This will trigger the `release` Github Action, which will publish to [PyPI](https://pypi.org).

### Determining the Version

`pysparkplug` is versioned according to [PEP 440](https://www.python.org/dev/peps/pep-0440/). The type of final release (major, minor, or micro) should be determined by the types of unreleased changes in the changelog. Any "Removed" changes call for a major release (increment the major digit, minor and micro reset to 0). "Added" changes call for a minor release (increment the minor digit, micro set to 0). Otherwise, a "micro" release is called for (increment the micro digit only).

Intermediate versions between releases are incremented with `dev` and taken care of by [`hatch-vcs`](https://github.com/ofek/hatch-vcs).

## Continuous Integration & Continuous Deployment

We use Github actions to run our CI/CD pipeline on every pull request. The configuration can be found in `.github/workflows/cicd.yaml`. That said, most steps of most jobs can also be run locally.

### Main

This is the "main" job that runs on every commit to a branch with a pull request to `main`, every push to `main`, and on workflow dispatch. It runs the tests, and on pushes to main publishes a draft Github Release and publishes a dev version of the package to [TestPyPI](https://test.pypi.org).

### OS Compatibility

Using Github Actions' [build matrix feature](https://docs.github.com/en/actions/learn-github-actions/managing-complex-workflows#using-a-build-matrix), we're able to run unit tests on MacOS, Windows, & Linux. The coverage report from each of these is then uploaded to [Codecov](https://about.codecov.io/).

## Pull Requests

The `main` branch has [branch protections](https://help.github.com/en/github/administering-a-repository/about-protected-branches) turned on in Github, requiring one reviewer to approve a PR before merging. We also use the code owners feature to specify who can approve certain PRs. As well, merging a PR requires status checks (Read the Docs, both CI/CD jobs, and codecov) to complete successfully.

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
- MQTT v5
- Historian/analytics (just listens)
- Refactor all of `_payload.py`.
- Refactor `_datatype.py` for better type annotation.
- Add validation for correct combinations of group_id, edge_node_id, etc. to `Topic.__init__`.
