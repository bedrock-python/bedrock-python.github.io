---
title: Bedrock Python
description: Production-grade Python libraries and developer tools for the infrastructure layer of modern backend services.
hide:
  - navigation
  - toc
---

# Bedrock Python

<style>
  /* Landing page — hide the page H1 (we render our own hero) and the edit button. */
  .md-content__button { display: none !important; }
  .md-content__inner > h1:first-of-type { display: none; }
  .md-main__inner { margin-top: 0; }
</style>

<section class="bdr-hero" markdown="0">
  <div class="bdr-hero__eyebrow">The Bedrock Python ecosystem</div>
  <h1 class="bdr-hero__title">Foundations for serious Python services.</h1>
  <p class="bdr-hero__lede">
    A focused set of open-source libraries and developer tools — Postgres, Redis, Kafka,
    Outbox, idempotency, partitioning, migrations, AI-powered code review — built for
    the same production stack, versioned together, tested together.
  </p>
  <div class="bdr-hero__actions">
    <a class="bdr-btn bdr-btn--primary" href="libraries/">Browse libraries →</a>
    <a class="bdr-btn bdr-btn--ghost" href="blog/">Read the blog</a>
  </div>
</section>

<section class="bdr-featured" markdown="0">
  <div class="bdr-featured__visual"></div>
  <div>
    <div class="bdr-featured__eyebrow">Featured · Tools</div>
    <h2 class="bdr-featured__title">
      <a href="blog/posts/2026-05-28-introducing-mr-review/">Introducing mr-review: AI-powered merge request reviews</a>
    </h2>
    <p class="bdr-featured__lede">
      A new CLI tool that runs locally and walks through merge-request diffs the way a
      thorough engineer would — staged review with brief, dispatch, polish and post phases,
      plus presets for thorough, security, style, and performance.
    </p>
    <div class="bdr-featured__meta">
      <span>May 28, 2026</span>
      <span>·</span>
      <span>Tools</span>
    </div>
  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Latest from the blog</h2>
    <a class="bdr-section-head__link" href="blog/">See all posts →</a>
  </div>

  <div class="bdr-grid">
    <a class="bdr-card" href="blog/posts/2026-05-30-welcome/">
      <div class="bdr-card__visual bdr-card__visual--meta"></div>
      <div class="bdr-card__eyebrow">Meta</div>
      <h3 class="bdr-card__title">Welcome to the Bedrock Python Blog</h3>
      <p class="bdr-card__lede">
        An introduction to the ecosystem — what Bedrock Python is, the libraries that
        form the foundation, reliability, and testing layers, and what you can expect.
      </p>
      <div class="bdr-card__meta">May 30, 2026</div>
    </a>

    <a class="bdr-card" href="blog/posts/2026-05-28-introducing-mr-review/">
      <div class="bdr-card__visual bdr-card__visual--tools"></div>
      <div class="bdr-card__eyebrow">Tools</div>
      <h3 class="bdr-card__title">Introducing mr-review</h3>
      <p class="bdr-card__lede">
        A new CLI tool that runs locally and uses an LLM to walk through a merge
        request diff the way a thorough engineer would.
      </p>
      <div class="bdr-card__meta">May 28, 2026</div>
    </a>

    <a class="bdr-card" href="blog/posts/2026-05-15-transactional-outbox-with-omni-box/">
      <div class="bdr-card__visual bdr-card__visual--libraries"></div>
      <div class="bdr-card__eyebrow">Libraries · Design</div>
      <h3 class="bdr-card__title">The Transactional Outbox pattern in Python</h3>
      <p class="bdr-card__lede">
        How <code>omni-box</code> solves the classic dual-write problem between Postgres
        and Kafka using the Transactional Outbox pattern, plus the Inbox side for
        idempotent consumers.
      </p>
      <div class="bdr-card__meta">May 15, 2026</div>
    </a>
  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Libraries</h2>
    <a class="bdr-section-head__link" href="libraries/">All libraries →</a>
  </div>

  <div class="bdr-list">
    <a class="bdr-list__item" href="https://bedrock-python.github.io/sqlalchemy-foundation-kit/">
      <p class="bdr-list__name">sqlalchemy-foundation-kit</p>
      <p class="bdr-list__desc">Async SQLAlchemy session management, base ORM models, Unit of Work.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/redis-client-kit/">
      <p class="bdr-list__name">redis-client-kit</p>
      <p class="bdr-list__desc">Redis client with optional Pydantic serialization and OpenTelemetry spans.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/aiokafka-foundation-kit/">
      <p class="bdr-list__name">aiokafka-foundation-kit</p>
      <p class="bdr-list__desc">asyncio Kafka producer / consumer foundations with structured logging.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/omni-box/">
      <p class="bdr-list__name">omni-box</p>
      <p class="bdr-list__desc">Transactional Outbox and Inbox patterns for SQLAlchemy + Kafka stacks.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/idempotency-kit/">
      <p class="bdr-list__name">idempotency-kit</p>
      <p class="bdr-list__desc">Idempotency key guards for HTTP endpoints and Kafka consumers.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/alembic-gauntlet/">
      <p class="bdr-list__name">alembic-gauntlet</p>
      <p class="bdr-list__desc">Stairway migration testing — every upgrade and downgrade, against a real DB.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/pg-partsmith/">
      <p class="bdr-list__name">pg-partsmith</p>
      <p class="bdr-list__desc">PostgreSQL declarative table partitioning helpers for SQLAlchemy projects.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/deadline-budget/">
      <p class="bdr-list__name">deadline-budget</p>
      <p class="bdr-list__desc">Deadline and budget propagation for async task chains.</p>
    </a>
  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Tools</h2>
    <a class="bdr-section-head__link" href="tools/">All tools →</a>
  </div>

  <div class="bdr-list">
    <a class="bdr-list__item" href="https://bedrock-python.github.io/mr-review/">
      <p class="bdr-list__name">mr-review</p>
      <p class="bdr-list__desc">AI-powered merge request review for GitLab, GitHub, Gitea, and more.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/mattermind/">
      <p class="bdr-list__name">mattermind</p>
      <p class="bdr-list__desc">Ask natural-language questions about your Mattermost workspace.</p>
    </a>
  </div>
</section>
