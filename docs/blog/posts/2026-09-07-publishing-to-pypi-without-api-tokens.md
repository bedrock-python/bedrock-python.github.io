---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - python-library-template
  - pypi
  - github-actions
  - release
  - security
---

# Publishing to PyPI without API tokens: Trusted Publishing end to end

A PyPI API token in a repository secret is a password with no expiry, no scope beyond the project it was minted for, and no way to tell who used it. Trusted Publishing replaces it with an identity: GitHub Actions presents a short-lived OIDC token that says which repository, which workflow and which environment is asking, and PyPI decides whether that combination is allowed to publish. Nothing to store, nothing to rotate, nothing to leak. Here is the whole pipeline as it runs in the Bedrock repositories, from a merged pull request to a wheel on PyPI, including the day it goes wrong.

<!-- more -->

Today six libraries went out through this pipeline, so every step below is the one that actually ran rather than the one in the documentation. The workflow files are in every repository under `.github/workflows/`.

## What replaces the token

The publishing job declares one permission and one environment:

```yaml
permissions:
  contents: read
  id-token: write        # Trusted Publisher (PyPI OIDC)

jobs:
  publish:
    environment: pypi
```

`id-token: write` is what lets the job ask GitHub for an OIDC token. That token is a signed statement about *this* run: the repository, the workflow file, the ref, the environment. The publish tool exchanges it with PyPI for a short-lived upload token, and PyPI accepts the exchange only if the project has a Trusted Publisher configured that matches all of those.

The configuration on the PyPI side is four fields: the repository owner, the repository name, the workflow filename, and the environment name. Both halves matter. A workflow file with a different name cannot publish, and neither can the same workflow running without the environment.

What proves it is not a token is what is absent. The repository's secrets are:

```text
CODECOV_TOKEN
```

That is the whole list. There is no PyPI token in the repository, none in the `pypi` environment, and none passed to the publish step:

```yaml
- run: uv build
- run: uv publish --check-url https://pypi.org/simple/redis-client-kit/
```

`uv publish` with no credentials in sight looks for the OIDC token and uses it. The failure mode when Trusted Publishing is misconfigured is a clear 403 from PyPI naming what it expected, not a mysterious authentication error.

## The environment is the gate

`environment: pypi` looks decorative and is not. A GitHub environment can carry required reviewers, a wait timer and a branch restriction, and the job cannot start until those pass. It is also the thing PyPI's configuration pins to, so a workflow that publishes from a fork's pull request — where the environment is not available — cannot get a token at all.

In these repositories the environment has no protection rules, because the release itself is already gated: publishing only happens for a tag that release automation created after a pull request was merged. A project where a human should sign off on every release adds a required reviewer here and gets an approval step in front of the upload, without changing anything about how the credentials work.

## From a merged pull request to a tag

The other half of the pipeline is the part that decides *what* to publish. Conventional commits go in, and a release pull request comes out:

```yaml
on:
  push:
    branches: [master]

jobs:
  release-please:
    steps:
      - uses: googleapis/release-please-action@v5
```

That action keeps one open pull request per project, containing the version bump, the changelog entries derived from the commit messages since the last release, and any file listed as an extra:

```json
"extra-files": [
  { "type": "generic", "path": "redis_client_kit/__version__.py" }
]
```

That last part is worth the two lines it takes. A version that lives in exactly one file, written by the release automation, cannot drift from the tag. When the release pull request merges, the action creates the tag and the GitHub release, and the publish workflow takes over.

The commit type decides the bump: `fix:` gives a patch, `feat:` a minor, a `!` or a `BREAKING CHANGE:` footer a major. That is a real constraint on how you write commit messages, and it is the point: the version is a fact derived from what changed, not a number somebody chose while tired.

## The publish trigger, and why it is a `workflow_run`

```yaml
on:
  workflow_run:
    workflows: ["Release Please"]
    types: [completed]
  workflow_dispatch:
    inputs:
      tag:
        description: "Release tag to publish (e.g. redis-client-kit-v0.1.0)"
```

The publish workflow runs after the release workflow finishes, then asks a question: did that run leave a release tag on this commit?

```bash
TAG=$(git tag --points-at HEAD | grep -E '^redis-client-kit-v' | head -1)
```

Most runs answer "no" — every ordinary merge to the default branch triggers the release workflow, which usually just updates the release pull request — and the job stops there. Only the merge of the release pull request itself leaves a tag, and that is the run that publishes.

Then, before building, the version is written one more time from the tag:

```bash
VERSION="${TAG#redis-client-kit-v}"
echo "__version__ = \"$VERSION\"" > redis_client_kit/__version__.py
```

The release automation already committed that exact line. Doing it again is a safety net: whatever else happened, the artefact that goes to PyPI carries the version in the tag it was built from. Here is that step from today's run:

```text
    __version__ = "0.2.0"
    Successfully built dist/redis_client_kit-0.2.0.tar.gz
    Successfully built dist/redis_client_kit-0.2.0-py3-none-any.whl
    Publishing 2 files to https://upload.pypi.org/legacy/
    Uploading redis_client_kit-0.2.0-py3-none-any.whl (33.0KiB)
    Uploading redis_client_kit-0.2.0.tar.gz (23.5KiB)
```

## The day something goes wrong

Two mechanisms, both used today.

**A publish that half-succeeded.** `--check-url https://pypi.org/simple/<project>/` makes the upload idempotent: a rerun skips files already on the index instead of failing on "file already exists". Without it, a run that uploaded the wheel and then lost its connection before the sdist leaves you unable to retry without deleting a release from PyPI, which you cannot do.

**A publish that never started.** The `workflow_dispatch` input takes a tag and publishes it. That is the escape hatch for the case where the tag exists but the automatic run did not happen — a GitHub incident, a workflow that was disabled, a run cancelled by a queue limit. It builds from the tag, so it cannot publish anything but what was released.

There is a third failure that has nothing to do with publishing and hit twice today: a flaky infrastructure step in the release pull request's own CI. The release automation cannot merge a pull request whose checks failed, so the pipeline stalls at a green-looking release that never ships. Rerunning the failed jobs is the whole fix, and the reason to watch a release to completion rather than assuming a merged pull request means a published package.

## What this buys, concretely

- **Nothing to rotate.** There is no long-lived credential, so there is no rotation policy, no expiry to miss, and no scramble when somebody leaves the team.
- **Nothing to leak.** A secret that does not exist cannot be printed by a debug step, exfiltrated by a compromised dependency in the build, or committed by accident.
- **A narrower blast radius.** The identity is repository plus workflow plus environment. A different workflow in the same repository, added by a pull request, cannot publish.
- **An audit trail that means something.** PyPI records which repository and workflow published each file, so "who released 0.2.0" has an answer that is not "somebody with the token".

The cost is that it only works from a CI provider PyPI knows about, and that a local `uv publish` from a laptop needs a token again — which is the right shape, because releasing from a laptop is the thing you wanted to stop doing.

## The pieces

All of the above ships in [python-library-template](https://github.com/bedrock-python/python-library-template), the copier template every Bedrock library is generated from: the four workflows, the release configuration with the version file wired in, the `pypi` environment, and the repository setup that creates them. A new library is a template render and one Trusted Publisher configured on PyPI, and its first release goes out the same way as today's sixth one.
