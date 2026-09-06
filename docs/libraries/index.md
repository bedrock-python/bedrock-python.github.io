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
    Twelve packages, one set of conventions: strict typing, a small core with
    opt-in extras instead of hard dependencies, semantic versioning via Release
    Please, Apache-2.0, and every release published to PyPI under the
    <code>bedrock-python</code> organisation. Versions below are read live from PyPI.
  </p>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Service runtime &amp; transports</h2>
  </div>
  <div class="bdr-list">
    <a class="bdr-list__item" href="https://bedrock-python.github.io/servicewright/">
      <p class="bdr-list__name">servicewright</p>
      <p class="bdr-list__desc">
        One <code>Host</code>, many <code>Entrypoint</code>s. Describe a service once as an
        <code>AppSpec</code> — DI container, lifecycle, observability, warmup, health — and run it
        as FastAPI, Litestar, gRPC, a scheduler, a background daemon or a one-shot batch under a
        single Kubernetes-correct lifecycle. A <code>ServiceError</code> renders as an RFC 9457
        problem document over HTTP and as the mapped status over gRPC.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="servicewright">v0.9.0</span>
        <span>Python 3.12+</span>
        <span>zero-dependency kernel</span>
      </p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/grpc-server-kit/">
      <p class="bdr-list__name">grpc-server-kit</p>
      <p class="bdr-list__desc">
        <code>grpc.aio</code> servers without the boilerplate: a one-object <code>GrpcApp</code>
        facade, validated channel options, TLS/mTLS credential loading, graceful signal-driven
        shutdown, health checking and streaming-aware interceptors. Reflection, channelz,
        Prometheus, OpenTelemetry, Sentry, Dishka and pydantic settings are extras.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="grpc-server-kit">v0.1.0</span>
        <span>Python 3.12+</span>
        <span>core depends on grpcio only</span>
      </p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/grpc-client-kit/">
      <p class="bdr-list__name">grpc-client-kit</p>
      <p class="bdr-list__desc">
        The caller-side half of a production gRPC setup: a channel pool keyed by the full
        identity of a channel, client-side load balancing, active health monitoring, passive
        quarantine on the first <code>UNAVAILABLE</code>, and one fixed-order chain of
        streaming-aware interceptors for retries, deadlines, circuit breaking, logging, tracing
        and metrics. A timeout is the budget of the whole call, not of one attempt.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="grpc-client-kit">v0.1.0</span>
        <span>Python 3.12+</span>
        <span>core depends on grpcio only</span>
      </p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/clientwright/">
      <p class="bdr-list__name">clientwright</p>
      <p class="bdr-list__desc">
        One resilience and observability core for HTTP clients — retries with a budget, circuit
        breaking, a total deadline across attempts and redirects, and a frozen
        <code>http_client_*</code> telemetry schema — wired <em>under</em> the public API of
        httpx, aiohttp, requests and urllib3. You get back the genuine native client, not a
        wrapper, and a report of any configuration the adapter could not honour.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="clientwright">v0.2.0</span>
        <span>Python 3.12+</span>
        <span>zero-dependency core</span>
      </p>
    </a>
  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Data &amp; messaging foundations</h2>
  </div>
  <div class="bdr-list">
    <a class="bdr-list__item" href="https://bedrock-python.github.io/sqlalchemy-foundation-kit/">
      <p class="bdr-list__name">sqlalchemy-foundation-kit</p>
      <p class="bdr-list__desc">
        The async SQLAlchemy foundation you rewrite for every service, once: an
        <code>AsyncSessionManager</code> that stays compatible with pgbouncer transaction mode,
        a Unit of Work with automatic commit and rollback, base ORM models with mixins and custom
        types, Prometheus connection-pool metrics, OpenTelemetry tracing, and providers for
        dishka and dependency-injector.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="sqlalchemy-foundation-kit">v0.2.0</span>
        <span>Python 3.11+</span>
      </p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/redis-client-kit/">
      <p class="bdr-list__name">redis-client-kit</p>
      <p class="bdr-list__desc">
        Async and sync redis-py clients with cluster support, connection pooling, health checks,
        retries and TLS in the core; Pydantic settings, Prometheus metrics and Dishka providers
        as extras. Settings can be a dataclass, a dict or a Pydantic model — the client only
        asks for a protocol.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="redis-client-kit">v0.1.2</span>
        <span>Python 3.10+</span>
      </p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/aiokafka-foundation-kit/">
      <p class="bdr-list__name">aiokafka-foundation-kit</p>
      <p class="bdr-list__desc">
        Producer and consumer factories over aiokafka with Pydantic settings, configurable retry
        policies, cluster health checks and topic management. Prometheus metrics and
        OpenTelemetry instrumentation, plus dishka and dependency-injector providers, ship as
        extras.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="aiokafka-foundation-kit">v0.1.1</span>
        <span>Python 3.11+</span>
      </p>
    </a>
  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Reliability patterns</h2>
  </div>
  <div class="bdr-list">
    <a class="bdr-list__item" href="https://bedrock-python.github.io/omni-box/">
      <p class="bdr-list__name">omni-box</p>
      <p class="bdr-list__desc">
        Transactional Outbox and Inbox for async Python: write the event in the same database
        transaction as the business row, publish to Kafka from a background publisher, consume
        with deduplication. PostgreSQL storage, an aiokafka broker adapter, and a composable
        pipeline with metrics, OpenTelemetry, DLQ and circuit-breaker steps.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="omni-box">v0.1.1</span>
        <span>Python 3.12+</span>
      </p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/idempotency-kit/">
      <p class="bdr-list__name">idempotency-kit</p>
      <p class="bdr-list__desc">
        Execute an operation once per idempotency key, however many times it is called. A
        coordinator and an <code>@async_idempotent</code> decorator over a Redis store, with
        collision handling for concurrent requests, graceful degradation when the store is
        unavailable, bulk operations, and hit / miss / collision / latency metrics.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="idempotency-kit">v0.1.1</span>
        <span>Python 3.11+</span>
      </p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/deadline-budget/">
      <p class="bdr-list__name">deadline-budget</p>
      <p class="bdr-list__desc">
        A request deadline budget for distributed orchestrations: one total budget, per-call
        caps, a safety margin, and a timeout for every downstream call computed from what is
        left. The budget that clientwright, grpc-client-kit and servicewright propagate across
        hops.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="deadline-budget">v0.1.2</span>
        <span>Python 3.10+</span>
        <span>zero dependencies</span>
      </p>
    </a>
  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Database operations &amp; testing</h2>
  </div>
  <div class="bdr-list">
    <a class="bdr-list__item" href="https://bedrock-python.github.io/pg-partsmith/">
      <p class="bdr-list__name">pg-partsmith</p>
      <p class="bdr-list__desc">
        PostgreSQL partition lifecycle management with a plan you can read before it runs.
        <code>RANGE</code>, <code>LIST</code> and <code>HASH</code> schemes nested to any depth,
        create-ahead and expiry policies, batched data movement, and a maintenance plan of typed
        operations with a reason on each. A library, a CLI and a container image — one version
        number. No extension, no superuser, no scheduler of its own.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="pg-partsmith">v1.5.0</span>
        <span>Python 3.11+</span>
        <span>production / stable</span>
      </p>
    </a>
    <a class="bdr-list__item" href="https://bedrock-python.github.io/alembic-gauntlet/">
      <p class="bdr-list__name">alembic-gauntlet</p>
      <p class="bdr-list__desc">
        A pytest plugin that runs your Alembic migrations through the gauntlet against a real
        PostgreSQL: stairway upgrade and downgrade for every revision, schema-versus-models
        drift, a single head, a full downgrade to base, and naming conventions on indexes and
        foreign keys. Inherit one base class and you get all five tests.
      </p>
      <p class="bdr-list__meta">
        <span class="bdr-list__version" data-pypi="alembic-gauntlet">v0.2.1</span>
        <span>Python 3.10+</span>
        <span>pytest plugin</span>
      </p>
    </a>
  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Start your own</h2>
  </div>
  <div class="bdr-list">
    <a class="bdr-list__item" href="https://github.com/bedrock-python/python-library-template">
      <p class="bdr-list__name">python-library-template</p>
      <p class="bdr-list__desc">
        The Copier template every library above starts from: uv and hatchling, ruff and mypy,
        pytest with unit and integration lanes, Zensical docs, Release Please with
        PyPI trusted publishing, Dependabot, and a script that applies the org's repository
        settings. One command from an empty directory to a release-ready repository.
      </p>
      <p class="bdr-list__meta">
        <span>Copier template</span>
        <span>GitHub</span>
      </p>
    </a>
  </div>
</section>
