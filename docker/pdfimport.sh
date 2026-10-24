#!/usr/bin/env bash
# Run the PDF importer's command line in the mocap-writer image, in the
# current directory (mounted at its own path, so relative paths work):
#   docker/pdfimport.sh probe <pdf> [--skip-pages N]
#   docker/pdfimport.sh import <pdf>... --profile <toml> --out <dir> [--trace]
# The repository's starter profiles are at /app/trelby/pdfprofiles/.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
image="mocap-writer:dev"
docker build -q -t "$image" -f "$repo/docker/Dockerfile" "$repo/docker" >/dev/null

exec docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo":/app:ro -v "$PWD":"$PWD" -w "$PWD" -e PYTHONPATH=/app \
    "$image" /opt/venv/bin/python -W ignore::SyntaxWarning -m trelby.pdfimport "$@"
