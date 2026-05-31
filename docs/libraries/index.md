---
title: Libraries
description: Reusable Python packages published to PyPI under the bedrock-python organisation.
hide:
  - toc
---

# Libraries

<style>
  .md-content__inner > h1:first-of-type { display: none; }
</style>

<section class="bdr-hero" markdown="0">
  <div class="bdr-hero__eyebrow">PyPI · bedrock-python</div>
  <h1 class="bdr-hero__title">Libraries.</h1>
  <p class="bdr-hero__lede">
    Every Bedrock Python library follows the same conventions: strict typing,
    90%+ coverage, semantic versioning via Release Please, and published to PyPI
    under the <code>bedrock-python</code> organisation.
  </p>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Foundation layer</h2>
  </div>
  <div class="bdr-list">
    <a class="bdr-list__item" href="https://bedrock-python.github.io/sqlalchemy-foundation-kit/">
      <p class="bdr-list__name">sqlalchemy-foundation-kit</p>
      <p class="bdr-list__desc">Async SQLAlchemy session management, base ORM models with UUIDs and UTC timestamps, AsyncSession lifecycle wired to a Unit of Work.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/redis-client-kit/">
      <p class="bdr-list__name">redis-client-kit</p>
      <p class="bdr-list__desc">redis-py wrapper with optional Pydantic serialization and OpenTelemetry spans on every command.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/aiokafka-foundation-kit/">
      <p class="bdr-list__name">aiokafka-foundation-kit</p>
      <p class="bdr-list__desc">asyncio Kafka producer/consumer abstraction over aiokafka with structured logging and metrics.</p>
    </a>
  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Reliability layer</h2>
  </div>
  <div class="bdr-list">
    <a class="bdr-list__item" href="https://bedrock-python.github.io/omni-box/">
      <p class="bdr-list__name">omni-box</p>
      <p class="bdr-list__desc">Transactional Outbox and Inbox patterns — write events in the same DB transaction as your business data, publish to Kafka asynchronously, consume idempotently.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/idempotency-kit/">
      <p class="bdr-list__name">idempotency-kit</p>
      <p class="bdr-list__desc">Idempotency key guards for HTTP endpoints and Kafka consumers — at-most-once semantics where you need them.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/deadline-budget/">
      <p class="bdr-list__name">deadline-budget</p>
      <p class="bdr-list__desc">Deadline and budget propagation across async task chains so no task runs longer than it should.</p>
    </a>
  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Testing &amp; tooling</h2>
  </div>
  <div class="bdr-list">
    <a class="bdr-list__item" href="https://bedrock-python.github.io/alembic-gauntlet/">
      <p class="bdr-list__name">alembic-gauntlet</p>
      <p class="bdr-list__desc">Stairway tests for Alembic migrations — every upgrade and downgrade, in order, against a real database.</p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/pg-partsmith/">
      <p class="bdr-list__name">pg-partsmith</p>
      <p class="bdr-list__desc">PostgreSQL declarative table partitioning helpers for SQLAlchemy projects.</p>
    </a>
  </div>
</section>
