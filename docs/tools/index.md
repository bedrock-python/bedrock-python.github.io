---
title: Tools
description: Standalone developer tools — install and run, no integration required.
hide:
  - navigation
  - toc
---

# Tools

<style>
  .md-content__inner > h1:first-of-type { display: none; }
</style>

<div class="bdr-catalog" markdown="0">

<section class="bdr-hero bdr-hero--compact" markdown="0">
  <div class="bdr-hero__eyebrow">Standalone tools</div>
  <h1 class="bdr-hero__title">Tools.</h1>
  <p class="bdr-hero__lede">
    Developer tools with Python underneath — no integration into your codebase required.
  </p>
</section>

<section class="bdr-group" id="standalone" markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Standalone</h2>
    <span class="bdr-section-head__note">Install or <code>docker compose up</code>, point at your repository or workspace, run.</span>
  </div>
  <div class="bdr-rows">
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/mr-review/">mr-review</a>
        <p class="bdr-row__desc">Self-hosted AI merge request review for GitLab, GitHub, Gitea, Forgejo and Bitbucket with Claude, OpenAI or any compatible model: a web UI, a four-stage review, and every comment approved by you before it is posted.</p>
      </div>
      <div class="bdr-row__meta">
        <span>Python 3.12 backend</span>
        <span>Docker · images on GHCR</span>
        <a href="https://github.com/bedrock-python/mr-review">GitHub</a>
      </div>
    </div>
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/mattermind/">mattermind</a>
        <p class="bdr-row__desc">Ask your Mattermost workspace questions in plain language: an agentic loop over full-text search that cites every claim with a permalink. <code>ask</code>, a <code>chat</code> TUI, <code>--json</code> for scripts.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="mattermind" href="https://pypi.org/project/mattermind/" title="On PyPI">v0.1.1</a>
        <span>Python 3.12+</span>
        <span>uv tool install</span>
        <a href="https://github.com/bedrock-python/mattermind">GitHub</a>
      </div>
    </div>
  </div>
</section>
<section class="bdr-group" id="from-libraries" markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Shipped with a library</h2>
    <span class="bdr-section-head__note">A library that is also a command.</span>
  </div>
  <div class="bdr-rows">
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/pg-partsmith/guide/cli/">pg-partsmith CLI</a>
        <p class="bdr-row__desc"><code>plan</code>, <code>apply</code>, <code>validate</code> and <code>backfill</code> over a YAML document, exit codes a CronJob can read, and a container image at <code>ghcr.io/bedrock-python/pg-partsmith</code> for stacks with no Python in them.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="pg-partsmith" href="https://pypi.org/project/pg-partsmith/" title="On PyPI">v1.5.0</a>
        <span>pip install "pg-partsmith[cli]"</span>
        <a href="https://github.com/bedrock-python/pg-partsmith">GitHub</a>
      </div>
    </div>
  </div>
</section>

</div>
