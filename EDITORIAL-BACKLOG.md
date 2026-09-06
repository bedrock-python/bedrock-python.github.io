# Editorial backlog: production Python engineering

The blog is not about Bedrock packages. It is about production Python
engineering, written by the people building Bedrock packages. Every post opens
on a problem the reader already has and only near the end shows which library
came out of it. Nobody searches for "introducing redis-client-kit"; people
search for "PgBouncer transaction mode async SQLAlchemy" and find the library
by accident. That is the discovery model this backlog serves.

This file is the working plan for the series. It lives in the repository so
any session can pick up the next post without re-deriving the plan.

## Two formats, one idea

Each topic ships twice: the canonical deep dive here, and a short post on
LinkedIn that points to it. They are not the same text.

| | Blog post (canonical) | LinkedIn post |
|---|---|---|
| Length | 1500-4000 words | 150-500 words |
| Carries | diagrams, code, failure scenarios, numbers, links to docs and GitHub | one idea, one surprising fact, one diagram or snippet, one conclusion |
| Ends with | the Bedrock library that came out of the problem, stated once, without a pitch | link to the blog post |

## House rules for a post

- First person, one engineer talking. The welcome post and the pg-partsmith post are the register.
- The problem first. The library appears once the reader would have asked "so what do you do about it".
- Every code sample runs against the published package version named in the post.
- Every number is measured, not reasoned. If it was not measured, it is not in the post.
- Front matter per `CONTRIBUTING.md`: `date`, `authors: [alex]`, `categories`, `tags`, and `<!-- more -->` after the lede.
- The listings are hand-written. A new post is added in five places: `docs/blog/index.md` (card inside `[data-bdr-grid]`), `docs/index.md` (three latest cards), `docs/blog/category/<cat>.md`, `docs/blog/category/index.md` (counts), `docs/blog/archive/index.md`.
- `make docs-build`, then grep the built HTML for the title before pushing.

## Publishing order

One post a week. The order alternates between the reliability line
(deadlines, retries, idempotency), the operations line (migrations, shutdown,
PgBouncer) and the two posts that speak for the whole organisation (docs for
agents, twelve repositories).

| Week | Post | Category | Shows | Status |
|---|---|---|---|---|
| 1 | Timeouts are not deadlines | Design | deadline-budget, clientwright, grpc-client-kit | planned |
| 2 | The five migration tests every project should run in CI | Tutorials | alembic-gauntlet | planned |
| 3 | Graceful shutdown in Kubernetes is a protocol, not a signal handler | Design | servicewright | planned |
| 4 | Idempotency keys: the part everyone gets wrong | Design | idempotency-kit | planned |
| 5 | Why I stopped wrapping HTTP clients | Design | clientwright | planned |
| 6 | Exactly-once is a lie; exactly-once effects are not | Design | omni-box, idempotency-kit | planned |
| 7 | We started writing documentation for AI coding agents | Meta | every library, python-library-template | planned |
| 8 | PgBouncer transaction mode and async SQLAlchemy | Tutorials | sqlalchemy-foundation-kit | planned |
| 9 | RAG was the wrong abstraction for searching our team chat | Tools | mattermind | planned |
| 10 | Safe gRPC retries: which status codes you should actually retry | Design | grpc-client-kit | planned |
| 11 | What every production Python microservice reimplements | Meta | the whole catalog | planned |
| 12 | Twelve repositories, one engineering standard | Meta | python-library-template | planned |

Status moves through `planned`, `drafting`, `review`, `published`.

## Post briefs

Each brief has the file name, the search title, the LinkedIn hook, the section
plan, the one diagram, the code that must appear, and the closing library
mention. The section plan is a starting point, not a contract.

### 1. Timeouts are not deadlines

- File: `docs/blog/posts/2026-09-13-timeouts-are-not-deadlines.md`
- Search title: *Timeouts Are Not Deadlines: How Latency Budgets Break Across Microservices*
- LinkedIn hook: "Your service has a 10-second timeout. It can still take 30 seconds."
- Tags: `deadline-budget`, `clientwright`, `grpc-client-kit`, `timeouts`, `microservices`
- Sections:
  - A timeout limits an operation; a deadline limits the request. Define both.
  - The arithmetic: A calls B calls C, each with a fresh 5-second timeout, and the caller waits 15 seconds. Add three retries and it is 45.
  - Where the deadline lives: a value in the request context, decremented at every hop, carried in a header or gRPC metadata.
  - The safety margin: why the last hop must stop early enough to roll back and serialise a response.
  - What changes in the code when the deadline is one object, not five timeouts.
- Diagram: a timeline of A, B, C, D on one axis showing the fresh-timeout case against the shared-deadline case.
- Code: a request budget created at the edge, passed to an HTTP call and a gRPC call, each deriving its own timeout from the remaining time.
- Closing library: deadline-budget as the budget object, clientwright and grpc-client-kit as the clients that read it.

### 2. The five migration tests every project should run in CI

- File: `docs/blog/posts/2026-09-20-five-alembic-migration-tests.md`
- Search title: *The 5 Alembic Migration Tests Every Python Project Should Run in CI*
- LinkedIn hook: "We test our code heavily. Then we deploy untested database migrations."
- Tags: `alembic-gauntlet`, `alembic`, `sqlalchemy`, `postgresql`, `testing`, `ci`
- Sections:
  - The gap: unit tests, integration tests, and a migration nobody has run backwards.
  - Test one: every revision upgrades and downgrades cleanly.
  - Test two: the models and the schema have not drifted.
  - Test three: exactly one head.
  - Test four: downgrade to base leaves nothing behind.
  - Test five: constraint names follow the naming convention, so downgrades can find them.
  - Running it in CI with a real PostgreSQL in a container.
- Diagram: the `upgrade → downgrade → upgrade` loop with the assertion at each step.
- Code: the five tests as they read in a project's `tests/test_migrations.py`, then the same five as one fixture.
- Closing library: alembic-gauntlet, which is the five tests packaged.

### 3. Graceful shutdown in Kubernetes is a protocol, not a signal handler

- File: `docs/blog/posts/2026-09-27-graceful-shutdown-is-a-protocol.md`
- Search title: *Graceful Shutdown in Kubernetes Is Harder Than Catching SIGTERM*
- LinkedIn hook: "SIGTERM, cleanup, exit is not graceful shutdown."
- Tags: `servicewright`, `kubernetes`, `graceful-shutdown`, `asyncio`, `fastapi`, `grpc`
- Sections:
  - What actually happens between `kubectl rollout` and the last packet: endpoints removal races the signal.
  - Readiness must go false before draining starts, and the pod must keep serving while the endpoint list catches up.
  - Draining in-flight HTTP and gRPC requests, and what to do with a consumer mid-batch.
  - `terminationGracePeriodSeconds` as the outer deadline the whole sequence must fit inside.
  - Cleanup order: stop accepting, drain, close pools, exit.
- Diagram: a timeline `SIGTERM → ready=false → drain → cleanup → exit` with the Kubernetes endpoint update overlaid.
- Code: a lifecycle with explicit `Bootstrap → Warmup → Ready → Serve → Drain → Cleanup` phases hosting an HTTP server and a worker.
- Closing library: servicewright, whose lifecycle is that sequence.

### 4. Idempotency keys: the part everyone gets wrong

- File: `docs/blog/posts/2026-10-04-idempotency-keys-the-part-everyone-gets-wrong.md`
- Search title: *Idempotency Keys: The Part Everyone Gets Wrong*
- LinkedIn hook: "An Idempotency-Key is not a distributed lock."
- Tags: `idempotency-kit`, `idempotency`, `http`, `redis`, `distributed-systems`
- Sections:
  - What the key promises: the same request produces the same effect once, and the same response every time.
  - The concurrent case: two identical requests in flight at the same time, and the three outcomes a store can give the second one.
  - Fingerprinting the body, so a reused key with a different payload is rejected, not replayed.
  - Result caching and what to cache when the handler failed.
  - Scope and TTL: per user, per endpoint, for how long.
  - Fail-open or fail-closed when the store is down.
- Diagram: a sequence diagram of two identical POSTs arriving within milliseconds.
- Code: a handler wrapped in idempotency with a Redis backend, then the collision test.
- Closing library: idempotency-kit.

### 5. Why I stopped wrapping HTTP clients

- File: `docs/blog/posts/2026-10-11-why-i-stopped-wrapping-http-clients.md`
- Search title: *Why I Stopped Wrapping HTTP Clients in Python*
- LinkedIn hook: "Every company eventually writes its own httpx wrapper. I think that is the wrong abstraction."
- Tags: `clientwright`, `httpx`, `aiohttp`, `requests`, `retries`, `circuit-breaker`
- Sections:
  - The wrapper's life: born as a retry helper, grows a config class, ends as a client nobody can migrate away from.
  - What the wrapper actually owns: retries, backoff, deadlines, circuit breaking, telemetry. None of it is HTTP.
  - The alternative: configure the native client and keep it native, so `type(client) is httpx.AsyncClient` stays true.
  - Capability honesty: when a client cannot do what the policy asks, fail at construction, not at 3 a.m.
  - Migrating httpx to aiohttp with the reliability layer untouched.
- Diagram: the wrapper stack against the engine-beside-the-client layout.
- Code: one policy applied to an httpx client and an aiohttp client, and the assertion that the type is unchanged.
- Closing library: clientwright.

### 6. Exactly-once is a lie; exactly-once effects are not

- File: `docs/blog/posts/2026-10-18-exactly-once-effects.md`
- Search title: *Exactly-Once Is a Lie. Exactly-Once Effects Are Not.*
- LinkedIn hook: "Kafka cannot make your database update exactly once."
- Tags: `omni-box`, `idempotency-kit`, `kafka`, `outbox`, `inbox`, `exactly-once`
- Sections:
  - Delivery guarantees are about messages; the business cares about effects.
  - Every failure window between a commit and a publish, mapped one by one.
  - The outbox closes the producer side; the inbox closes the consumer side; the idempotency key closes the HTTP edge.
  - Why the library must not own the transaction.
  - The whole path: HTTP → idempotency → transaction → outbox → Kafka → inbox → consumer transaction.
- Diagram: the full path with the three dedup points marked.
- Code: a use case writing a row and an outbox record in one transaction, and the consumer side with the inbox.
- Closing library: omni-box for outbox and inbox, idempotency-kit at the edge. Links back to the existing outbox post rather than repeating it.

### 7. We started writing documentation for AI coding agents

- File: `docs/blog/posts/2026-10-25-documentation-for-ai-coding-agents.md`
- Search title: *Building Python Libraries for AI Coding Agents, Not Just Humans*
- LinkedIn hook: "In 2024 I wrote docs for developers. In 2026 I realised half of my documentation users are not human."
- Tags: `bedrock-python`, `documentation`, `ai-agents`, `python-library-template`
- Sections:
  - The observation: an assistant wiring a library guesses an API that does not exist, because the docs explain concepts and it needed invariants.
  - Human docs and agent docs want different things: browsing against exact API, wrong/right examples, integration constraints.
  - What an `agents.md` page contains and why every library ships one.
  - Copy page as Markdown, open in ChatGPT, open in Claude: the documentation as an input, not a destination.
  - Invariants as sentences the model can hold: "Engine, never Session".
- Diagram: the two columns, human docs against agent docs.
- Code: a fragment of an agents page with a WRONG and a RIGHT example side by side.
- Closing library: the org convention itself, with pg-partsmith as the worked example.

### 8. PgBouncer transaction mode and async SQLAlchemy

- File: `docs/blog/posts/2026-11-01-pgbouncer-transaction-mode-async-sqlalchemy.md`
- Search title: *PostgreSQL + PgBouncer + Async SQLAlchemy: The Production Setup Nobody Documents Enough*
- LinkedIn hook: "Your SQLAlchemy config works perfectly until PgBouncer enters transaction mode."
- Tags: `sqlalchemy-foundation-kit`, `sqlalchemy`, `pgbouncer`, `postgresql`, `asyncpg`
- Sections:
  - What transaction pooling takes away: session state, prepared statements, `SET`, advisory locks across transactions.
  - The asyncpg prepared statement cache and the error you get on the second deploy.
  - Pool sizing when there is a pool in front of your pool.
  - What to monitor: checked out, overflow, wait time, and the one metric that predicts an outage.
  - Closing pools during a rollout without dropping in-flight transactions.
- Diagram: application pool, PgBouncer, PostgreSQL, with the state that survives each boundary.
- Code: the engine configuration that works in transaction mode, and the settings that break it.
- Closing library: sqlalchemy-foundation-kit, which ships that configuration and the pool metrics.

### 9. RAG was the wrong abstraction for searching our team chat

- File: `docs/blog/posts/2026-11-08-rag-was-the-wrong-abstraction-for-team-chat.md`
- Search title: *RAG Was the Wrong Abstraction for Searching Our Team Chat*
- LinkedIn hook: "We did not embed a single message. The assistant still answers with citations."
- Tags: `mattermind`, `mattermost`, `llm`, `rag`, `search`
- Sections:
  - The default plan: embed everything, retrieve, generate. Why it fails on chat: freshness, permissions, threads, two languages.
  - Search first: expand the query, run the platform's own search, fetch the threads, follow the permalinks.
  - Permalinks as a knowledge graph.
  - Citations as a requirement, not a feature.
  - What this costs against an embedding pipeline, measured.
- Diagram: the agent loop, query expansion to search to fetch to permalink walk to cited answer.
- Code: the tool definitions the model calls, and one full trace of a question.
- Closing library: mattermind.

### 10. Safe gRPC retries: which status codes you should actually retry

- File: `docs/blog/posts/2026-11-15-safe-grpc-retries.md`
- Search title: *gRPC Retries: When Retrying Is More Dangerous Than Failing*
- LinkedIn hook: "Retrying INTERNAL is not resilience."
- Tags: `grpc-client-kit`, `grpc`, `retries`, `deadlines`, `circuit-breaker`
- Sections:
  - The status code table: which codes mean "try again", which mean "you broke it", which mean "nobody knows".
  - Idempotent methods only, and how the client knows.
  - `max_attempts=3` must not triple the deadline.
  - Retries and streaming do not mix the way you think.
  - Circuit breaker state per backend, not per channel.
- Diagram: the status code table rendered as three columns.
- Code: a retry policy declared once, applied to a channel, with the deadline shared across attempts.
- Closing library: grpc-client-kit.

### 11. What every production Python microservice reimplements

- File: `docs/blog/posts/2026-11-22-what-every-python-microservice-reimplements.md`
- Search title: *What Every Production Python Microservice Reimplements*
- LinkedIn hook: "I kept seeing the same 3,000 lines in every service. None of it was the product."
- Tags: `bedrock-python`, `architecture`, `microservices`
- Sections:
  - The list: lifecycle, health, shutdown, retries, timeouts, breakers, sessions, transactions, Redis, Kafka, idempotency, outbox, metrics, tracing, migration tests.
  - Why a framework is the wrong answer: it owns the application; a service needs to own itself.
  - Small independent libraries with zero-dependency cores and optional extras.
  - How the pieces compose without knowing about each other.
- Diagram: the request path with each concern pinned to the library that owns it.
- Code: a service skeleton with the libraries wired, under a hundred lines.
- Closing library: the catalog page. This is the post that explains why Bedrock exists.

### 12. Twelve repositories, one engineering standard

- File: `docs/blog/posts/2026-11-29-twelve-repositories-one-standard.md`
- Search title: *How I Standardized 12 Open-Source Python Libraries Without Building a Monorepo*
- LinkedIn hook: "12 repos. One engineering standard. No monorepo."
- Tags: `bedrock-python`, `python-library-template`, `uv`, `release-please`, `github`
- Sections:
  - The stack: uv, hatchling, Ruff, mypy strict, pytest, Release Please, Trusted Publishing.
  - Repository settings as code: rulesets, security policy, Dependabot on uv, one script that applies them.
  - A Copier template instead of copy-paste, and what happens when the template changes.
  - Releases across twelve repositories without a human typing a version.
  - What a monorepo would have given, and why I did not want it.
- Diagram: the template fan-out to twelve repositories with the update path back.
- Code: the release workflow and the settings script, trimmed to what matters.
- Closing library: python-library-template.

## The pool behind the twelve

Topics with a brief's worth of material, to draw from once the first twelve
are out. One line each; the brief gets written when the post is scheduled.

- servicewright: readiness as part of the deployment algorithm; warmup, readiness and liveness are different things; transport-independent errors; a runtime that is not a framework; zero-dependency cores.
- clientwright: retry budgets and retry storms; Retry-After, backoff and jitter; circuit breakers per origin; PII masking with observability intact; observability that survives a client migration.
- deadline-budget: designing an API backwards from the SLO; why deadlines need a safety margin.
- grpc-client-kit: channel identity beyond the address; client-side load balancing without shared breaker state; an unchecked backend is not a healthy backend.
- grpc-server-kit: the anatomy of a production gRPC server; why interceptors break on streaming; graceful shutdown for `grpc.aio`; mapping exceptions to status codes without leaking internals; TLS against mTLS internally.
- sqlalchemy-foundation-kit: Unit of Work in SQLAlchemy 2; who owns the transaction; stop passing AsyncSession everywhere; sessions are resources, not dependencies.
- redis-client-kit: what a production Redis client needs; PING is not a health check; cluster changes more than the connection string; when Redis should fail open.
- aiokafka-foundation-kit: the production checklist; producers need a lifecycle; should the application create topics; tracing an event across Kafka; consumer shutdown in Kubernetes.
- idempotency-kit: Stripe-style keys explained; idempotency across a chain of services; idempotency for jobs and consumers; idempotency against deduplication against exactly-once.
- omni-box: the inbox as the other half; what happens when Kafka is down for an hour; an extensible processing pipeline.
- alembic-gauntlet: schema drift and whether CI would notice; `alembic upgrade head` is not a test; how branches reach production; naming conventions matter more than they look.
- pg-partsmith: partitioning an existing table without rewriting the application; RANGE plus HASH for multi-tenant data; migrating from pg_partman; UUIDv7 as a partition key; retention is not DROP TABLE; a plan phase for destructive automation; maintenance as a CronJob; backfilling safely.
- mr-review: review should not be autonomous; no comment without human approval; self-hosted architecture; one UI for five forges; what context to send the model; can local models review production code, with fifty real bugs and numbers.
- mattermind: citations as a requirement; query expansion for bilingual teams; tool calling against RAG; a CLI assistant over Mattermost.
- python-library-template: starting a library in 2026; Trusted Publishing without tokens; what every repository should configure on GitHub; Copier against copy-paste.
- Cross-cutting: retries, timeouts, deadlines, idempotency and circuit breakers are different problems; effectively-once operations in an at-least-once world.
