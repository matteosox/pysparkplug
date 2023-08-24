#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"/..
cd "$REPO_DIR"

echo "Opening notebook environment"

cleanup() {
    docker compose down
}
trap cleanup EXIT

docker compose up notebook emqx
