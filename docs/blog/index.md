---
title: Blog
description: Guides, design notes and plain engineering articles from the Bedrock Python ecosystem.
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
    Guides, design notes and plain engineering articles from the libraries and tools
    that power our backend services — the infrastructure layer, in writing.
  </p>
</section>

<nav class="bdr-chips" data-bdr-chips markdown="0">
  <a class="bdr-chip is-active" data-bdr-filter="all" href="#">All</a>
  <a class="bdr-chip" data-bdr-filter="libraries" href="category/libraries/">Libraries</a>
  <a class="bdr-chip" data-bdr-filter="tools" href="category/tools/">Tools</a>
  <a class="bdr-chip" data-bdr-filter="design" href="category/design/">Design</a>
  <a class="bdr-chip" data-bdr-filter="tutorials" href="category/tutorials/">Tutorials</a>
  <a class="bdr-chip" data-bdr-filter="meta" href="category/meta/">Meta</a>
  <a class="bdr-chip" data-bdr-filter="archive" href="archive/">Archive</a>
</nav>

<div class="bdr-grid" data-bdr-grid markdown="0">
  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-grpc-channels-pooled-by-identity/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">gRPC channels should not be pooled by address alone</h3>
    <p class="bdr-card__lede">
      grpc.aio bakes credentials, options, compression and the interceptor chain into a
      channel at creation, so a pool keyed by host:port hands one caller another caller's
      configuration. Measured: an audit client with no retry policy that retried three times,
      a chain rebuilt per request minting a channel per call, and keepalive as part of the
      identity.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tutorials" href="posts/2026-09-07-retry-after-backoff-and-jitter/">
    <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
    <div class="bdr-card__eyebrow">Tutorials</div>
    <h3 class="bdr-card__title">Retry-After, backoff and jitter: what a production HTTP client actually does</h3>
    <p class="bdr-card__lede">
      The four-line retry loop makes eight decisions wrong. Measured: a Retry-After honoured
      and ignored, fifty callers whose fixed backoff put 49 retries in one ten-millisecond
      window, a timed-out POST received once by default and three times when declared
      idempotent, and which of six answers a client should retry at all.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tutorials" href="posts/2026-09-07-unit-of-work-in-sqlalchemy-2/">
    <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
    <div class="bdr-card__eyebrow">Tutorials</div>
    <h3 class="bdr-card__title">The Unit of Work pattern in SQLAlchemy 2</h3>
    <p class="bdr-card__lede">
      Every first repository has a commit in it, and a use case that touches two of them can
      leave half of itself in the database. Measured: users=1 orders=0 with self-committing
      repositories, users=0 orders=0 with a unit of work, a read-only block that discards a
      write, a savepoint that keeps one failed step from poisoning the transaction, and the
      use case under test with a list instead of PostgreSQL.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-circuit-breakers-should-be-per-origin/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Circuit breakers should be per origin, not per client</h3>
    <p class="bdr-card__lede">
      One client, three upstreams, one of them down: a breaker keyed on the client refused
      half the requests to the two that were fine. Measured: the origin as the key, which
      responses should trip a breaker and which should not, attempts against logical calls
      under retries, and the single probe after the recovery timeout.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-exactly-once-effects/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Exactly-once is a lie; exactly-once effects are not</h3>
    <p class="bdr-card__lede">
      Kafka cannot make your database update exactly once. Measured against PostgreSQL and
      Kafka: the two dual-write windows, an outbox relay that crashes after the send and
      publishes twice, and an inbox that receives both copies and writes the invoice once.
      At-least-once delivery plus one unique key per boundary is the only exactly-once there
      is, and it is the one you wanted.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="libraries" href="posts/2026-09-07-one-lifecycle-for-http-grpc-workers-and-cron/">
    <div class="bdr-card__visual bdr-card__visual--libraries"></div>
    <div class="bdr-card__eyebrow">Libraries</div>
    <h3 class="bdr-card__title">One lifecycle for HTTP, gRPC, workers and cron jobs</h3>
    <p class="bdr-card__lede">
      An API, a scheduler and a worker are one application with three ways for work to
      enter, and most codebases give each its own startup, readiness and shutdown. One
      AppSpec run as one process and as two, every lifecycle call printed: bind in order,
      readiness after the last bind, drain in reverse, the pool closed last, exit 0, and
      the split into two deployments costing one dictionary.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-retries-can-make-an-outage-worse/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Retries can make an outage worse: designing a retry budget</h3>
    <p class="bdr-card__lede">
      Three attempts at every hop of a four-layer chain is 81 requests at the bottom for one
      at the top, measured: 810 for ten callers against a dead origin. A per-origin retry
      budget bounds the storm from the first request, a circuit breaker stops it once the
      dependency has proven it is down, and the one case where the budget makes every caller
      fail is the case where it should.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-idempotency-keys-the-part-everyone-gets-wrong/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Idempotency keys: the part everyone gets wrong</h3>
    <p class="bdr-card__lede">
      A result cache looks like an idempotency key until a client retries while the first
      request is still running. Measured against a provider that counts its charges: the
      cache charged twice with identical responses, a reservation charged once, a reused key
      with a different amount was refused, a failed action was not cached, and a missing store
      failed open. What the key promises, and why it is still not a lock.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tutorials" href="posts/2026-09-07-pgbouncer-transaction-mode-async-sqlalchemy/">
    <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
    <div class="bdr-card__eyebrow">Tutorials</div>
    <h3 class="bdr-card__title">PgBouncer transaction mode and async SQLAlchemy: the production setup nobody documents enough</h3>
    <p class="bdr-card__lede">
      Transaction pooling takes the session away, and everything that lived on it goes with
      it. Measured on PgBouncer 1.25: a bare SET leaking to the next client, the prepared
      statement error that stopped happening in 1.22, the one startup parameter that refuses
      every connection, and the configuration that survived the table.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="meta" href="posts/2026-09-07-what-every-microservice-reimplements/">
    <div class="bdr-card__visual bdr-card__visual--meta"></div>
    <div class="bdr-card__eyebrow">Meta</div>
    <h3 class="bdr-card__title">What every production Python microservice reimplements</h3>
    <p class="bdr-card__lede">
      Lifecycle, health, shutdown, retries, timeouts, deadlines, sessions, transactions,
      idempotency, outbox, metrics, tracing, migration tests: the same code in every service,
      none of it the product. Why a framework is the wrong shape for it, and a hundred-line
      service with four independent libraries, run against a real PostgreSQL from readiness
      to exit 0.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="meta" href="posts/2026-09-07-twelve-libraries-one-standard/">
    <div class="bdr-card__visual bdr-card__visual--meta"></div>
    <div class="bdr-card__eyebrow">Meta</div>
    <h3 class="bdr-card__title">Twelve libraries, one engineering standard, no monorepo</h3>
    <p class="bdr-card__lede">
      Sixteen repositories that agree on tooling, CI, releases, security settings and docs, without
      a monorepo. A Copier template that renders a green library in five seconds, a script that
      makes a GitHub repository match, Release Please with Trusted Publishing, and the three
      lessons the standard now carries so nobody learns them twice.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-why-i-stopped-wrapping-http-clients/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Why I stopped wrapping HTTP clients</h3>
    <p class="bdr-card__lede">
      Every company writes an HTTP client wrapper: a retry helper that grows a config class
      and ends as a dialect nobody can migrate away from. What the wrapper owns is not HTTP,
      and what it takes is the client. Measured: the native type kept on three libraries,
      one policy driving two of them with the same metrics, nine requests from two stacked
      retry loops, and a build that fails when an adapter cannot honour a setting.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-safe-grpc-retries/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Safe gRPC retries: which status codes you should actually retry</h3>
    <p class="bdr-card__lede">
      A retry is a bet that the server did not do the work. Measured against a payments
      server that counts its charges: retrying INTERNAL charged the card three times, so did
      UNAVAILABLE in one of the two ways a server produces it, the deadline did not triple
      across attempts, the breaker counted attempts, and a retried stream replayed what the
      consumer had already seen. The table of codes, and the three settings that make a
      policy honest.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-graceful-shutdown-is-a-protocol/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Graceful shutdown in Kubernetes is a protocol, not a signal handler</h3>
    <p class="bdr-card__lede">
      SIGTERM, finish in-flight requests, exit: that is what every framework calls graceful,
      and it refused 44 of 47 requests in the second after the signal, because Kubernetes
      keeps routing while the endpoint removal propagates. The four steps a pod has to
      follow, the one everybody skips, measured before and after, and the arithmetic for
      terminationGracePeriodSeconds.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="meta" href="posts/2026-09-07-documentation-for-ai-coding-agents/">
    <div class="bdr-card__visual bdr-card__visual--meta"></div>
    <div class="bdr-card__eyebrow">Meta</div>
    <h3 class="bdr-card__title">We started writing documentation for AI coding agents</h3>
    <p class="bdr-card__lede">
      A coding assistant invented a class, awaited a sync function and passed a session
      where the library wants an engine, all with complete confidence. The docs were not
      wrong; they were written for a reader who browses. One page per library, written
      for a model: the invariants as numbered rules, WRONG next to RIGHT, every page also
      served as Markdown, and what keeping fourteen of them true costs.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tutorials" href="posts/2026-09-07-five-alembic-migration-tests/">
    <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
    <div class="bdr-card__eyebrow">Tutorials</div>
    <h3 class="bdr-card__title">The five migration tests every Python project should run in CI</h3>
    <p class="bdr-card__lede">
      Four Alembic revisions, five bugs I have shipped, three test suites. The one most
      pipelines have, a plain upgrade to head, caught one bug in five. Five short checks
      written against Alembic's own API caught all of them, each for its own reason, with
      the messages you would otherwise read during an incident.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-06-timeouts-are-not-deadlines/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Timeouts are not deadlines: how latency budgets break across microservices</h3>
    <p class="bdr-card__lede">
        A timeout measures patience; a deadline is a point on the clock. Measured three times: an
        httpx call that took four seconds under a one-second timeout, a retry loop that tripled
        it, and a chain of three gRPC services where the card was charged a second after the
        customer saw the error. Then the arithmetic that fixes it, and the three places it has
        to live.
    </p>
    <div class="bdr-card__meta">September 6, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="libraries tools" href="posts/2026-09-06-pg-partsmith/">
    <div class="bdr-card__visual bdr-card__visual--libraries"></div>
    <div class="bdr-card__eyebrow">Libraries · Tools</div>
    <h3 class="bdr-card__title">Managing PostgreSQL partitions, one failure at a time</h3>
    <p class="bdr-card__lede">
      The pain of keeping a partitioned table right every night, and how pg-partsmith
      answers it: a plan you can read before it runs, ownership that never drops a table
      it did not make, the same API async and sync, a command line and a container image
      for teams with no Python, hooks from a YAML document, and one page written for the
      AI assistant doing the wiring.
    </p>
    <div class="bdr-card__meta">September 6, 2026</div>
  </a>

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

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Recommended reading</h2>
    <span class="bdr-section-head__note">Written elsewhere, by other people. Worth your time.</span>
  </div>

  <div class="bdr-grid">
    <a class="bdr-card" href="https://medium.com/@shimovolos.stas/your-llm-is-streaming-to-nobody-how-to-handle-client-disconnects-in-fastapi-8cdf8c5d519e">
      <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
      <div class="bdr-card__eyebrow">Medium · Stanislav Shimovolos</div>
      <h3 class="bdr-card__title">Your LLM Is Streaming to Nobody: How to Handle Client Disconnects in FastAPI</h3>
      <p class="bdr-card__lede">
        The client closes the tab and your endpoint keeps going: the GPU generates tokens
        nobody reads, the transaction never commits, the pool gets a broken connection back.
        The full path of a disconnect from TCP through ASGI to asyncio, and working code for
        both streaming and plain endpoints on FastAPI and uvicorn.
      </p>
      <div class="bdr-card__meta">January 19, 2026 · ~30 min read</div>
    </a>
  </div>
</section>
