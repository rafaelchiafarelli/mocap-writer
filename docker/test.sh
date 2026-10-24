#!/usr/bin/env bash
# Run the full test suite inside the mocap-writer image (no display needed).
#   docker/test.sh [pytest args]
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
image="mocap-writer:dev"
docker build -q -t "$image" -f "$repo/docker/Dockerfile" "$repo/docker" >/dev/null

exec docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo":/app:ro -w /app "$image" \
    /opt/venv/bin/python -m pytest -p no:cacheprovider "$@"
