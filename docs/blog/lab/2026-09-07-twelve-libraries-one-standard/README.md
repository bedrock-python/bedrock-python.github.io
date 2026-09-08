# Lab: twelve libraries, one standard

`generate_and_check.sh` renders a new library from the organisation's Copier template with every
question answered on the command line, counts the files it produced, and runs the generated
project's own quality gate (`uv sync`, `make check`, `make test`). Pass a local checkout of the
template as the first argument to run it offline.
