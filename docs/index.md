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
    A focused set of open-source libraries and developer tools — a service runtime,
    gRPC and HTTP clients, Postgres, Redis, Kafka, Outbox, idempotency, deadlines,
    partitioning, migrations, AI-powered code review — built for the same production
    stack, versioned together, tested together.
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
    <a class="bdr-list__item" href="https://bedrock-python.github.io/servicewright/">
      <p class="bdr-list__name">servicewright</p>
      <p class="bdr-list__desc">One Host, many Entrypoints — FastAPI, gRPC, Litestar, scheduler, daemon, one-shot — under a single Kubernetes-correct lifecycle.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/grpc-server-kit/">
      <p class="bdr-list__name">grpc-server-kit</p>
      <p class="bdr-list__desc">grpc.aio servers: GrpcApp facade, TLS, graceful shutdown, health, streaming-aware interceptors.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/grpc-client-kit/">
      <p class="bdr-list__name">grpc-client-kit</p>
      <p class="bdr-list__desc">gRPC clients: channel pool, load balancing, health monitoring, retries and deadlines that span the whole call.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/clientwright/">
      <p class="bdr-list__name">clientwright</p>
      <p class="bdr-list__desc">One resilience and observability core under the public API of httpx, aiohttp, requests and urllib3.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/sqlalchemy-foundation-kit/">
      <p class="bdr-list__name">sqlalchemy-foundation-kit</p>
      <p class="bdr-list__desc">Async SQLAlchemy session management, Unit of Work, base ORM models, pgbouncer-safe.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/redis-client-kit/">
      <p class="bdr-list__name">redis-client-kit</p>
      <p class="bdr-list__desc">Async and sync Redis clients with cluster support; Pydantic, Prometheus and Dishka as extras.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/aiokafka-foundation-kit/">
      <p class="bdr-list__name">aiokafka-foundation-kit</p>
      <p class="bdr-list__desc">Kafka producer and consumer factories over aiokafka with settings, metrics and tracing.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/omni-box/">
      <p class="bdr-list__name">omni-box</p>
      <p class="bdr-list__desc">Transactional Outbox and Inbox for SQLAlchemy + Kafka stacks.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/idempotency-kit/">
      <p class="bdr-list__name">idempotency-kit</p>
      <p class="bdr-list__desc">Execute an operation once per idempotency key, with collision handling and graceful degradation.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/deadline-budget/">
      <p class="bdr-list__name">deadline-budget</p>
      <p class="bdr-list__desc">One request deadline budget, propagated across every downstream call.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/pg-partsmith/">
      <p class="bdr-list__name">pg-partsmith</p>
      <p class="bdr-list__desc">PostgreSQL partition lifecycle management with a plan you can read before it runs. Library, CLI, container image.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/alembic-gauntlet/">
      <p class="bdr-list__name">alembic-gauntlet</p>
      <p class="bdr-list__desc">Stairway tests for Alembic migrations — every upgrade and downgrade, against a real database.</p>
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
      <p class="bdr-list__desc">Self-hosted AI merge request review for GitLab, GitHub, Gitea, Forgejo and Bitbucket — web UI, staged review, nothing leaves your machine.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/mattermind/">
      <p class="bdr-list__name">mattermind</p>
      <p class="bdr-list__desc">Ask your Mattermost workspace questions in plain language; every answer cites its permalinks.</p>
    </a>
  </div>
</section>
