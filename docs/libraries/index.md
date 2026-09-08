---
title: Libraries
description: Find the right building blocks for your Python service. Twelve libraries for runtimes, clients, data, reliability, and database operations.
hide:
  - navigation
  - toc
---

<div class="bdr-catalog bdr-library-page" data-library-page markdown="0">
  <header class="bdr-lib-hero">
    <div class="bdr-lib-hero__copy">
      <div class="bdr-lib-eyebrow"><span></span> THE BUILDING BLOCKS / LIBRARIES</div>
      <h1>Small pieces.<br><em>Strong foundations.</em></h1>
      <p>Twelve Python libraries for the infrastructure behind your service. Pick what you need. Keep the conventions that make it all fit together.</p>
      <div class="bdr-lib-principles"><span>Strict typing</span><span>Opt-in extras</span><span>Apache 2.0</span></div>
      <a class="bdr-lib-hero__link" href="#library-directory">Find your building blocks <span aria-hidden="true">↓</span></a>
    </div>
    <div class="bdr-lib-composer" aria-label="An example stack of independent Python packages">
      <div class="bdr-lib-composer__header"><span>COMPOSE YOUR STACK</span><span aria-hidden="true">⌘</span></div>
      <div class="bdr-lib-composer__packages">
        <a class="bdr-lib-piece bdr-lib-piece--runtime" href="#package-servicewright"><span class="bdr-lib-piece__icon" aria-hidden="true">◷</span><div><span>THE LIFECYCLE</span><strong>servicewright</strong></div><span class="bdr-lib-piece__arrow" aria-hidden="true">↗</span></a>
        <div class="bdr-lib-composer__connector" aria-hidden="true">+</div>
        <a class="bdr-lib-piece bdr-lib-piece--data" href="#package-sqlalchemy-foundation-kit"><span class="bdr-lib-piece__icon" aria-hidden="true">▤</span><div><span>THE DATA LAYER</span><strong>sqlalchemy-foundation-kit</strong></div><span class="bdr-lib-piece__arrow" aria-hidden="true">↗</span></a>
        <div class="bdr-lib-composer__connector" aria-hidden="true">+</div>
        <a class="bdr-lib-piece bdr-lib-piece--reliability" href="#package-omni-box"><span class="bdr-lib-piece__icon" aria-hidden="true">⇢</span><div><span>THE DELIVERY GUARANTEE</span><strong>omni-box</strong></div><span class="bdr-lib-piece__arrow" aria-hidden="true">↗</span></a>
      </div>
      <div class="bdr-lib-composer__footer"><span aria-hidden="true">↳</span> Independent packages. A shared engineering standard.</div>
    </div>
  </header>

  <nav class="bdr-lib-layers" aria-label="Library categories">
    <a href="#runtime" class="bdr-lib-layer" data-layer="runtime"><span class="bdr-lib-layer__top"><span>01 / BUILD</span><span>4 libraries</span></span><strong>Runtime &amp; transports <span aria-hidden="true">↗</span></strong><span>Services, HTTP &amp; gRPC</span></a>
    <a href="#data" class="bdr-lib-layer" data-layer="data"><span class="bdr-lib-layer__top"><span>02 / CONNECT</span><span>3 libraries</span></span><strong>Data &amp; messaging <span aria-hidden="true">↗</span></strong><span>Postgres, Redis &amp; Kafka</span></a>
    <a href="#reliability" class="bdr-lib-layer" data-layer="reliability"><span class="bdr-lib-layer__top"><span>03 / PROTECT</span><span>3 libraries</span></span><strong>Reliability patterns <span aria-hidden="true">↗</span></strong><span>Outbox, idempotency &amp; deadlines</span></a>
    <a href="#database" class="bdr-lib-layer" data-layer="database"><span class="bdr-lib-layer__top"><span>04 / OPERATE</span><span>2 libraries</span></span><strong>Database operations <span aria-hidden="true">↗</span></strong><span>Partitions &amp; migration tests</span></a>
  </nav>

  <section class="bdr-lib-directory" id="library-directory" aria-label="Package directory">
    <div class="bdr-lib-directory__heading"><h2>The package directory</h2><span>12 Bedrock libraries + a few useful neighbours</span></div>
    <div class="bdr-lib-toolbar">
      <div class="bdr-lib-search" role="search" aria-label="Find a library" data-library-controls hidden><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><label class="bdr-lib-sr-only" for="library-query">Search packages, capabilities, or technologies</label><input id="library-query" data-library-query type="search" placeholder="Find a package, a capability, a technology…" autocomplete="off" enterkeyhint="search"><button type="button" data-library-clear aria-label="Clear package search" hidden>×</button></div>
      <nav class="bdr-lib-extras" aria-label="More resources"><a href="#template">Start your own ↗</a><a href="#recommended">Community picks ↗</a></nav>
    </div>
    <p class="bdr-lib-status" data-library-status role="status" aria-live="polite" hidden></p>

    <section class="bdr-lib-group" id="runtime" data-library-group data-layer="runtime" aria-labelledby="library-runtime-title">
      <div class="bdr-lib-group__heading"><div><span class="bdr-lib-group__number">01</span><h2 id="library-runtime-title">Service runtime &amp; transports</h2><span class="bdr-lib-group__count">4</span></div><p>Run a service; call other services.</p></div>
      <div class="bdr-lib-grid">
        <article class="bdr-package" id="package-servicewright" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3v4m0 10v4M3 12h4m10 0h4"/><rect x="7" y="7" width="10" height="10" rx="2"/></svg></span>
            <a class="bdr-package__version" data-pypi="servicewright" href="https://pypi.org/project/servicewright/" title="servicewright on PyPI">v0.9.0</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/servicewright/">servicewright<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">One <code>Host</code>, many <code>Entrypoint</code>s: FastAPI, Litestar, gRPC, scheduler, daemon or one-shot batch under a single Kubernetes-correct lifecycle.</p>
          <div class="bdr-package__tags"><span>Python 3.12+</span><span>zero-dependency kernel</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/servicewright/">Documentation <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/servicewright">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add servicewright</code><button type="button" data-copy-command="uv add servicewright" aria-label="Copy install command for servicewright" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-clientwright" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3v4m0 10v4M3 12h4m10 0h4"/><rect x="7" y="7" width="10" height="10" rx="2"/></svg></span>
            <a class="bdr-package__version" data-pypi="clientwright" href="https://pypi.org/project/clientwright/" title="clientwright on PyPI">v0.2.0</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/clientwright/">clientwright<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">One resilience and observability core wired <em>under</em> the public API of httpx, aiohttp, requests and urllib3 — you get back the genuine native client.</p>
          <div class="bdr-package__tags"><span>Python 3.12+</span><span>zero-dependency core</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/clientwright/">Documentation <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/clientwright">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add clientwright</code><button type="button" data-copy-command="uv add clientwright" aria-label="Copy install command for clientwright" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-grpc-server-kit" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3v4m0 10v4M3 12h4m10 0h4"/><rect x="7" y="7" width="10" height="10" rx="2"/></svg></span>
            <a class="bdr-package__version" data-pypi="grpc-server-kit" href="https://pypi.org/project/grpc-server-kit/" title="grpc-server-kit on PyPI">v0.1.0</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/grpc-server-kit/">grpc-server-kit<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description"><code>grpc.aio</code> servers without the boilerplate: a <code>GrpcApp</code> facade, TLS/mTLS, graceful shutdown, health checking, streaming-aware interceptors.</p>
          <div class="bdr-package__tags"><span>Python 3.12+</span><span>grpcio only</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/grpc-server-kit/">Documentation <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/grpc-server-kit">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add grpc-server-kit</code><button type="button" data-copy-command="uv add grpc-server-kit" aria-label="Copy install command for grpc-server-kit" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-grpc-client-kit" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3v4m0 10v4M3 12h4m10 0h4"/><rect x="7" y="7" width="10" height="10" rx="2"/></svg></span>
            <a class="bdr-package__version" data-pypi="grpc-client-kit" href="https://pypi.org/project/grpc-client-kit/" title="grpc-client-kit on PyPI">v0.1.0</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/grpc-client-kit/">grpc-client-kit<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">The caller side: a channel pool keyed by full channel identity, load balancing, health monitoring, and retries under a deadline that spans the whole call.</p>
          <div class="bdr-package__tags"><span>Python 3.12+</span><span>grpcio only</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/grpc-client-kit/">Documentation <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/grpc-client-kit">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add grpc-client-kit</code><button type="button" data-copy-command="uv add grpc-client-kit" aria-label="Copy install command for grpc-client-kit" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
      </div>
    </section>
    <section class="bdr-lib-group" id="data" data-library-group data-layer="data" aria-labelledby="library-data-title">
      <div class="bdr-lib-group__heading"><div><span class="bdr-lib-group__number">02</span><h2 id="library-data-title">Data &amp; messaging foundations</h2><span class="bdr-lib-group__count">3</span></div><p>Postgres, Redis, Kafka — the clients every service needs.</p></div>
      <div class="bdr-lib-grid">
        <article class="bdr-package" id="package-sqlalchemy-foundation-kit" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v14c0 1.7 3.1 3 7 3s7-1.3 7-3V5M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/></svg></span>
            <a class="bdr-package__version" data-pypi="sqlalchemy-foundation-kit" href="https://pypi.org/project/sqlalchemy-foundation-kit/" title="sqlalchemy-foundation-kit on PyPI">v0.2.0</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/sqlalchemy-foundation-kit/">sqlalchemy-foundation-kit<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Async session management that stays pgbouncer-safe, a Unit of Work, base ORM models, pool metrics and tracing, dishka and dependency-injector providers.</p>
          <div class="bdr-package__tags"><span>Python 3.11+</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/sqlalchemy-foundation-kit/">Documentation <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/sqlalchemy-foundation-kit">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add sqlalchemy-foundation-kit</code><button type="button" data-copy-command="uv add sqlalchemy-foundation-kit" aria-label="Copy install command for sqlalchemy-foundation-kit" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-redis-client-kit" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v14c0 1.7 3.1 3 7 3s7-1.3 7-3V5M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/></svg></span>
            <a class="bdr-package__version" data-pypi="redis-client-kit" href="https://pypi.org/project/redis-client-kit/" title="redis-client-kit on PyPI">v0.1.2</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/redis-client-kit/">redis-client-kit<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Async and sync redis-py clients with cluster support, pooling, health checks and retries; Pydantic settings, Prometheus and Dishka as extras.</p>
          <div class="bdr-package__tags"><span>Python 3.10+</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/redis-client-kit/">Documentation <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/redis-client-kit">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add redis-client-kit</code><button type="button" data-copy-command="uv add redis-client-kit" aria-label="Copy install command for redis-client-kit" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-aiokafka-foundation-kit" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v14c0 1.7 3.1 3 7 3s7-1.3 7-3V5M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/></svg></span>
            <a class="bdr-package__version" data-pypi="aiokafka-foundation-kit" href="https://pypi.org/project/aiokafka-foundation-kit/" title="aiokafka-foundation-kit on PyPI">v0.1.1</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/aiokafka-foundation-kit/">aiokafka-foundation-kit<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Producer and consumer factories over aiokafka with Pydantic settings, retry policies, health checks, Prometheus metrics and OpenTelemetry.</p>
          <div class="bdr-package__tags"><span>Python 3.11+</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/aiokafka-foundation-kit/">Documentation <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/aiokafka-foundation-kit">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add aiokafka-foundation-kit</code><button type="button" data-copy-command="uv add aiokafka-foundation-kit" aria-label="Copy install command for aiokafka-foundation-kit" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
      </div>
    </section>
    <section class="bdr-lib-group" id="reliability" data-library-group data-layer="reliability" aria-labelledby="library-reliability-title">
      <div class="bdr-lib-group__heading"><div><span class="bdr-lib-group__number">03</span><h2 id="library-reliability-title">Reliability patterns</h2><span class="bdr-lib-group__count">3</span></div><p>Exactly-once effects and bounded latency.</p></div>
      <div class="bdr-lib-grid">
        <article class="bdr-package" id="package-omni-box" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m12 3 8 3v6c0 4-4 7-8 9-4-2-8-5-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/></svg></span>
            <a class="bdr-package__version" data-pypi="omni-box" href="https://pypi.org/project/omni-box/" title="omni-box on PyPI">v0.1.1</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/omni-box/">omni-box<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Transactional Outbox and Inbox: the event goes in the same transaction as the business row, out to Kafka from a background publisher, in with deduplication.</p>
          <div class="bdr-package__tags"><span>Python 3.12+</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/omni-box/">Documentation <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/omni-box">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add omni-box</code><button type="button" data-copy-command="uv add omni-box" aria-label="Copy install command for omni-box" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-idempotency-kit" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m12 3 8 3v6c0 4-4 7-8 9-4-2-8-5-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/></svg></span>
            <a class="bdr-package__version" data-pypi="idempotency-kit" href="https://pypi.org/project/idempotency-kit/" title="idempotency-kit on PyPI">v0.1.1</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/idempotency-kit/">idempotency-kit<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Execute an operation once per idempotency key: a coordinator and a decorator over Redis, collision handling, graceful degradation, metrics.</p>
          <div class="bdr-package__tags"><span>Python 3.11+</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/idempotency-kit/">Documentation <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/idempotency-kit">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add idempotency-kit</code><button type="button" data-copy-command="uv add idempotency-kit" aria-label="Copy install command for idempotency-kit" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-deadline-budget" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m12 3 8 3v6c0 4-4 7-8 9-4-2-8-5-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/></svg></span>
            <a class="bdr-package__version" data-pypi="deadline-budget" href="https://pypi.org/project/deadline-budget/" title="deadline-budget on PyPI">v0.1.2</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/deadline-budget/">deadline-budget<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">One request deadline budget with per-call caps and a safety margin — the budget that clientwright, grpc-client-kit and servicewright propagate across hops.</p>
          <div class="bdr-package__tags"><span>Python 3.10+</span><span>zero dependencies</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/deadline-budget/">Documentation <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/deadline-budget">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add deadline-budget</code><button type="button" data-copy-command="uv add deadline-budget" aria-label="Copy install command for deadline-budget" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
      </div>
    </section>
    <section class="bdr-lib-group" id="database" data-library-group data-layer="database" aria-labelledby="library-database-title">
      <div class="bdr-lib-group__heading"><div><span class="bdr-lib-group__number">04</span><h2 id="library-database-title">Database operations &amp; testing</h2><span class="bdr-lib-group__count">2</span></div><p>Partitions planned, migrations tested.</p></div>
      <div class="bdr-lib-grid">
        <article class="bdr-package" id="package-pg-partsmith" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M4 10h16m-9 0v10"/></svg></span>
            <a class="bdr-package__version" data-pypi="pg-partsmith" href="https://pypi.org/project/pg-partsmith/" title="pg-partsmith on PyPI">v1.5.0</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/pg-partsmith/">pg-partsmith<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">PostgreSQL partition lifecycle management with a plan you can read before it runs: RANGE, LIST and HASH nested to any depth — as a library, a CLI and a container image.</p>
          <div class="bdr-package__tags"><span>Python 3.11+</span><span>stable</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/pg-partsmith/">Documentation <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/pg-partsmith">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add pg-partsmith</code><button type="button" data-copy-command="uv add pg-partsmith" aria-label="Copy install command for pg-partsmith" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-alembic-gauntlet" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M4 10h16m-9 0v10"/></svg></span>
            <a class="bdr-package__version" data-pypi="alembic-gauntlet" href="https://pypi.org/project/alembic-gauntlet/" title="alembic-gauntlet on PyPI">v0.2.1</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/alembic-gauntlet/">alembic-gauntlet<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">A pytest plugin that runs Alembic migrations through the gauntlet: stairway up and down, models drift, single head, full downgrade, naming conventions.</p>
          <div class="bdr-package__tags"><span>Python 3.10+</span><span>pytest plugin</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/alembic-gauntlet/">Documentation <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/alembic-gauntlet">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add alembic-gauntlet</code><button type="button" data-copy-command="uv add alembic-gauntlet" aria-label="Copy install command for alembic-gauntlet" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
      </div>
    </section>
    <section class="bdr-lib-group" id="template" data-library-group data-layer="template" aria-labelledby="library-template-title">
      <div class="bdr-lib-group__heading"><div><span class="bdr-lib-group__number">05</span><h2 id="library-template-title">Start your own</h2><span class="bdr-lib-group__count">1</span></div><p>Every library above began here.</p></div>
      <div class="bdr-lib-grid">
        <article class="bdr-package" id="package-python-library-template" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m8 6-6 6 6 6m8-12 6 6-6 6m-3-14-2 16"/></svg></span>
            <span class="bdr-package__kind">PROJECT TEMPLATE</span>
          </div>
          <h3><a href="https://github.com/bedrock-python/python-library-template">python-library-template<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">The Copier template: uv, hatchling, ruff, mypy, pytest with unit and integration lanes, Zensical docs, Release Please with PyPI trusted publishing, and the org repo-settings script.</p>
          <div class="bdr-package__tags"><span>Copier template</span></div>
          <div class="bdr-package__links"><a href="https://github.com/bedrock-python/python-library-template">Use the template <span aria-hidden="true">↗</span></a>
          </div>
        </article>
      </div>
    </section>
    <section class="bdr-lib-group" id="recommended" data-library-group data-layer="recommended" aria-labelledby="library-recommended-title">
      <div class="bdr-lib-group__heading"><div><span class="bdr-lib-group__number">06</span><h2 id="library-recommended-title">Recommended</h2><span class="bdr-lib-group__count">2</span></div><p>Not ours. Libraries built with the same care.</p></div>
      <div class="bdr-lib-grid">
        <article class="bdr-package" id="package-aiofence" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m12 3 2.8 5.7L21 9.6l-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z"/></svg></span>
            <a class="bdr-package__version" data-pypi="aiofence" href="https://pypi.org/project/aiofence/" title="aiofence on PyPI">v0.4.0</a>
          </div>
          <h3><a href="https://github.com/stanislaushimovolos/aiofence">aiofence<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Multi-reason cancellation for asyncio in the spirit of Go's <code>context.Context</code>: declare timeout, client disconnect and shutdown once at the boundary, carry them in a <code>ContextVar</code>, wrap only the work you want cancelled in a <code>Fence</code>, and ask afterwards which reason fired.</p>
          <div class="bdr-package__tags"><span>Python 3.12+</span><span>by Stanislav Shimovolos</span></div>
          <div class="bdr-package__links"><a href="https://github.com/stanislaushimovolos/aiofence">Explore project <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/stanislaushimovolos/aiofence">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add aiofence</code><button type="button" data-copy-command="uv add aiofence" aria-label="Copy install command for aiofence" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-d9d" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m12 3 2.8 5.7L21 9.6l-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z"/></svg></span>
            <a class="bdr-package__version" data-pypi="d9d" href="https://pypi.org/project/d9d/" title="d9d on PyPI">v0.19.0</a>
          </div>
          <h3><a href="https://d9d-project.github.io/d9d/">d9d<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">A distributed training framework on PyTorch 2 that stays hackable: composable parallelism strategies instead of one god class, plain <code>nn.Module</code>s, <code>DTensor</code> for every distributed parameter, checkpoints as a graph — from single-GPU debugging to 6D-parallel clusters.</p>
          <div class="bdr-package__tags"><span>Python 3.11+</span><span>Apache-2.0</span></div>
          <div class="bdr-package__links"><a href="https://d9d-project.github.io/d9d/">Explore project <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/d9d-project/d9d">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add d9d</code><button type="button" data-copy-command="uv add d9d" aria-label="Copy install command for d9d" title="Copy install command" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
      </div>
    </section>
    <div class="bdr-lib-empty" data-library-empty hidden><h3>No packages found.</h3><p>Try a broader term such as “Kafka”, “client”, or “migrations”.</p><button type="button" data-library-reset>Clear search</button></div>
  </section>
  <p class="bdr-lib-footnote">Version badges link to PyPI and refresh when the page loads.</p>
  <div class="bdr-lib-sr-only" data-library-copy-status role="status" aria-live="polite"></div>
</div>
