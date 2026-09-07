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
    <div class="bdr-featured__eyebrow">Featured · Libraries</div>
    <h2 class="bdr-featured__title">
      <a href="blog/posts/2026-09-06-pg-partsmith/">Managing PostgreSQL partitions, one failure at a time</a>
    </h2>
    <p class="bdr-featured__lede">
      Two ways a partitioned table gets you out of bed, and the library that grew out of
      them: a plan you can read before it runs, ownership that never drops a table it did
      not make, the same API async and sync, a command line and a container image for
      teams with no Python, hooks from a YAML document, and one page for the AI assistant
      doing the wiring.
    </p>
    <div class="bdr-featured__meta">
      <span>September 6, 2026</span>
      <span>·</span>
      <span>Libraries · Tools</span>
    </div>
  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Latest from the blog</h2>
    <a class="bdr-section-head__link" href="blog/">See all posts →</a>
  </div>

  <div class="bdr-grid">
    <a class="bdr-card" href="blog/posts/2026-09-07-mapping-python-exceptions-to-grpc-status-codes/">
      <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
      <div class="bdr-card__eyebrow">Tutorials</div>
      <h3 class="bdr-card__title">Mapping Python exceptions to gRPC status codes</h3>
      <p class="bdr-card__lede">
        Eleven exceptions through four configurations of one gRPC server. With no map
        every failure is UNKNOWN and two of them put a database password in the status details.
      </p>
      <div class="bdr-card__meta">September 7, 2026</div>
    </a>

    <a class="bdr-card" href="blog/posts/2026-09-07-transport-independent-errors/">
      <div class="bdr-card__visual bdr-card__visual--design"></div>
      <div class="bdr-card__eyebrow">Design</div>
      <h3 class="bdr-card__title">Transport-independent errors: one domain error, two protocols</h3>
      <p class="bdr-card__lede">
        A service that speaks HTTP outward and gRPC inward has two answers for every
        failure. Seven calls through both transports: the same domain error, the same code, and
        the undeclared exception masked identically.
      </p>
      <div class="bdr-card__meta">September 7, 2026</div>
    </a>

    <a class="bdr-card" href="blog/posts/2026-09-07-idempotency-across-a-chain-of-microservices/">
      <div class="bdr-card__visual bdr-card__visual--design"></div>
      <div class="bdr-card__eyebrow">Design</div>
      <h3 class="bdr-card__title">Idempotency across a chain of microservices</h3>
      <p class="bdr-card__lede">
        A gateway calling orders calling payments, each with one retry. Without a key
        that travels, one user action produced four charges; with a key minted per attempt,
        two; with one key per intent, one.
      </p>
      <div class="bdr-card__meta">September 7, 2026</div>
    </a>
























  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Libraries</h2>
    <a class="bdr-section-head__link" href="libraries/">All libraries →</a>
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

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Tools</h2>
    <a class="bdr-section-head__link" href="tools/">All tools →</a>
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
