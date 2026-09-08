---
title: Blog
description: Practical field notes on production Python. Find articles on PostgreSQL, gRPC, Kafka, service lifecycle, and resilient systems.
hide:
  - navigation
  - toc
---

<div class="bdr-explorer" data-blog-explorer data-catalog-url="catalog.json" data-view="list" markdown="0">
  <header class="bdr-journal">
    <div>
      <div class="bdr-journal__eyebrow"><span></span> THE BEDROCK BLOG</div>
      <h1>Engineering beyond<br>the <em>happy path.</em></h1>
      <p>Field notes on building Python systems that hold up in production.<br class="bdr-desktop-break"> The decisions, the trade-offs, and the code behind them.</p>
    </div>
    <div class="bdr-journal__aside" aria-hidden="true">
      <svg viewBox="0 0 130 100" fill="none"><path d="M65 8 112 33 65 58 18 33 65 8Z"/><path d="m18 48 47 25 47-25M18 63l47 25 47-25"/><path d="M65 58v30M18 33v30M112 33v30"/><path class="bdr-journal__accent" d="m65 8 47 25-47 25-47-25L65 8Z"/></svg>
      <span>FROM THE<br>INFRASTRUCTURE LAYER</span>
    </div>
  </header>

  <div class="bdr-discovery" data-blog-controls hidden>
    <div class="bdr-searchbox" role="search" aria-label="Search blog articles">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/></svg>
      <label class="bdr-sr-only" for="blog-query">Search articles by title, topic, or library</label>
      <input id="blog-query" data-blog-query type="search" placeholder="Find an article, a topic, a library…" autocomplete="off" spellcheck="false" enterkeyhint="search" aria-controls="blog-results">
      <button class="bdr-searchbox__clear" data-blog-clear-query type="button" aria-label="Clear search" hidden>×</button>
      <kbd aria-hidden="true">/</kbd>
    </div>
    <span class="bdr-discovery__hint">A specific problem in mind? Start here.</span>
  </div>
  <p class="bdr-load-status" data-blog-load-status role="status">Explore all articles below. <a href="archive/">Browse the archive →</a></p>

  <section class="bdr-collections" aria-labelledby="collections-title">
    <div class="bdr-collections__heading"><h2 id="collections-title">A few good places to start</h2><span>Follow your curiosity</span></div>
    <div class="bdr-collections__grid">
      <a class="bdr-collection bdr-collection--resilience" data-blog-collection="reliability" href="posts/2026-09-07-reliability-is-not-retry-3/">
        <div class="bdr-collection__icon" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><rect x="4" y="16" width="12" height="16" rx="3"/><rect x="32" y="16" width="12" height="16" rx="3"/><path d="M16 24h16m-11-5 5 5-5 5M10 10V6m28 36v-4"/></svg></div>
        <div><span class="bdr-collection__label">WHEN DEPENDENCIES FAIL</span><h3>Build resilient services</h3><p>Deadlines, retries & circuit breakers</p></div><span class="bdr-collection__arrow" aria-hidden="true">↗</span>
      </a>
      <a class="bdr-collection bdr-collection--postgres" data-blog-collection="postgres" href="posts/2026-09-06-pg-partsmith/">
        <div class="bdr-collection__icon" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><ellipse cx="24" cy="11" rx="15" ry="6"/><path d="M9 11v25c0 3.3 6.7 6 15 6s15-2.7 15-6V11M9 23c0 3.3 6.7 6 15 6s15-2.7 15-6M9 35c0 3.3 6.7 6 15 6s15-2.7 15-6"/></svg></div>
        <div><span class="bdr-collection__label">BEYOND THE QUERY</span><h3>Postgres in production</h3><p>Partitions, sessions & migrations</p></div><span class="bdr-collection__arrow" aria-hidden="true">↗</span>
      </a>
      <a class="bdr-collection bdr-collection--messaging" data-blog-collection="messaging" href="posts/2026-05-15-transactional-outbox-with-omni-box/">
        <div class="bdr-collection__icon" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><rect x="3" y="18" width="10" height="12" rx="2"/><rect x="35" y="18" width="10" height="12" rx="2"/><rect x="19" y="6" width="10" height="12" rx="2"/><rect x="19" y="30" width="10" height="12" rx="2"/><path d="m13 24 6-12m10 0 6 12m-22 0 6 12m10 0 6-12"/></svg></div>
        <div><span class="bdr-collection__label">MAKE EVERY EVENT COUNT</span><h3>Deliver messages reliably</h3><p>Kafka, outbox & exactly-once effects</p></div><span class="bdr-collection__arrow" aria-hidden="true">↗</span>
      </a>
    </div>
  </section>

  <div class="bdr-explorer__layout">
    <aside class="bdr-explorer__sidebar" data-blog-controls hidden>
      <details class="bdr-topics" data-blog-topics-panel open>
        <summary>Explore by topic <svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="m5 7 5 5 5-5"/></svg></summary>
        <nav aria-label="Article topics" class="bdr-topics__nav">
          <button data-blog-topic="all" type="button" aria-pressed="true"><span class="bdr-topic-symbol" aria-hidden="true">✳</span><span>All articles</span><span data-topic-count></span></button>
          <button data-blog-topic="postgres" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">▤</span><span>PostgreSQL & SQLAlchemy</span><span data-topic-count></span></button>
          <button data-blog-topic="reliability" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">↻</span><span>HTTP & resilience</span><span data-topic-count></span></button>
          <button data-blog-topic="grpc" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">⇄</span><span>gRPC</span><span data-topic-count></span></button>
          <button data-blog-topic="messaging" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">⇢</span><span>Kafka & messaging</span><span data-topic-count></span></button>
          <button data-blog-topic="lifecycle" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">◷</span><span>Service lifecycle</span><span data-topic-count></span></button>
          <button data-blog-topic="redis" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">◇</span><span>Redis & idempotency</span><span data-topic-count></span></button>
          <button data-blog-topic="engineering" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">⌘</span><span>Python & tooling</span><span data-topic-count></span></button>
        </nav>
      </details>
      <div class="bdr-explorer__note"><span>BUILT IN THE OPEN</span><p>Real production problems.<br>Working code. Lessons shared.</p><a href="archive/">The complete archive <span aria-hidden="true">↗</span></a></div>
    </aside>

    <section class="bdr-explorer__main" aria-labelledby="blog-results-heading">
      <div class="bdr-results-heading" data-blog-results-heading>
        <div><h2 id="blog-results-heading" tabindex="-1">The articles</h2><span data-blog-count role="status" aria-live="polite" aria-atomic="true">Notes from the infrastructure layer</span></div>
        <div class="bdr-view-switch" role="group" aria-label="Article layout" data-blog-controls hidden>
          <button data-blog-view="list" type="button" aria-label="List view" title="List view" aria-pressed="true"><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M7 5h10M7 10h10M7 15h10M3 5h.5M3 10h.5M3 15h.5"/></svg></button>
          <button data-blog-view="grid" type="button" aria-label="Grid view" title="Grid view" aria-pressed="false"><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="3" y="3" width="5" height="5" rx=".5"/><rect x="12" y="3" width="5" height="5" rx=".5"/><rect x="3" y="12" width="5" height="5" rx=".5"/><rect x="12" y="12" width="5" height="5" rx=".5"/></svg></button>
        </div>
      </div>
      <div class="bdr-toolbar" data-blog-controls hidden>
        <div class="bdr-toolbar__filters">
          <label><span class="bdr-sr-only">Article format</span><select data-blog-format aria-controls="blog-results"><option value="all">All formats</option><option value="design">Design</option><option value="tutorials">Tutorials</option><option value="libraries">Libraries</option><option value="tools">Tools</option><option value="meta">Meta</option></select></label>
          <label><span class="bdr-sr-only">Reading time</span><select data-blog-duration aria-controls="blog-results"><option value="all">Any reading time</option><option value="short">8 min or less</option><option value="long">Over 8 min</option></select></label>
        </div>
        <label class="bdr-toolbar__sort"><span>Sort:</span><select data-blog-sort aria-label="Sort articles" aria-controls="blog-results"><option value="newest">Newest first</option><option value="oldest">Oldest first</option><option value="shortest">Shortest read</option><option value="title">Title A–Z</option></select></label>
      </div>
      <div class="bdr-active-filters" data-blog-active hidden></div>
      <div class="bdr-results" id="blog-results" data-blog-results>
<!-- catalog:articles:start -->
  <article class="bdr-entry" data-article-id="2026-09-07-ai-code-review-should-not-be-fully-autonomous">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-ai-code-review-should-not-be-fully-autonomous/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python &amp; tooling <span>·</span> Tools</div>
        <h3 class="bdr-entry__title">AI code review should not be fully autonomous</h3>
        <p class="bdr-entry__description">The obvious way to build an AI code reviewer is a webhook: a merge request opens, a model reads the diff, the comments appear.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-circuit-breakers-should-be-per-origin">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-circuit-breakers-should-be-per-origin/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP &amp; resilience <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Circuit breakers should be per origin, not per client</h3>
        <p class="bdr-entry__description">A circuit breaker is the simplest reliability pattern to explain and the easiest to key wrong.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>5 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-exactly-once-effects">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-exactly-once-effects/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka &amp; messaging <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Exactly-once is a lie; exactly-once effects are not</h3>
        <p class="bdr-entry__description">Kafka cannot make your database update exactly once. Nothing can, because the database and the broker are two systems with two commits and no transaction that spans them, and…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>7 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-graceful-kafka-consumer-shutdown">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-graceful-kafka-consumer-shutdown/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka &amp; messaging <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">Graceful Kafka consumer shutdown in Kubernetes</h3>
        <p class="bdr-entry__description">A Kafka consumer under Kubernetes is redeployed several times a day, and every redeploy sends it SIGTERM in the middle of a batch.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>5 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-graceful-shutdown-is-a-protocol">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-graceful-shutdown-is-a-protocol/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Service lifecycle <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Graceful shutdown in Kubernetes is a protocol, not a signal handler</h3>
        <p class="bdr-entry__description">Every web framework handles SIGTERM. It stops accepting connections, lets the requests already in flight finish, and exits cleanly.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>8 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-grpc-channels-pooled-by-identity">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-grpc-channels-pooled-by-identity/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Design</div>
        <h3 class="bdr-entry__title">gRPC channels should not be pooled by address alone</h3>
        <p class="bdr-entry__description">A gRPC channel is expensive to open and cheap to keep, so every service that talks to more than one gRPC backend grows a channel pool, and the first pool is always a dictionary…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>5 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-how-i-start-a-production-grade-python-library">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-how-i-start-a-production-grade-python-library/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python &amp; tooling <span>·</span> Meta</div>
        <h3 class="bdr-entry__title">How I start a production-grade Python library in 2026</h3>
        <p class="bdr-entry__description">Every library in this series started the same way: one command, forty-one files, and a green quality gate about three seconds later.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-how-to-partition-an-existing-postgresql-table">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-how-to-partition-an-existing-postgresql-table/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">How to partition an existing PostgreSQL table without rewriting your application</h3>
        <p class="bdr-entry__description">ALTER TABLE ... PARTITION BY does not exist. Turning a live table into a partitioned one means making a new parent, adopting the old table as its DEFAULT partition, and draining…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>8 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-idempotency-across-a-chain-of-microservices">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-idempotency-across-a-chain-of-microservices/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis &amp; idempotency <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Idempotency across a chain of microservices</h3>
        <p class="bdr-entry__description">One idempotency key in one service is a solved problem. A chain is not, because the retry that matters happens at the top and the effect that matters happens at the bottom, with…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-idempotency-for-jobs-and-consumers">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-idempotency-for-jobs-and-consumers/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis &amp; idempotency <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">Idempotency for background jobs and Kafka consumers</h3>
        <p class="bdr-entry__description">The Idempotency-Key header gets the attention because it has a name and a spec, but the same problem arrives at every worker that takes jobs from a queue, and it arrives more…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-idempotency-keys-the-part-everyone-gets-wrong">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-idempotency-keys-the-part-everyone-gets-wrong/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis &amp; idempotency <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Idempotency keys: the part everyone gets wrong</h3>
        <p class="bdr-entry__description">An Idempotency-Key header is the most widely copied idea in payment APIs, and the most widely misimplemented.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>8 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-mapping-python-exceptions-to-grpc-status-codes">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-mapping-python-exceptions-to-grpc-status-codes/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">Mapping Python exceptions to gRPC status codes without leaking internals</h3>
        <p class="bdr-entry__description">gRPC has sixteen status codes and your service has a hundred exception types, so somebody has to write the map.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-migrating-from-pg-partman">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-migrating-from-pg-partman/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">Migrating from pg_partman to application-managed partitions</h3>
        <p class="bdr-entry__description">pg_partman is the default answer for PostgreSQL partition maintenance, and it is a good one when you can install extensions and your team is comfortable operating inside the…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-one-lifecycle-for-http-grpc-workers-and-cron">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-one-lifecycle-for-http-grpc-workers-and-cron/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Service lifecycle <span>·</span> Libraries</div>
        <h3 class="bdr-entry__title">One lifecycle for HTTP, gRPC, workers and cron jobs</h3>
        <p class="bdr-entry__description">An HTTP API, a gRPC server, a Kafka consumer and a nightly job are one application with four ways for work to enter it.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>7 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-partition-retention-is-not-drop-table">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-partition-retention-is-not-drop-table/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Partition retention is not DROP TABLE</h3>
        <p class="bdr-entry__description">The retention job is the one line of the partitioning setup that nobody reviews. Find the partitions older than the window, drop them, run it nightly.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>7 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-pgbouncer-transaction-mode-async-sqlalchemy">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-pgbouncer-transaction-mode-async-sqlalchemy/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">PgBouncer transaction mode and async SQLAlchemy: the production setup nobody documents enough</h3>
        <p class="bdr-entry__description">Your SQLAlchemy configuration works perfectly against PostgreSQL, and then someone puts PgBouncer in front of the database in transaction mode, which is the only mode that solves…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>8 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-publishing-to-pypi-without-api-tokens">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-publishing-to-pypi-without-api-tokens/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python &amp; tooling <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">Publishing to PyPI without API tokens: Trusted Publishing end to end</h3>
        <p class="bdr-entry__description">A PyPI API token in a repository secret is a password with no expiry, no scope beyond the project it was minted for, and no way to tell who used it.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-redis-health-checks-ping-is-not-the-whole-story">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-redis-health-checks-ping-is-not-the-whole-story/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis &amp; idempotency <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Redis health checks: PING is not the whole story</h3>
        <p class="bdr-entry__description">A health check that answers True for a server that cannot take a write is worse than no health check, because something acts on it.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>5 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-reliability-is-not-retry-3">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-reliability-is-not-retry-3/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP &amp; resilience <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Reliability is not retry=3</h3>
        <p class="bdr-entry__description">retry=3 is the first thing anybody adds to an HTTP client and the last thing anybody revisits.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-retries-can-make-an-outage-worse">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-retries-can-make-an-outage-worse/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP &amp; resilience <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Retries can make an outage worse: designing a retry budget</h3>
        <p class="bdr-entry__description">Three retries at every hop of a five-service call is not resilience. It is a multiplier, and it multiplies hardest exactly when the bottom service is failing, which is the one…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>7 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-retry-after-backoff-and-jitter">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-retry-after-backoff-and-jitter/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP &amp; resilience <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">Retry-After, backoff and jitter: what a production HTTP client actually does</h3>
        <p class="bdr-entry__description">The retry loop every codebase has is four lines: try, catch, sleep, try again. A production HTTP client&#x27;s retry policy is a checklist of about eight decisions that the four lines…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>5 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-safe-grpc-retries">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-safe-grpc-retries/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Safe gRPC retries: which status codes you should actually retry</h3>
        <p class="bdr-entry__description">max_attempts=3 is the most common line in a gRPC client configuration and the least examined.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>7 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-should-your-application-create-kafka-topics-on-startup">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-should-your-application-create-kafka-topics-on-startup/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka &amp; messaging <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Should your application create Kafka topics on startup?</h3>
        <p class="bdr-entry__description">Somebody has to create the topic. The three candidates are the broker, doing it automatically the first time anyone mentions a name; the application, doing it at startup; and a…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-stop-passing-asyncsession-everywhere">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-stop-passing-asyncsession-everywhere/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Stop passing AsyncSession everywhere</h3>
        <p class="bdr-entry__description">Every async SQLAlchemy codebase I have worked on has the same signature, repeated at every level:</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>8 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-testing-migrations-with-testcontainers">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-testing-migrations-with-testcontainers/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">Testing database migrations with Testcontainers: up, down and up again</h3>
        <p class="bdr-entry__description">The five migration tests post made the case; this one is the setup, step by step, from an empty tests/ directory to a green job in CI that walks every revision forward, back and…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>4 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-the-anatomy-of-a-production-grpc-server">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-the-anatomy-of-a-production-grpc-server/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">The anatomy of a production Python gRPC server</h3>
        <p class="bdr-entry__description">A grpc.aio server is six lines. A grpc.aio server you can put behind a load balancer, roll out three times a day and hand to an on-call rota is a different object, and the…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>10 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-five-alembic-migration-tests">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-five-alembic-migration-tests/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">The five migration tests every Python project should run in CI</h3>
        <p class="bdr-entry__description">We test application code until the coverage badge is green, and then we deploy database migrations that have been run exactly once, on a laptop, in one direction.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>10 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-the-production-checklist-for-aiokafka">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-the-production-checklist-for-aiokafka/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka &amp; messaging <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">The production checklist for aiokafka</h3>
        <p class="bdr-entry__description">aiokafka is a good client with defaults chosen for a library, not for your service, and the gap between the two is where the incidents live.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>7 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-unit-of-work-in-sqlalchemy-2">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-unit-of-work-in-sqlalchemy-2/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">The Unit of Work pattern in SQLAlchemy 2</h3>
        <p class="bdr-entry__description">Every repository I have ever seen written for the first time has a commit() in it. It is there so that the id comes back, so that the next repository can use it, so that the test…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-transactional-inbox">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-transactional-inbox/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka &amp; messaging <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Transactional inbox: the other half of the outbox pattern</h3>
        <p class="bdr-entry__description">The outbox gets the attention because it solves the dramatic problem, the event that never left.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-transport-independent-errors">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-transport-independent-errors/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Service lifecycle <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Transport-independent errors: one domain error, HTTP and gRPC responses</h3>
        <p class="bdr-entry__description">A service that speaks HTTP to the outside and gRPC to its neighbours has two answers for every failure, and the two drift.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>5 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-twelve-libraries-one-standard">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-twelve-libraries-one-standard/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python &amp; tooling <span>·</span> Meta</div>
        <h3 class="bdr-entry__title">Twelve libraries, one engineering standard, no monorepo</h3>
        <p class="bdr-entry__description">Bedrock Python is sixteen repositories: twelve libraries, two tools, a template and this site.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>7 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-uuidv7-as-a-postgresql-partition-key">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-uuidv7-as-a-postgresql-partition-key/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Design</div>
        <h3 class="bdr-entry__title">UUIDv7 as a PostgreSQL partition key</h3>
        <p class="bdr-entry__description">Range-partitioning a table by time normally costs you the primary key: PostgreSQL requires every unique constraint to contain the partition column, so PRIMARY KEY (id) becomes…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-warmup-readiness-and-liveness-are-three-different-things">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-warmup-readiness-and-liveness-are-three-different-things/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Service lifecycle <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Warmup, readiness and liveness are three different things</h3>
        <p class="bdr-entry__description">Most services answer all three questions with one handler, usually one that pings the database. Each conflation has its own outage.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>7 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-documentation-for-ai-coding-agents">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-documentation-for-ai-coding-agents/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python &amp; tooling <span>·</span> Meta</div>
        <h3 class="bdr-entry__title">We started writing documentation for AI coding agents</h3>
        <p class="bdr-entry__description">In 2024 I wrote documentation for developers. Somewhere in 2026 I noticed that a good share of the readers were not people.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>9 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-what-every-microservice-reimplements">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-what-every-microservice-reimplements/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python &amp; tooling <span>·</span> Meta</div>
        <h3 class="bdr-entry__title">What every production Python microservice reimplements</h3>
        <p class="bdr-entry__description">Open the repository of any backend service that has been in production for a year and look for the code that is not the product.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>8 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-what-happens-when-kafka-is-down-for-an-hour">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-what-happens-when-kafka-is-down-for-an-hour/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka &amp; messaging <span>·</span> Design</div>
        <h3 class="bdr-entry__title">What happens when Kafka is down for an hour?</h3>
        <p class="bdr-entry__description">Not &quot;is down for a second, and the retry catches it&quot;. An hour: a broker rolling badly, a disk full on every node, a network partition between availability zones.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-what-to-monitor-in-a-sqlalchemy-connection-pool">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-what-to-monitor-in-a-sqlalchemy-connection-pool/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">What to monitor in a SQLAlchemy connection pool</h3>
        <p class="bdr-entry__description">The dashboard everyone builds first shows connections in use, and it is the least useful of the numbers available.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>7 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-when-should-redis-fail-open">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-when-should-redis-fail-open/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis &amp; idempotency <span>·</span> Design</div>
        <h3 class="bdr-entry__title">When should Redis fail open?</h3>
        <p class="bdr-entry__description">Redis is down. It is your cache, your rate limiter and the store behind your idempotency keys, and every request that arrives now has to decide what to do without it.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-why-application-lifecycle-should-not-belong-to-fastapi">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-why-application-lifecycle-should-not-belong-to-fastapi/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Service lifecycle <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Why application lifecycle should not belong to FastAPI</h3>
        <p class="bdr-entry__description">FastAPI&#x27;s lifespan is a good API. It is an async context manager: whatever you set up before the yield is the startup, whatever you do after it is the shutdown, and it runs…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>5 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-why-grpc-interceptors-break-on-streaming-rpcs">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-why-grpc-interceptors-break-on-streaming-rpcs/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Why gRPC interceptors break on streaming RPCs</h3>
        <p class="bdr-entry__description">An interceptor that times a call, counts its errors and binds a request id is twenty lines, and it works.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>7 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-why-i-stopped-wrapping-http-clients">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-why-i-stopped-wrapping-http-clients/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP &amp; resilience <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Why I stopped wrapping HTTP clients</h3>
        <p class="bdr-entry__description">Every company I have worked at eventually wrote its own HTTP client wrapper. It starts as a retry helper, grows a config class, learns to emit metrics, and ends as class…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>7 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-your-models-and-your-schema-have-drifted">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-your-models-and-your-schema-have-drifted/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Your models and your schema have drifted. Would CI notice?</h3>
        <p class="bdr-entry__description">The migration ran, the deploy went out, and the models and the database now say different things.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>7 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-zero-dependency-cores">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-zero-dependency-cores/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python &amp; tooling <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Zero-dependency cores: why optional dependencies matter in infrastructure libraries</h3>
        <p class="bdr-entry__description">An infrastructure library is one that ends up in every service, and every dependency it declares ends up there too.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">Sep 7, 2026</time><span>·</span><span>6 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-06-pg-partsmith">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-06-pg-partsmith/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Libraries</div>
        <h3 class="bdr-entry__title">Managing PostgreSQL partitions, one failure at a time</h3>
        <p class="bdr-entry__description">There are two ways a partitioned table gets you out of bed. The first is an INSERT at 03:00 that PostgreSQL rejects because nobody created next month&#x27;s partition.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-06">Sep 6, 2026</time><span>·</span><span>12 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-06-timeouts-are-not-deadlines">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-06-timeouts-are-not-deadlines/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP &amp; resilience <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Timeouts are not deadlines: how latency budgets break across microservices</h3>
        <p class="bdr-entry__description">Every service I have run had a timeout on every outgoing call, and every one of them still managed to take longer than any number in its config.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-06">Sep 6, 2026</time><span>·</span><span>10 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-05-30-welcome">
    <a class="bdr-entry__link bdr-card" href="posts/2026-05-30-welcome/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python &amp; tooling <span>·</span> Meta</div>
        <h3 class="bdr-entry__title">Welcome to the Bedrock Python Blog</h3>
        <p class="bdr-entry__description">This is the home of the Bedrock Python ecosystem — what it is, why it exists, and the thinking behind it.</p>
        <div class="bdr-entry__meta"><time datetime="2026-05-30">May 30, 2026</time><span>·</span><span>2 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-05-28-introducing-mr-review">
    <a class="bdr-entry__link bdr-card" href="posts/2026-05-28-introducing-mr-review/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python &amp; tooling <span>·</span> Tools</div>
        <h3 class="bdr-entry__title">Introducing mr-review: AI-powered merge request reviews</h3>
        <p class="bdr-entry__description">Code review is one of the highest-leverage activities in a software team, and also one of the most inconsistent. Reviewers get tired, context-switch mid-review, miss things.</p>
        <div class="bdr-entry__meta"><time datetime="2026-05-28">May 28, 2026</time><span>·</span><span>2 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-05-15-transactional-outbox-with-omni-box">
    <a class="bdr-entry__link bdr-card" href="posts/2026-05-15-transactional-outbox-with-omni-box/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka &amp; messaging <span>·</span> Libraries</div>
        <h3 class="bdr-entry__title">The Transactional Outbox pattern in Python: omni-box</h3>
        <p class="bdr-entry__description">Distributed systems have a classic problem: you want to update your database and publish an event to Kafka in the same operation, but there is no cross-system transaction.</p>
        <div class="bdr-entry__meta"><time datetime="2026-05-15">May 15, 2026</time><span>·</span><span>2 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
<!-- catalog:articles:end -->
      </div>
      <div class="bdr-empty" data-blog-empty hidden>
        <span class="bdr-empty__icon" aria-hidden="true">⌕</span><h3>No articles found. A different angle?</h3>
        <p>Try a broader term like “retries” or “PostgreSQL”, or clear a filter.</p>
        <button class="bdr-btn bdr-btn--primary" type="button" data-blog-reset>Clear all filters</button>
      </div>
      <footer class="bdr-results-footer" data-blog-controls hidden>
        <span data-blog-range></span><nav class="bdr-pagination" aria-label="Article pages" data-blog-pagination></nav>
      </footer>
    </section>
  </div>
</div>
