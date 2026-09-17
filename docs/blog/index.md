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
      <a class="bdr-collection bdr-collection--resilience" data-blog-collection="reliability" href="posts/2026-09-13-production-http-grpc-clients/">
        <div class="bdr-collection__icon" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><rect x="4" y="16" width="12" height="16" rx="3"/><rect x="32" y="16" width="12" height="16" rx="3"/><path d="M16 24h16m-11-5 5 5-5 5M10 10V6m28 36v-4"/></svg></div>
        <div><span class="bdr-collection__label">WHEN DEPENDENCIES FAIL</span><h3>Build resilient services</h3><p>Deadlines, retries & circuit breakers</p></div><span class="bdr-collection__arrow" aria-hidden="true">↗</span>
      </a>
      <a class="bdr-collection bdr-collection--postgres" data-blog-collection="postgres" href="posts/2026-09-13-postgresql-partition-maintenance/">
        <div class="bdr-collection__icon" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><ellipse cx="24" cy="11" rx="15" ry="6"/><path d="M9 11v25c0 3.3 6.7 6 15 6s15-2.7 15-6V11M9 23c0 3.3 6.7 6 15 6s15-2.7 15-6M9 35c0 3.3 6.7 6 15 6s15-2.7 15-6"/></svg></div>
        <div><span class="bdr-collection__label">BEYOND THE QUERY</span><h3>Postgres in production</h3><p>Partitions, sessions & migrations</p></div><span class="bdr-collection__arrow" aria-hidden="true">↗</span>
      </a>
      <a class="bdr-collection bdr-collection--messaging" data-blog-collection="messaging" href="posts/2026-09-13-reliable-events-outbox-inbox-kafka/">
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
  <article class="bdr-entry" data-article-id="2026-09-13-python-library-from-template-to-release">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-python-library-from-template-to-release/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python &amp; tooling <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">A Python library from template to release</h3>
        <p class="bdr-entry__description">Maintaining several Python libraries repeats more than code. Each repository needs packaging, tests, formatting rules, documentation and a path to PyPI.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>4 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-production-http-grpc-clients">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-production-http-grpc-clients/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP &amp; resilience <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Building HTTP and gRPC clients for production</h3>
        <p class="bdr-entry__description">A client for an external service needs to bound the cost of failure: waiting time, attempts and load on the dependency. These decisions interact.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>4 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-idempotency-in-apis-and-background-jobs">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-idempotency-in-apis-and-background-jobs/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis &amp; idempotency <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Idempotency in APIs and background jobs</h3>
        <p class="bdr-entry__description">A client sends a request, loses the response and retries. A worker finishes a job but crashes before acknowledging it.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>3 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-kafka-in-python-services">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-kafka-in-python-services/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka &amp; messaging <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">Kafka in a Python service: producers, consumers and operations</h3>
        <p class="bdr-entry__description">A Kafka client must fit the service&#x27;s rules: who owns topics, when a message counts as processed and what happens during shutdown. Library defaults do not answer those questions.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>3 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-partitioning-an-existing-postgresql-table">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-partitioning-an-existing-postgresql-table/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">Partitioning an existing PostgreSQL table</h3>
        <p class="bdr-entry__description">Partitioning an existing table changes more than row storage. It affects uniqueness, foreign keys, query plans and writes during the transition.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>3 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-postgresql-partition-maintenance">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-postgresql-partition-maintenance/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Design</div>
        <h3 class="bdr-entry__title">PostgreSQL partition maintenance: creation, archiving and deletion</h3>
        <p class="bdr-entry__description">Creating the next partition is relatively straightforward. Operational complexity surrounds it: who owns the schedule, which tables may be deleted, what happens if archiving…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>3 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-production-python-grpc-server">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-production-python-grpc-server/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Preparing a Python gRPC server for production</h3>
        <p class="bdr-entry__description">Registering a servicer and opening a port is enough for the first gRPC call. Operating that server requires decisions around the handler: which errors clients receive, when the…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>4 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-redis-failures-and-health-checks">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-redis-failures-and-health-checks/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis &amp; idempotency <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Redis failures: health checks and service behavior</h3>
        <p class="bdr-entry__description">Redis may serve as a cache, a rate limiter and an idempotency store within the same service. Those uses need different failure policies.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>4 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-reliable-events-outbox-inbox-kafka">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-reliable-events-outbox-inbox-kafka/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka &amp; messaging <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Reliable event delivery with Outbox, Inbox and Kafka</h3>
        <p class="bdr-entry__description">A service saves an order in PostgreSQL and needs to publish it through Kafka. The process can fail between commit and publication.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>3 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-sqlalchemy-pgbouncer-pools">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-sqlalchemy-pgbouncer-pools/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">SQLAlchemy and PgBouncer: configuring and diagnosing connection pools</h3>
        <p class="bdr-entry__description">A connection pool is full while the application responds quickly. After the database slows down, the same utilization graph remains full, but requests now time out.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>3 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-sqlalchemy-sessions-and-transactions">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-sqlalchemy-sessions-and-transactions/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Design</div>
        <h3 class="bdr-entry__title">SQLAlchemy sessions and transactions: who owns commit</h3>
        <p class="bdr-entry__description">An order and its creation event need to appear together. If each repository calls commit() independently, failure to record the event leaves an order without an event.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>3 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-testing-alembic-migrations-in-ci">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-testing-alembic-migrations-in-ci/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL &amp; SQLAlchemy <span>·</span> Tutorials</div>
        <h3 class="bdr-entry__title">Testing Alembic migrations in CI</h3>
        <p class="bdr-entry__description">A successful alembic upgrade head checks one path: applying history to the chosen starting state.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>3 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-python-service-lifecycle">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-python-service-lifecycle/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Service lifecycle <span>·</span> Design</div>
        <h3 class="bdr-entry__title">The Python service lifecycle: startup, health checks and shutdown</h3>
        <p class="bdr-entry__description">An HTTP API, Kafka consumer and background job may share settings, a database pool and outbound clients.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>3 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-ai-code-review-should-not-be-fully-autonomous">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-ai-code-review-should-not-be-fully-autonomous/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python &amp; tooling <span>·</span> Tools</div>
        <h3 class="bdr-entry__title">Why AI code review needs human oversight</h3>
        <p class="bdr-entry__description">AI helped me find bugs in my own merge requests. The problems began when I started automating reviews of colleagues&#x27; code: useful findings arrived alongside incorrect suggestions…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>4 min read</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-why-bedrock-python-libraries">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-why-bedrock-python-libraries/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python &amp; tooling <span>·</span> Meta</div>
        <h3 class="bdr-entry__title">Why I extract Python service infrastructure into libraries</h3>
        <p class="bdr-entry__description">Across Python services using the same stack, I kept assembling similar infrastructure: SQLAlchemy sessions, Redis and Kafka clients, resource startup and shutdown, retries…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">Sep 13, 2026</time><span>·</span><span>4 min read</span></div>
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
  <article class="bdr-entry" data-article-id="2026-09-06-timeouts-are-not-deadlines">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-06-timeouts-are-not-deadlines/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP &amp; resilience <span>·</span> Design</div>
        <h3 class="bdr-entry__title">Timeouts are not deadlines: how latency budgets break across microservices</h3>
        <p class="bdr-entry__description">Imagine an Orders service: it reads stock over HTTP, then reserves items and charges a card over gRPC.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-06">Sep 6, 2026</time><span>·</span><span>8 min read</span></div>
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
