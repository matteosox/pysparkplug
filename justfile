python := `cat .python-version`
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
    uv run --python {{python}} ruff format

lint:
    uv run --python {{python}} ruff check --fix --exit-non-zero-on-fix

typecheck:
    uv run --python {{python}} pyright

unit-test *ARGS:
    uv run --python {{python}} pytest test/unit_tests {{ARGS}}

coverage:
    for python in "3.9" "3.10" "3.11" "3.12" "3.13"; do \
        uv run --python $python coverage run -m pytest test/unit_tests; \
    done
    uv run --python {{python}} coverage combine
    uv run --python {{python}} coverage report

docs:
    uv run --python {{python}} sphinx-build -T -W -E --keep-going --color -b html docs docs/build/html
    uv run --python {{python}} sphinx-build -T -W -E --keep-going --color -b doctest docs docs/build/doctest

packaging:
    uv build
    uv run --python {{python}} check-wheel-contents dist
    uv run --python {{python}} twine check dist/*

draft:
    uv run --python {{python}} scripts/draft_release.py

publish: packaging
    uv publish --publish-url {{publish-url}}
