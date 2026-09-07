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
  <a class="bdr-card" data-bdr-cat="tutorials" href="posts/2026-09-07-how-to-partition-an-existing-postgresql-table/">
    <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
    <div class="bdr-card__eyebrow">Tutorials</div>
    <h3 class="bdr-card__title">How to partition an existing PostgreSQL table</h3>
    <p class="bdr-card__lede">
      Two million rows turned into twelve monthly partitions while a writer inserted the whole
      time. Every step measured: the key change that blocks writers for 413 ms and the one that
      blocks them for 3, a 14-second drain with the writer's median insert at 0.8 ms, and the
      sequence that refuses to let the old table go.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tutorials" href="posts/2026-09-07-publishing-to-pypi-without-api-tokens/">
    <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
    <div class="bdr-card__eyebrow">Tutorials</div>
    <h3 class="bdr-card__title">Publishing to PyPI without API tokens</h3>
    <p class="bdr-card__lede">
      A PyPI token in a repository secret is a password with no expiry and no audit trail.
      Trusted Publishing replaces it with an identity: repository, workflow and environment,
      checked by PyPI on every upload. The whole pipeline from a merged pull request to a
      wheel, as it ran for six libraries today, including the escape hatch.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-should-your-application-create-kafka-topics-on-startup/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Should your application create Kafka topics on startup?</h3>
    <p class="bdr-card__lede">
      A producer wrote to a topic name with a typo in it and got no error: the broker created
      it, with one partition, and every message went there while the real consumer sat idle.
      What the broker, the application and a person each get wrong, and why a declared partition
      count is documentation after the first deploy.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-uuidv7-as-a-postgresql-partition-key/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">UUIDv7 as a PostgreSQL partition key</h3>
    <p class="bdr-card__lede">
      Range-partitioning by time normally costs you the primary key: every unique constraint
      has to contain the partition column. A time-ordered id removes the problem instead.
      Measured: single-column primary key accepted, one partition scanned for an id range,
      four for the same range on a timestamp column, and three kinds of id that do not fit.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-why-grpc-interceptors-break-on-streaming-rpcs/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Why gRPC interceptors break on streaming RPCs</h3>
    <p class="bdr-card__lede">
      An interceptor that works for unary calls reports 0 ms for a 609 ms stream, counts no
      errors while the stream fails, and loses its request id before the first item arrives.
      One object inheriting all four gRPC interceptor base classes is registered for one kind
      of call, silently. What the four kinds actually require.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-warmup-readiness-and-liveness-are-three-different-things/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Warmup, readiness and liveness are three different things</h3>
    <p class="bdr-card__lede">
      One service, two probes and a route polled every 100 ms through a warmup, a dependency
      outage and a SIGTERM. Nothing answered for the first 3.3 seconds, readiness went false
      while liveness stayed true and the route kept serving, and requests kept succeeding for
      two seconds after readiness went false. Each conflation has its own outage.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-partition-retention-is-not-drop-table/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Partition retention is not DROP TABLE</h3>
    <p class="bdr-card__lede">
      A retention job given a table with fifteen partitions dropped one it did not create,
      and, talking its way past a refusal with CASCADE, removed all seventeen foreign keys from
      a table it was never asked to touch. What retention looks like when ownership, a plan, a
      grace period and an archive hook come first.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tutorials" href="posts/2026-09-07-the-production-checklist-for-aiokafka/">
    <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
    <div class="bdr-card__eyebrow">Tutorials</div>
    <h3 class="bdr-card__title">The production checklist for aiokafka</h3>
    <p class="bdr-card__lede">
      Ten items, each measured against a Kafka container: what the client refuses to be built
      with, what a JSON deserializer does to one bad message, what auto-commit commits (seven
      messages nobody processed), and what happens to a member whose batch outlives the poll
      interval (four messages handled twice, by two processes).
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tutorials" href="posts/2026-09-07-what-to-monitor-in-a-sqlalchemy-connection-pool/">
    <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
    <div class="bdr-card__eyebrow">Tutorials</div>
    <h3 class="bdr-card__title">What to monitor in a SQLAlchemy connection pool</h3>
    <p class="bdr-card__lede">
      Eight workers, a pool of four, and a database that got twenty times slower halfway
      through. Connections in use read 4/4 before the incident and 4/4 after it. The wait in
      front of the pool, the held time behind it and the timeout counter are where the whole
      story was, and they say different things.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-what-happens-when-kafka-is-down-for-an-hour/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">What happens when Kafka is down for an hour?</h3>
    <p class="bdr-card__lede">
      A paused broker, twenty events and two designs. The request path was told three times
      that a send had failed, and one of those three was delivered anyway. The outbox kept its
      rows pending, spent no retries, and drained the whole backlog in one cycle when the
      broker came back.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-redis-health-checks-ping-is-not-the-whole-story/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Redis health checks: PING is not the whole story</h3>
    <p class="bdr-card__lede">
      Three Redis servers answered PONG: a healthy one, one full at its memory limit with
      eviction off, and a read-only replica. Two of them fail every SET the application makes,
      and readiness stayed green for all three. What a readiness check owes the caller, and
      what a write probe costs.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-your-models-and-your-schema-have-drifted/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Your models and your schema have drifted. Would CI notice?</h3>
    <p class="bdr-card__lede">
      Six kinds of schema drift, each one revision away from a clean history, against three
      suites. The pipeline everybody runs, alembic upgrade head, caught none of them.
      Autogenerate caught three. A check constraint, an enum member and a server default need
      checks Alembic does not perform at all.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-stop-passing-asyncsession-everywhere/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Stop passing AsyncSession everywhere</h3>
    <p class="bdr-card__lede">
      The most-repeated parameter in an async SQLAlchemy codebase is not a parameter: it is a
      pooled connection, a transaction and an identity map with no owner. Measured: an order
      committed with no outbox row, five of six requests failing on a pool of two because each
      held two connections, and an INSERT that vanished inside a read block.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tutorials" href="posts/2026-09-07-the-anatomy-of-a-production-grpc-server/">
    <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
    <div class="bdr-card__eyebrow">Tutorials</div>
    <h3 class="bdr-card__title">The anatomy of a production Python gRPC server</h3>
    <p class="bdr-card__lede">
      A six-line grpc.aio server handed the caller the database password in a status message,
      answered UNIMPLEMENTED when Kubernetes asked whether it was serving, and cancelled a
      request mid-flight on every deploy. Each part of the production server, the incident it
      prevents, and the status code a client actually gets with it and without it.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tutorials" href="posts/2026-09-07-graceful-kafka-consumer-shutdown/">
    <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
    <div class="bdr-card__eyebrow">Tutorials</div>
    <h3 class="bdr-card__title">Graceful Kafka consumer shutdown in Kubernetes</h3>
    <p class="bdr-card__lede">
      Every rollout sends the consumer SIGTERM mid-batch. Measured: a loop that exits on the
      signal left three messages to be processed twice and made its replacement wait 29.6 s
      for a rebalance; the same loop under a lifecycle finished the batch, committed, left the
      group, exited in 0.45 s, and the replacement was working in 0.31 s with no duplicates.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tutorials" href="posts/2026-09-07-idempotency-for-jobs-and-consumers/">
    <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
    <div class="bdr-card__eyebrow">Tutorials</div>
    <h3 class="bdr-card__title">Idempotency for background jobs and Kafka consumers</h3>
    <p class="bdr-card__lede">
      Queues deliver at least once by design, and every worker meets the crash before the ack,
      the visibility timeout that hands one job to two workers, and the rebalance that
      replays a batch. Measured against Redis: two mails and one, both workers waiting on one
      reservation, the key that named the delivery instead of the effect, and where the inbox
      stops and the key begins.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-when-should-redis-fail-open/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">When should Redis fail open?</h3>
    <p class="bdr-card__lede">
      Redis is gone and it is your cache, your rate limiter and your idempotency store. The
      decision is per use, not per client, and what the client owes every use is finding out
      fast. Measured against a paused Redis: twenty seconds for a default redis-py client,
      half a second with timeouts and zero retries, and what each use should do with that
      half second.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tutorials" href="posts/2026-09-07-testing-migrations-with-testcontainers/">
    <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
    <div class="bdr-card__eyebrow">Tutorials</div>
    <h3 class="bdr-card__title">Testing database migrations with Testcontainers: up, down and up again</h3>
    <p class="bdr-card__lede">
      From an empty tests directory to a green CI job that walks every Alembic revision forward,
      back and forward again against a real PostgreSQL: the session-scoped container, the two
      pytest settings that are not optional, the fifteen-line env.py contract with SET LOCAL,
      the test file, the workflow, and what it costs.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="tools" href="posts/2026-09-07-ai-code-review-should-not-be-fully-autonomous/">
    <div class="bdr-card__visual bdr-card__visual--tools"></div>
    <div class="bdr-card__eyebrow">Tools</div>
    <h3 class="bdr-card__title">AI code review should not be fully autonomous</h3>
    <p class="bdr-card__lede">
      A bot that posts twelve comments on every merge request trains the team to skip all
      twelve within a week. The alternative is a pipeline where the model drafts and a person
      decides: brief, dispatch, polish, post, with nothing reaching the merge request that a
      human did not read first. Why the polish stage is the design, not a safety valve.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-why-application-lifecycle-should-not-belong-to-fastapi/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Why application lifecycle should not belong to FastAPI</h3>
    <p class="bdr-card__lede">
      FastAPI's lifespan is a good API and the wrong owner. The pool, the warmup and the health
      checks live there until the service needs a worker, which has no lifespan and rewrites
      the plumbing by hand, without readiness or a drain window. The two files it produces,
      and the dictionary they should have been.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

  <a class="bdr-card" data-bdr-cat="design" href="posts/2026-09-07-transactional-inbox/">
    <div class="bdr-card__visual bdr-card__visual--design"></div>
    <div class="bdr-card__eyebrow">Design</div>
    <h3 class="bdr-card__title">Transactional inbox: the other half of the outbox pattern</h3>
    <p class="bdr-card__lede">
      A broker delivers at least once, and a handler can fail halfway. An inbox row per message,
      in the same transaction as the effect, answers both. Measured: a duplicate delivery
      that ran no handler, and a handler that fails after its write under four ack
      strategies, two of which lose the message and two of which end with exactly one
      invoice.
    </p>
    <div class="bdr-card__meta">September 7, 2026</div>
  </a>

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
