---
title: Blog
description: News, release notes, and deep dives from the Bedrock Python ecosystem.
hide:
  - toc
---

# Blog

<style>
  .md-content__inner > h1:first-of-type { display: none; }
</style>

<section class="bdr-hero" markdown="0">
  <div class="bdr-hero__eyebrow">Bedrock Python</div>
  <h1 class="bdr-hero__title">Blog</h1>
  <p class="bdr-hero__lede">
    Release notes, design decisions, and deep dives from the libraries and tools
    that power our backend services — the infrastructure layer, in writing.
  </p>
</section>

<nav class="bdr-chips" data-bdr-chips markdown="0">
  <a class="bdr-chip is-active" data-bdr-filter="all" href="#">All</a>
  <a class="bdr-chip" data-bdr-filter="libraries" href="category/libraries/">Libraries</a>
  <a class="bdr-chip" data-bdr-filter="tools" href="category/tools/">Tools</a>
  <a class="bdr-chip" data-bdr-filter="design" href="category/design/">Design</a>
  <a class="bdr-chip" data-bdr-filter="tutorials" href="category/tutorials/">Tutorials</a>
  <a class="bdr-chip" data-bdr-filter="releases" href="category/releases/">Releases</a>
  <a class="bdr-chip" data-bdr-filter="meta" href="category/meta/">Meta</a>
  <a class="bdr-chip" data-bdr-filter="archive" href="archive/">Archive</a>
</nav>

<div class="bdr-grid" data-bdr-grid markdown="0">
  <a class="bdr-card" data-bdr-cat="meta" href="posts/2026-05-30-welcome/">
    <div class="bdr-card__visual bdr-card__visual--meta"></div>
    <div class="bdr-card__eyebrow">Meta</div>
    <h3 class="bdr-card__title">Welcome to the Bedrock Python Blog</h3>
    <p class="bdr-card__lede">
      An introduction to the ecosystem — what Bedrock Python is, the libraries that
      form the foundation, reliability, and testing layers, and what you can expect
      from this blog.
    </p>
    <div class="bdr-card__meta">May 30, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tools" href="posts/2026-05-28-introducing-mr-review/">
    <div class="bdr-card__visual bdr-card__visual--tools"></div>
    <div class="bdr-card__eyebrow">Tools</div>
    <h3 class="bdr-card__title">Introducing mr-review: AI-powered merge request reviews</h3>
    <p class="bdr-card__lede">
      A new CLI tool that runs locally and uses an LLM to walk through a merge request
      diff the way a thorough engineer would — staged review with brief, dispatch,
      polish, and post phases, plus presets for thorough, security, style, and
      performance reviews.
    </p>
    <div class="bdr-card__meta">May 28, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="libraries design" href="posts/2026-05-15-transactional-outbox-with-omni-box/">
    <div class="bdr-card__visual bdr-card__visual--libraries"></div>
    <div class="bdr-card__eyebrow">Libraries · Design</div>
    <h3 class="bdr-card__title">The Transactional Outbox pattern in Python: omni-box</h3>
    <p class="bdr-card__lede">
      How <code>omni-box</code> solves the classic dual-write problem between Postgres
      and Kafka using the Transactional Outbox pattern, plus the Inbox side for
      idempotent consumers.
    </p>
    <div class="bdr-card__meta">May 15, 2026</div>
  </a>
</div>
