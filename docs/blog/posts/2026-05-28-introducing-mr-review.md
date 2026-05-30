---
date: 2026-05-28
authors:
  - alex
categories:
  - Tools
tags:
  - mr-review
  - ai
  - gitlab
  - github
---

# Introducing mr-review: AI-powered merge request reviews

Code review is one of the highest-leverage activities in a software team, and also one of the most inconsistent. Reviewers get tired, context-switch mid-review, miss things. **mr-review** is a CLI tool that runs locally and uses an LLM to walk through a merge request diff the way a thorough engineer would.

<!-- more -->

## The problem

A typical MR review has a few distinct phases that humans often compress or skip:

1. **Understanding the intent** — what is this change trying to do?
2. **Checking the diff** — does the implementation match the intent? Are there bugs?
3. **Inline suggestions** — specific, actionable feedback on individual lines
4. **Summary** — overall verdict and blocking issues

Most AI review tools dump all of this into a single prompt and get a wall of generic feedback. mr-review structures the review into stages.

## How it works

mr-review connects to your VCS (GitLab, GitHub, Gitea, Forgejo, or Bitbucket) and fetches the diff. It then runs the review in four stages:

```
Brief → Dispatch → Polish → Post
```

**Brief** — the model reads the MR title, description, and file list to form an initial understanding of what the change is trying to accomplish.

**Dispatch** — the model processes the diff in chunks, generating raw inline comments per file. Chunked processing keeps each prompt focused and avoids context overflow on large diffs.

**Polish** — the raw comments are cleaned up: duplicates removed, tone normalised, unhelpful observations dropped.

**Post** — you review the final comment list interactively and approve which ones to post. Nothing goes to your MR without your sign-off.

## Preset-based review modes

Different reviews need different lenses. mr-review ships with four presets:

| Preset | Focus |
|---|---|
| `thorough` | General correctness, logic, maintainability |
| `security` | Input validation, auth, secrets, injection |
| `style` | Naming, structure, consistency with the surrounding codebase |
| `performance` | Hot paths, unnecessary allocations, N+1 queries |

## Model flexibility

mr-review works with Claude, OpenAI, and any OpenAI-compatible endpoint. Point it at a local Ollama instance if you need everything to stay on-premise.

## Getting started

```bash
docker run --rm -it \
  -e GITLAB_TOKEN=your_token \
  ghcr.io/bedrock-python/mr-review \
  review --preset thorough --mr-url https://gitlab.com/org/repo/-/merge_requests/42
```

Full documentation at [bedrock-python.github.io/mr-review](https://bedrock-python.github.io/mr-review/).
