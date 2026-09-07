# Lab: what a library costs to install and to import

For each of eight libraries: a fresh virtual environment, an install of the bare package, the
number of distributions that came with it, the megabytes on disk, and the best of five import
times for the package root — then the same with one extra, so the difference is the extra's price.
Finally, what reaching for a feature an extra provides says when the extra is not installed.

```bash
uv venv --python 3.13 .venv
.venv/bin/python footprint.py       # it creates its own throwaway venv per package
```
