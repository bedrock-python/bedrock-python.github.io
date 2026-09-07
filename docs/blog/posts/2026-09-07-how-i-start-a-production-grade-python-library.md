---
date: 2026-09-07
authors:
  - alex
categories:
  - Meta
tags:
  - python-library-template
  - packaging
  - ci
  - release
  - documentation
---

# How I start a production-grade Python library in 2026

Every library in this series started the same way: one command, forty-one files, and a green quality gate about three seconds later. That is not a boast about tooling, it is a claim about where the effort goes. The decisions that make a library maintainable — what the gate checks, who owns the version number, how it publishes, what the documentation is for — are made once and then applied by a template, so that the work on library number nine is the library and not the scaffolding.

<!-- more -->

Everything below was generated and run today against [python-library-template](https://github.com/bedrock-python/python-library-template), on Python 3.13.

## One command

```bash
uvx --with jinja2-time copier copy \
  --data project_name="Widget Kit" --data package_name="widget_kit" \
  gh:bedrock-python/python-library-template ./widget-kit
```

Forty-one files, and the gate runs before I have written a line:

```text
    uv run ruff check .           All checks passed!
    uv run ruff format --check .  8 files already formatted
    uv run mypy widget_kit        Success: no issues found in 2 source files
    make check                    2.25s
    pytest ...                    1 passed, coverage 100.00% (threshold 90%)
    make test                     0.66s
```

Three seconds. That number matters more than it looks: a gate that is fast is a gate people run before pushing, and a gate people run is the only kind that prevents anything.

## What is in the forty-one

Roughly: eight files of packaging and tooling configuration, four GitHub workflows, five community files, a `docs/` tree with seven pages, a test tree, and the package itself with three files in it.

The interesting part is what each group decides.

**The gate.** `ruff` for linting and formatting, `mypy` in strict mode over the package, `pytest` with a coverage floor of ninety percent, and fourteen pre-commit hooks including a conventional-commit check. Every one of those is a decision I do not want to re-make per repository, and more importantly, do not want to *drift* per repository — a library where `mypy` is advisory is a different library from one where it blocks.

**The workflows.** Lint, unit tests across the supported Python versions, integration tests, and an `all-checks-passed` job whose only purpose is to be the single required status check. That last one is a small trick worth stealing: branch protection points at one job name, so adding a Python version to the matrix does not mean editing the repository's protection rules.

**The release.** Release automation from conventional commits, a version that lives in exactly one file which the automation rewrites, and publishing to PyPI over OIDC with no token anywhere — [the pipeline post](2026-09-07-publishing-to-pypi-without-api-tokens.md) is the whole of it.

**The documentation.** Seven pages, and one of them is `docs/agents.md`: a single page holding everything a coding assistant needs to use the library correctly, which is a convention this org adopted after measuring how badly assistants guess at APIs. That is [its own post](2026-09-07-documentation-for-ai-coding-agents.md), and it is in the template because a documentation format that is not scaffolded is a documentation format that exists in one repository.

## The gate has to run what it claims

Generating this project today turned up something worth the whole exercise. The linting configuration selected the `DTZ` family — the rules that catch `datetime.now()` without a timezone — and then listed `DTZ` in the ignores, along with `ANN`. Selected and switched off, in the same block, in every library generated from the template.

Nothing was broken by it. What was broken was the claim: anybody reading that file, human or assistant, would have concluded that naive datetimes are checked. In a set of libraries whose subject matter is deadlines, retention windows, partition boundaries and TTLs, that is the one family you least want silently off.

The fix is two lines and a comment that says the rule out loud:

```toml
# Everything selected here runs. An entry below names one rule the house style
# disagrees with -- never a whole family that `select` has just asked for, which
# reads as a promise the linter does not keep.
select = ["F", "E", "W", "I", "B", "N", "S", "C4", "DTZ", "SIM", "TRY", "PERF", "RUF", "UP", "ANN", ...]
ignore = ["TRY003", "ANN401", "RUF012", "S104", "ANN204", "N802", "PERF401", "SIM105", "S607"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "S105", "S106"]
```

The families that were being switched off wholesale are on; the specific rules the house style disagrees with are named individually; and the exemptions that only make sense in tests — `assert`, hard-coded passwords in fixtures — say so by living in a per-file block. A naive `datetime.now()` now fails the gate:

```text
    3 |     return datetime.datetime.now()
      |            ^^^^^^^^^^^^^^^^^^^^^^^
    help: Pass a `datetime.timezone` object to the `tz` parameter
```

And the generated CI grew a step that renders the template, feeds it a naive datetime and an unannotated function, and fails if the linter stays quiet. A configuration that claims to check something needs a test that it does, or it will drift back.

Running the new rule set against four existing libraries found no naive datetimes at all, which is the good outcome, and does not make the switch-off harmless — it means the discipline held without the tool, which is not a plan.

## The things a template cannot give you

**A reason to exist.** Every library in this series came out of a problem measured in a service, not from a desire to have a library. The template makes the mechanics free, which raises rather than lowers the bar for starting one: if the only argument for a package is that the code is reusable in principle, it belongs in the service until somebody needs it twice.

**A public API you can live with.** `__all__` is a promise, and the template cannot make it for you. What it does do is make the promise visible: an agents page that lists the public surface is uncomfortable to write when the surface is arbitrary, which is a useful discomfort at version 0.1.

**Integration tests against the real thing.** The template ships the split — unit and integration as separate jobs — and the containers are yours. Everything in this series that turned out to be worth writing about came from a test against a real PostgreSQL, a real Kafka, a real Redis. A library whose integration story is mocks will discover its behaviour in production.

## The order I actually work in

1. **Write the problem down** as a failing test against a real dependency, in the service where it hurts.
2. **Generate the library** and move the smallest thing that fixes it, with that test.
3. **Write the agents page** before the guide. It forces the public API to be a list of names somebody can hold in their head.
4. **Release 0.1.0 immediately**, because a version that has been through the publish pipeline once is worth more than a perfect one that has not.
5. **Use it in the service** and let the next problem name the next release.

Steps two and four are the ones the template makes free. The rest is the work.

## The pieces

[python-library-template](https://github.com/bedrock-python/python-library-template) is a copier template plus a setup script that applies the repository settings — branch protection, the required check, dependabot, the release environment — to a fresh repository. Every library referenced in this series was generated from it, which is also why a fix to its linting configuration is a fix to twelve repositories at once, once they take the update.

Forty-one files, three seconds, and one line of configuration that was lying.
