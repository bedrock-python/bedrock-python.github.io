#!/usr/bin/env sh
# Generate a library from the organisation template and run the generated project's own gate.
# Needs uv and make. Times the two halves separately.
set -eu
TEMPLATE="${1:-gh:bedrock-python/python-library-template}"

time uvx --from copier --with jinja2-time copier copy --trust --defaults \
  --data project_name=widget-kit --data project_slug=widget-kit --data package_name=widget_kit \
  --data project_description="A lab library" --data author_name="Alex Shalaev" \
  --data author_email=alex@example.com --data github_org=bedrock-python \
  --data python_min_version=3.12 --data initial_version=0.0.0 \
  "$TEMPLATE" widget-kit

cd widget-kit
find . -type f | wc -l
git init -q
time sh -c 'uv sync --group dev && make check && make test'
