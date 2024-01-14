"""Test/developer workflow automation"""

import pathlib
from typing import cast

import nox
from packaging.version import Version

nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_missing_interpreters = True
nox.options.envdir = ".cache/nox"
nox.options.sessions = [
    "black",
    "isort",
    "pylint",
    "mypy",
    "unit_tests",
    "coverage",
    "docs",
    "packaging",
]


@nox.session(python=False)
def fix(session: nox.Session) -> None:
    """Simple workflow to run black and isort in fix mode"""
    session.notify("black", ["fix"])
    session.notify("isort", ["fix"])


@nox.session()
def black(session: nox.Session) -> None:
    """Black Python formatting tool"""
    session.install("--requirement", "requirements/black.txt")
    if session.posargs and session.posargs[0] == "fix":
        session.run("black", ".")
    else:
        session.run("black", "--diff", "--check", ".")


@nox.session()
def isort(session: nox.Session) -> None:
    """ISort Python import formatting tool"""
    session.install("--requirement", "requirements/isort.txt")
    if session.posargs and session.posargs[0] == "fix":
        session.run("isort", ".")
    else:
        session.run("isort", "--check-only", ".")


@nox.session()
def pylint(session: nox.Session) -> None:
    """Pylint Python linting tool"""
    session.install("--requirement", "requirements/pylint.txt", ".")
    session.run(
        "pylint",
        "src",
        "test/unit_tests",
        "noxfile.py",
        "docs",
    )


@nox.session()
def mypy(session: nox.Session) -> None:
    """Mypy Python static type checker"""
    session.install("--requirement", "requirements/mypy.txt", ".")
    session.run(
        "mypy",
        "src",
        "noxfile.py",
        "test/unit_tests",
        "docs/linkcode.py",
    )


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
def unit_tests(session: nox.Session) -> None:
    """Unit test suite run with coverage tracking"""
    session.install("--requirement", "requirements/unit_tests.txt", ".")
    if session.posargs and session.posargs[0] == "fast":
        session.run("python", "-m", "pytest")
    else:
        session.run("coverage", "run", "-m", "pytest")
        session.notify("coverage", ["no-cleanup"])


@nox.session()
def coverage(session: nox.Session) -> None:
    """Report on coverage tracking"""
    session.install("--requirement", "requirements/coverage.txt")
    try:
        session.run("coverage", "combine")
        session.run("coverage", "report")
    finally:
        if not (session.posargs and session.posargs[0] == "no-cleanup"):
            session.run("rm", "-f", ".coverage", external=True)


@nox.session()
def docs(session: nox.Session) -> None:
    """Generate and test documentation"""
    session.install("--requirement", "requirements/docs.txt", ".")
    session.run(
        "sphinx-build",
        "-T",
        "-W",
        "-E",
        "--keep-going",
        "--color",
        "-b",
        "html",
        "docs",
        "docs/build/html",
    )
    session.run(
        "sphinx-build",
        "-T",
        "-W",
        "-E",
        "--keep-going",
        "--color",
        "-b",
        "doctest",
        "docs",
        "docs/build/html",
    )


@nox.session()
def packaging(session: nox.Session) -> None:
    """Build and test packaging"""
    session.install("--requirement", "requirements/packaging.txt", ".")
    try:
        session.run("python", "-m", "build")
        session.run("check-wheel-contents", "dist")
        session.run("twine", "check", "dist/*")
    finally:
        session.run("rm", "-rf", "dist", external=True)


@nox.session()
def draft_release(session: nox.Session) -> None:
    """Create a draft Github Release"""
    session.install("--requirement", "requirements/draft_release.txt", ".")
    version_str = _version(session)
    version_obj = Version(version_str)
    if not version_obj.is_devrelease:
        raise ValueError(f"Package version {version_str} should be a dev release")
    cmd = [
        "gh",
        "release",
        "create",
        f"v{version_str}",
        "--draft",
        "--title",
        version_str,
        "--notes",
        _get_notes(),
    ]
    if version_obj.pre is not None:
        cmd.append("--prerelease")
    session.run(*cmd, external=True)


@nox.session()
def publish(session: nox.Session) -> None:
    """Publish package to PyPI and upload build artifacts to Github Release"""
    session.install("--requirement", "requirements/publish.txt", ".")
    version_str = _version(session)
    version_obj = Version(version_str)
    repository = session.posargs[0]
    if repository == "pypi":
        if (
            version_obj.is_devrelease
            or version_obj.is_postrelease
            or version_obj.local is not None
        ):
            raise ValueError(
                f"Package version {version_str} should not be a post or dev release"
            )
    elif repository == "testpypi":
        if not version_obj.is_devrelease:
            raise ValueError(f"Package version {version_str} should be a dev release")
    else:
        raise ValueError(f"Unrecognized repository {repository}")
    try:
        session.run("python", "-m", "build")
        session.run(
            "bash", "-c", f"gh release upload v{version_str} dist/*", external=True
        )
        session.run(
            "bash",
            "-c",
            f"twine upload --verbose --repository {repository} dist/*",
            external=True,
        )
    finally:
        session.run("rm", "-rf", "dist", external=True)


def _version(session: nox.Session) -> str:
    output = cast(
        str,
        session.run(
            "python",
            "-c",
            "import pysparkplug; print(pysparkplug.__version__)",
            silent=True,
        ),
    )
    return output.strip()


def _get_notes() -> str:
    search_pattern = "## "
    changes_lines = []
    with open("CHANGELOG.md", encoding="utf-8") as file_obj:
        for line in file_obj:
            if line.startswith(search_pattern):
                break
        else:
            raise LookupError(f"Could not find {search_pattern} in CHANGELOG.md")

        for line in file_obj:
            if line.startswith(search_pattern):
                break
            changes_lines.append(line)

    return "".join(changes_lines)


@nox.session()
def update_requirements(session: nox.Session) -> None:
    """Pin requirements files for nox environments.

    NOTE: "'pip-compile' should be run from the same virtual environment as your
    project so conditional dependencies that require a specific Python
    version, or other environment markers, resolve relative to your project's
    environment." This does not do that, and may break in the future as a
    result, especially the various unit test environments, with their
    different Python versions.
    """
    session.install("pip-tools")
    for path in pathlib.Path(pathlib.Path.cwd(), "requirements").iterdir():
        if path.suffix == ".in":
            session.run(
                "pip-compile",
                "--allow-unsafe",
                "--resolver=backtracking",
                "--upgrade",
                "--verbose",
                "--output-file",
                f"requirements/{path.stem}.txt",
                str(path),
                env={"CUSTOM_COMPILE_COMMAND": "./nox.sh -s update_requirements"},
            )
