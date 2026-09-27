#!/usr/bin/env sh
# Compatibility entry point; the Python runner works on Windows, Linux and macOS.
set -eu
LAB_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec uv run --no-project --python 3.13 --with-requirements "$LAB_DIR/requirements.txt" \
  python "$LAB_DIR/generate_and_check.py" "$@"
