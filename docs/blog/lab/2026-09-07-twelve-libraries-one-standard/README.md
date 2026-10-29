# Lab: report-periods from template to installed package {#lab-twelve-libraries-one-standard}

Generate `report-periods` from Bedrock's template, add a UTC month-boundary function, test it, build version `0.1.0` and install both distribution formats. This is the executable companion to [A Python library from template to release](../../posts/2026-10-22-python-library-from-template-to-release.md).

## Run {#run}

You need Git, uv and network access for the template, Python interpreters and dependencies. Run from the website repository root:

```bash
uv run --no-project --python 3.13 --with-requirements docs/blog/lab/2026-09-07-twelve-libraries-one-standard/requirements.txt python docs/blog/lab/2026-09-07-twelve-libraries-one-standard/generate_and_check.py --output build/report-periods-lab
```

The output directory must not exist. Omit `--output` to create a fresh temporary directory that is retained after the run. An optional first positional argument can point to a local checkout of `python-library-template`; it must contain commit `a1a1e7d5eafdcac08aeed7c1a0daaff31c67ac8c`. This avoids downloading the template, but dependencies may still need the network. `generate_and_check.sh` is a shell wrapper around the same Python runner.

The lab enables Copier's trusted mode for the pinned template's Jinja extension and post-generation task. That task only prints instructions. The lab initializes a local Git repository to isolate ignore rules; it makes no commits, GitHub changes, tags or PyPI uploads.

## What is checked {#checks}

| Stage | Expected result |
|---|---|
| Generated baseline | Ruff, formatting, mypy, one version test; integration selection exits `5` |
| Useful behavior | Seven tests on Python 3.11, 3.12 and 3.13, including UTC conversion and December rollover |
| Deliberate defects | Ruff detects `DTZ005`; a broken December increment fails the test |
| Aggregate CI job | The condition is evaluated for all 64 result combinations; only all-success passes, the original accepted seven with a skipped job |
| Tag/version check | The replacement publish step accepts two tag forms and rejects four inputs against the committed version |
| Build | Wheel and sdist agree on package modules; metadata and `py.typed` are present |
| Consumer | Wheel and sdist installed separately on Python 3.11; isolated imports, public API and version pass |

The runner restores deliberately broken files, installs the replacement aggregate job and publish step into the generated project and models release-PR version files locally. It does not run GitHub Actions or validate Trusted Publishing, and the publishing workflow still does not wait for CI on the tagged commit.

## Files and results {#files-and-results}

- `generate_and_check.py`: generation, checks, controlled defects, build and installation.
- `periods.py`, `test_periods.py`: six behavior cases, plus the generated version test.
- `ci-gate.yml`: replacement aggregate job; the runner evaluates its condition for every result combination.
- `release-check.yml`: replacement for the publish step that rewrote `__version__.py` from the tag; the runner executes its Python.
- `artifact_smoke.py`: checks performed from the installed package in each clean environment.
- `requirements.txt`: Copier 9.18.2, jinja2-time 0.2.0 and PyYAML 6.0.3.

The output retains `report-periods/` with `uv.lock` and `dist/`, the original CI and publish YAML, a consumer directory, two clean environments, numbered command logs and `report.json`. Development dependencies are resolved from the template's constraints, not pinned by this lab's requirements; the generated lock and report record what was used. The run verified on 2026-10-16 used uv 0.10.2, Ruff 0.17.1, mypy 2.4.0, pytest 9.1.1 and pytest-cov 7.1.0.
