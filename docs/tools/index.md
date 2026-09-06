---
title: Tools
description: Standalone developer tools — install and run, no integration required.
hide:
  - toc
---

# Tools

<style>
  .md-content__inner > h1:first-of-type { display: none; }
</style>

<section class="bdr-hero" markdown="0">
  <div class="bdr-hero__eyebrow">Standalone tools</div>
  <h1 class="bdr-hero__title">Tools.</h1>
  <p class="bdr-hero__lede">
    Developer tools with Python underneath — no integration into your codebase required.
    Install or <code>docker compose up</code>, point at your repository or workspace, and run.
  </p>
</section>

<section markdown="0">
  <div class="bdr-list">
    <a class="bdr-list__item" href="https://bedrock-python.github.io/mr-review/">
      <p class="bdr-list__name">mr-review</p>
      <p class="bdr-list__desc">
        AI-powered merge request review, self-hosted. One <code>docker compose up</code> brings
        a web UI and a REST API; connect GitLab, GitHub, Gitea, Forgejo or Bitbucket and Claude,
        OpenAI or any OpenAI-compatible model. A review runs in four stages — Brief, Dispatch,
        Polish, Post — and every inline comment waits for your approval before it is posted back
        to the MR. No accounts, no cloud, no data leaves your machine.
      </p>
      <p class="bdr-list__meta">
        <span>Docker · images on GHCR</span>
        <span>Python 3.12 backend</span>
      </p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/mattermind/">
      <p class="bdr-list__name">mattermind</p>
      <p class="bdr-list__desc">
        Ask your Mattermost workspace questions in plain language. An agentic loop with tool
        calling — full-text search, thread and permalink lookup, user resolution — that cites
        every claim with a permalink. <code>mattermind ask</code> for one-offs,
        <code>mattermind chat</code> for a terminal session, <code>--json</code> for scripts;
        session-token auth for SSO setups and a token-budget guard.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="mattermind">v0.1.1</span>
        <span>Python 3.12+</span>
        <span>uv tool install mattermind</span>
      </p>
    </a>
  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Shipped with a library</h2>
  </div>
  <div class="bdr-list">
    <a class="bdr-list__item" href="https://bedrock-python.github.io/pg-partsmith/guide/cli/">
      <p class="bdr-list__name">pg-partsmith CLI</p>
      <p class="bdr-list__desc">
        <code>pg-partsmith plan</code>, <code>apply</code>, <code>validate</code> and
        <code>backfill</code> over a YAML or JSON document, with a saved plan as the artifact
        between plan and apply and exit codes a CronJob or a CI step can read. Also a container
        image at <code>ghcr.io/bedrock-python/pg-partsmith</code> for stacks with no Python in
        them: a Job, a CronJob, an init container.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="pg-partsmith">v1.5.0</span>
        <span>pip install "pg-partsmith[cli]"</span>
      </p>
    </a>
  </div>
</section>
