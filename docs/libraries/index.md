---
title: Libraries
description: Reusable Python packages published to PyPI under the bedrock-python organisation.
hide:
  - navigation
  - toc
---

# Libraries

<style>
  .md-content__inner > h1:first-of-type { display: none; }
</style>

<div class="bdr-catalog" markdown="0">

<section class="bdr-hero bdr-hero--compact" markdown="0">
  <div class="bdr-hero__eyebrow">PyPI · bedrock-python</div>
  <h1 class="bdr-hero__title">Libraries.</h1>
  <p class="bdr-hero__lede">
    Twelve packages, one set of conventions: strict typing, a small core with opt-in extras,
    Release Please, Apache-2.0. Versions are read live from PyPI.
  </p>
</section>

<nav class="bdr-chips bdr-chips--anchors" aria-label="Sections" markdown="0">
  <a class="bdr-chip" href="#runtime">Service runtime &amp; transports <span class="bdr-chip__count">4</span></a>
  <a class="bdr-chip" href="#data">Data &amp; messaging foundations <span class="bdr-chip__count">3</span></a>
  <a class="bdr-chip" href="#reliability">Reliability patterns <span class="bdr-chip__count">3</span></a>
  <a class="bdr-chip" href="#database">Database operations &amp; testing <span class="bdr-chip__count">2</span></a>
  <a class="bdr-chip" href="#template">Start your own <span class="bdr-chip__count">1</span></a>
</nav>

<section class="bdr-group" id="runtime" markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Service runtime &amp; transports</h2>
    <span class="bdr-section-head__note">Run a service; call other services.</span>
  </div>
  <div class="bdr-rows">
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/servicewright/">servicewright</a>
        <p class="bdr-row__desc">One <code>Host</code>, many <code>Entrypoint</code>s: FastAPI, Litestar, gRPC, scheduler, daemon or one-shot batch under a single Kubernetes-correct lifecycle.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="servicewright" href="https://pypi.org/project/servicewright/" title="On PyPI">v0.9.0</a>
        <span>Python 3.12+</span>
        <span>zero-dependency kernel</span>
        <a href="https://github.com/bedrock-python/servicewright">GitHub</a>
      </div>
    </div>
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/clientwright/">clientwright</a>
        <p class="bdr-row__desc">One resilience and observability core wired <em>under</em> the public API of httpx, aiohttp, requests and urllib3 — you get back the genuine native client.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="clientwright" href="https://pypi.org/project/clientwright/" title="On PyPI">v0.2.0</a>
        <span>Python 3.12+</span>
        <span>zero-dependency core</span>
        <a href="https://github.com/bedrock-python/clientwright">GitHub</a>
      </div>
    </div>
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/grpc-server-kit/">grpc-server-kit</a>
        <p class="bdr-row__desc"><code>grpc.aio</code> servers without the boilerplate: a <code>GrpcApp</code> facade, TLS/mTLS, graceful shutdown, health checking, streaming-aware interceptors.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="grpc-server-kit" href="https://pypi.org/project/grpc-server-kit/" title="On PyPI">v0.1.0</a>
        <span>Python 3.12+</span>
        <span>grpcio only</span>
        <a href="https://github.com/bedrock-python/grpc-server-kit">GitHub</a>
      </div>
    </div>
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/grpc-client-kit/">grpc-client-kit</a>
        <p class="bdr-row__desc">The caller side: a channel pool keyed by full channel identity, load balancing, health monitoring, and retries under a deadline that spans the whole call.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="grpc-client-kit" href="https://pypi.org/project/grpc-client-kit/" title="On PyPI">v0.1.0</a>
        <span>Python 3.12+</span>
        <span>grpcio only</span>
        <a href="https://github.com/bedrock-python/grpc-client-kit">GitHub</a>
      </div>
    </div>
  </div>
</section>
<section class="bdr-group" id="data" markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Data &amp; messaging foundations</h2>
    <span class="bdr-section-head__note">Postgres, Redis, Kafka — the clients every service needs.</span>
  </div>
  <div class="bdr-rows">
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/sqlalchemy-foundation-kit/">sqlalchemy-foundation-kit</a>
        <p class="bdr-row__desc">Async session management that stays pgbouncer-safe, a Unit of Work, base ORM models, pool metrics and tracing, dishka and dependency-injector providers.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="sqlalchemy-foundation-kit" href="https://pypi.org/project/sqlalchemy-foundation-kit/" title="On PyPI">v0.2.0</a>
        <span>Python 3.11+</span>
        <a href="https://github.com/bedrock-python/sqlalchemy-foundation-kit">GitHub</a>
      </div>
    </div>
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/redis-client-kit/">redis-client-kit</a>
        <p class="bdr-row__desc">Async and sync redis-py clients with cluster support, pooling, health checks and retries; Pydantic settings, Prometheus and Dishka as extras.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="redis-client-kit" href="https://pypi.org/project/redis-client-kit/" title="On PyPI">v0.1.2</a>
        <span>Python 3.10+</span>
        <a href="https://github.com/bedrock-python/redis-client-kit">GitHub</a>
      </div>
    </div>
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/aiokafka-foundation-kit/">aiokafka-foundation-kit</a>
        <p class="bdr-row__desc">Producer and consumer factories over aiokafka with Pydantic settings, retry policies, health checks, Prometheus metrics and OpenTelemetry.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="aiokafka-foundation-kit" href="https://pypi.org/project/aiokafka-foundation-kit/" title="On PyPI">v0.1.1</a>
        <span>Python 3.11+</span>
        <a href="https://github.com/bedrock-python/aiokafka-foundation-kit">GitHub</a>
      </div>
    </div>
  </div>
</section>
<section class="bdr-group" id="reliability" markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Reliability patterns</h2>
    <span class="bdr-section-head__note">Exactly-once effects and bounded latency.</span>
  </div>
  <div class="bdr-rows">
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/omni-box/">omni-box</a>
        <p class="bdr-row__desc">Transactional Outbox and Inbox: the event goes in the same transaction as the business row, out to Kafka from a background publisher, in with deduplication.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="omni-box" href="https://pypi.org/project/omni-box/" title="On PyPI">v0.1.1</a>
        <span>Python 3.12+</span>
        <a href="https://github.com/bedrock-python/omni-box">GitHub</a>
      </div>
    </div>
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/idempotency-kit/">idempotency-kit</a>
        <p class="bdr-row__desc">Execute an operation once per idempotency key: a coordinator and a decorator over Redis, collision handling, graceful degradation, metrics.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="idempotency-kit" href="https://pypi.org/project/idempotency-kit/" title="On PyPI">v0.1.1</a>
        <span>Python 3.11+</span>
        <a href="https://github.com/bedrock-python/idempotency-kit">GitHub</a>
      </div>
    </div>
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/deadline-budget/">deadline-budget</a>
        <p class="bdr-row__desc">One request deadline budget with per-call caps and a safety margin — the budget that clientwright, grpc-client-kit and servicewright propagate across hops.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="deadline-budget" href="https://pypi.org/project/deadline-budget/" title="On PyPI">v0.1.2</a>
        <span>Python 3.10+</span>
        <span>zero dependencies</span>
        <a href="https://github.com/bedrock-python/deadline-budget">GitHub</a>
      </div>
    </div>
  </div>
</section>
<section class="bdr-group" id="database" markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Database operations &amp; testing</h2>
    <span class="bdr-section-head__note">Partitions planned, migrations tested.</span>
  </div>
  <div class="bdr-rows">
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/pg-partsmith/">pg-partsmith</a>
        <p class="bdr-row__desc">PostgreSQL partition lifecycle management with a plan you can read before it runs: RANGE, LIST and HASH nested to any depth — as a library, a CLI and a container image.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="pg-partsmith" href="https://pypi.org/project/pg-partsmith/" title="On PyPI">v1.5.0</a>
        <span>Python 3.11+</span>
        <span>stable</span>
        <a href="https://github.com/bedrock-python/pg-partsmith">GitHub</a>
      </div>
    </div>
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://bedrock-python.github.io/alembic-gauntlet/">alembic-gauntlet</a>
        <p class="bdr-row__desc">A pytest plugin that runs Alembic migrations through the gauntlet: stairway up and down, models drift, single head, full downgrade, naming conventions.</p>
      </div>
      <div class="bdr-row__meta">
        <a class="bdr-row__version" data-pypi="alembic-gauntlet" href="https://pypi.org/project/alembic-gauntlet/" title="On PyPI">v0.2.1</a>
        <span>Python 3.10+</span>
        <span>pytest plugin</span>
        <a href="https://github.com/bedrock-python/alembic-gauntlet">GitHub</a>
      </div>
    </div>
  </div>
</section>
<section class="bdr-group" id="template" markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Start your own</h2>
    <span class="bdr-section-head__note">Every library above began here.</span>
  </div>
  <div class="bdr-rows">
    <div class="bdr-row">
      <div class="bdr-row__main">
        <a class="bdr-row__name" href="https://github.com/bedrock-python/python-library-template">python-library-template</a>
        <p class="bdr-row__desc">The Copier template: uv, hatchling, ruff, mypy, pytest with unit and integration lanes, Zensical docs, Release Please with PyPI trusted publishing, and the org repo-settings script.</p>
      </div>
      <div class="bdr-row__meta">
        <span>Copier template</span>
      </div>
    </div>
  </div>
</section>

</div>
