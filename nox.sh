#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

if [[ "$#" -gt 0 ]]; then
    echo "Running" "$@" "in nox"
else
    echo "Running test suite"
fi

docker compose run --rm cicd nox "$@"

echo "$0 completed successfully!"
