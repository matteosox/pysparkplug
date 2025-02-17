export UV_PYTHON := env("UV_PYTHON", `cat .python-version`)
repository := "pypi"
publish-url := if repository == "pypi" {
  "https://upload.pypi.org/legacy/"
} else if repository == "testpypi" {
  "https://test.pypi.org/legacy/"
} else {
  error("Unrecognized repository")
}

default: test

test: format lint typecheck unit-test docs packaging

format:
    uv run ruff format

lint:
    uv run ruff check --fix --exit-non-zero-on-fix

typecheck:
    uv run pyright

unit-test *ARGS:
    uv run pytest test/unit_tests {{ARGS}}

coverage:
    for python in "3.9" "3.10" "3.11" "3.12" "3.13"; do \
        uv run --python "$python" coverage run -m pytest test/unit_tests; \
    done
    uv run coverage combine
    uv run coverage report
    uv run coverage xml --fail-under 0

docs:
    uv run sphinx-build -T -W -E --keep-going --color -b html docs docs/build/html
    uv run sphinx-build -T -W -E --keep-going --color -b doctest docs docs/build/doctest

packaging:
    uv build --no-sources
    uv run check-wheel-contents dist
    uv run twine check dist/*

draft:
    uv run scripts/draft_release.py

publish: packaging
    uv publish --publish-url {{publish-url}}

notebooks:
    -docker compose up
    docker compose down
