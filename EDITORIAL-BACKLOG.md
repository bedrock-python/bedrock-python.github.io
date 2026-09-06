# Editorial plan: production Python engineering

The blog is not about Bedrock packages. It is about production Python
engineering, written by the people building Bedrock packages. Every post opens
on a problem the reader already has and only near the end shows which library
came out of it. Nobody searches for "introducing redis-client-kit"; people
search for "PgBouncer transaction mode async SQLAlchemy" and find the library
by accident. That is the discovery model this plan serves.

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
| Cadence | whenever a post is done | one a week, in the plan's order, from a queue of finished posts |

## House rules for a post

- First person, one engineer talking. The welcome post and the pg-partsmith post are the register.
- The problem first. The library appears once the reader would have asked "so what do you do about it".
- Every code sample runs against the published package version named in the post.
- Every number is measured, not reasoned. If it was not measured, it is not in the post.
- Front matter per `CONTRIBUTING.md`: `date`, `authors: [alex]`, `categories`, `tags`, and `<!-- more -->` after the lede. The date in the file name and the front matter is the day the post merges, set when it does.
- The listings are hand-written. A new post is added in five places: `docs/blog/index.md` (card inside `[data-bdr-grid]`), `docs/index.md` (three latest cards), `docs/blog/category/<cat>.md`, `docs/blog/category/index.md` (counts), `docs/blog/archive/index.md`.
- `make docs-build`, then grep the built HTML for the title before pushing.
- A post that quotes a library feature is checked against the library's current docs before drafting. Where a plan below says "check", the feature may not exist yet; the post then proposes it and the library gets an issue.
- A bug found while measuring is fixed first. File the issue in the library's repo with the repro and the cause, mark the post `drafting, blocked on <repo> #N`, move on to a post that does not depend on it. When the fix is released, re-measure against the new version and continue the post as if the bug had never existed. A published post never carries a caveat paragraph about a library's bug.

## Series

Forty-eight posts in priority order, not on a calendar. They are written
here as fast as they get written and go live on the blog when they merge.
The only cadence is LinkedIn: one short version a week, in the same order,
however far ahead the blog has run. Every post belongs to one of seven
series. The series are the site's long-term structure; the order below
interleaves them so no stretch of posts is about one library.

| Series | What it argues | Libraries | Posts |
|---|---|---|---|
| Reliability | Deadlines, retries, circuit breakers and idempotency are different problems solved at different layers | deadline-budget, clientwright, grpc-client-kit, idempotency-kit, redis-client-kit | 1, 4, 10, 13, 17, 18, 22, 40, 47 |
| Effectively-once | At-least-once delivery plus dedup at every boundary is the only exactly-once that exists | omni-box, idempotency-kit, aiokafka-foundation-kit | 6, 16, 24, 26, 30, 32, 41 |
| Lifecycle and Kubernetes | A service is a lifecycle that hosts entrypoints; health and shutdown are part of the deployment algorithm | servicewright, grpc-server-kit, redis-client-kit | 3, 15, 19, 35, 37, 38 |
| Clients and servers | Keep the native client native; the reliability layer lives beside it, not around it | clientwright, grpc-client-kit, grpc-server-kit | 5, 20, 28, 33, 43 |
| Database in production | Sessions, transactions, PgBouncer, migrations and partitions, as they behave under load and during deploys | sqlalchemy-foundation-kit, alembic-gauntlet, pg-partsmith | 2, 8, 14, 21, 25, 27, 29, 31, 34, 39, 44 |
| AI tooling | Where an LLM belongs in the engineering loop, with a human in front of every side effect | mr-review, mattermind, the agents pages | 7, 9, 23, 36, 42 |
| Bedrock and open source | Why the organisation exists and how twelve repositories stay one standard | python-library-template, the catalog | 11, 12, 45, 46, 48 |

## The list

Status moves through `planned`, `drafting`, `review`, `published`; `published` means merged to master, whether or not the LinkedIn version has gone out yet.

### Block 1: the opening dozen

The twelve posts with the widest reach and the clearest problem statements.
Full briefs below.

| # | Post | Category | Series | Status |
|---|---|---|---|---|
| 1 | Timeouts are not deadlines | Design | Reliability | drafting, blocked on clientwright #24 and #25 |
| 2 | The five migration tests every project should run in CI | Tutorials | Database | review |
| 3 | Graceful shutdown in Kubernetes is a protocol, not a signal handler | Design | Lifecycle | drafting, blocked on servicewright #46 |
| 4 | Idempotency keys: the part everyone gets wrong | Design | Reliability | planned |
| 5 | Why I stopped wrapping HTTP clients | Design | Clients | planned |
| 6 | Exactly-once is a lie; exactly-once effects are not | Design | Effectively-once | planned |
| 7 | We started writing documentation for AI coding agents | Meta | AI tooling | planned |
| 8 | PgBouncer transaction mode and async SQLAlchemy | Tutorials | Database | planned |
| 9 | RAG was the wrong abstraction for searching our team chat | Tools | AI tooling | planned |
| 10 | Safe gRPC retries: which status codes you should actually retry | Design | Reliability | planned |
| 11 | What every production Python microservice reimplements | Meta | Bedrock | planned |
| 12 | Twelve repositories, one engineering standard | Meta | Bedrock | planned |

### Block 2: going deeper

Second posts in each series: the follow-up questions readers of block 1 ask.

| # | Post | Category | Series | Status |
|---|---|---|---|---|
| 13 | Retries can make an outage worse: designing a retry budget | Design | Reliability | planned |
| 14 | Testing database migrations with Testcontainers: up, down and up again | Tutorials | Database | planned |
| 15 | One lifecycle for HTTP, gRPC, workers and cron jobs | Libraries | Lifecycle | planned |
| 16 | Transactional inbox: the other half of the outbox pattern | Design | Effectively-once | planned |
| 17 | Circuit breakers should be per origin, not per client | Design | Reliability | planned |
| 18 | Retry-After, backoff and jitter: what a production HTTP client actually does | Tutorials | Reliability | planned |
| 19 | Why application lifecycle should not belong to FastAPI | Design | Lifecycle | planned |
| 20 | gRPC channels should not be pooled by address alone | Design | Clients | planned |
| 21 | The Unit of Work pattern in SQLAlchemy 2 | Tutorials | Database | planned |
| 22 | When should Redis fail open? | Design | Reliability | planned |
| 23 | AI code review should not be fully autonomous | Tools | AI tooling | planned |
| 24 | What happens when Kafka is down for an hour? | Design | Effectively-once | planned |

### Block 3: operations

Checklists, monitoring and the hands-on posts: what to run, what to watch,
what to do at 03:00.

| # | Post | Category | Series | Status |
|---|---|---|---|---|
| 25 | How to partition an existing PostgreSQL table without rewriting your application | Tutorials | Database | planned |
| 26 | The production checklist for aiokafka | Tutorials | Effectively-once | planned |
| 27 | Your models and your schema have drifted. Would CI notice? | Design | Database | planned |
| 28 | The anatomy of a production Python gRPC server | Tutorials | Clients | planned |
| 29 | Stop passing AsyncSession everywhere | Design | Database | planned |
| 30 | Idempotency for background jobs and Kafka consumers | Tutorials | Effectively-once | planned |
| 31 | Partition retention is not DROP TABLE | Design | Database | planned |
| 32 | Graceful Kafka consumer shutdown in Kubernetes | Tutorials | Effectively-once | planned |
| 33 | Why gRPC interceptors break on streaming RPCs | Design | Clients | planned |
| 34 | What to monitor in a SQLAlchemy connection pool | Tutorials | Database | planned |
| 35 | Redis health checks: PING is not the whole story | Design | Lifecycle | planned |
| 36 | Can local LLMs review production code? Fifty real bugs, four models | Tools | AI tooling | planned |

### Block 4: design and the organisation

The opinion pieces that need the earlier posts as groundwork, and the closing
posts about how the libraries are built.

| # | Post | Category | Series | Status |
|---|---|---|---|---|
| 37 | Warmup, readiness and liveness are three different things | Design | Lifecycle | planned |
| 38 | Transport-independent errors: one domain error, HTTP and gRPC responses | Design | Lifecycle | planned |
| 39 | Migrating from pg_partman to application-managed partitions | Tutorials | Database | planned |
| 40 | Idempotency across a chain of microservices | Design | Reliability | planned |
| 41 | Should your application create Kafka topics on startup? | Design | Effectively-once | planned |
| 42 | Why enterprise AI answers need citations | Tools | AI tooling | planned |
| 43 | Mapping Python exceptions to gRPC status codes without leaking internals | Tutorials | Clients | planned |
| 44 | UUIDv7 as a PostgreSQL partition key | Design | Database | planned |
| 45 | Publishing to PyPI without API tokens: Trusted Publishing end to end | Tutorials | Bedrock | planned |
| 46 | Zero-dependency cores: why optional dependencies matter in infrastructure libraries | Design | Bedrock | planned |
| 47 | Reliability is not `retry=3` | Design | Reliability | planned |
| 48 | How I start a production-grade Python library in 2026 | Meta | Bedrock | planned |

## Briefs: block 1

Each brief has the file name, the search title, the LinkedIn hook, the section
plan, the one diagram, the code that must appear, and the closing library
mention. The section plan is a starting point, not a contract.

### 1. Timeouts are not deadlines

- File: `docs/blog/posts/2026-09-06-timeouts-are-not-deadlines.md`, lab scripts in `docs/blog/lab/2026-09-06-timeouts-are-not-deadlines/`
- Blocked: measuring against clientwright 0.2.0 found two things, filed as [clientwright #24](https://github.com/bedrock-python/clientwright/issues/24) (an `attempt` ceiling escapes as a bare `TimeoutError` and is never retried) and [#25](https://github.com/bedrock-python/clientwright/issues/25) (`total` stops at the response headers on httpx). The draft is honest about both. When the fixes are released: re-run the lab against the new version, drop the boundary caveat in the retries section, bump the version line, move to `review`.
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

- File: `docs/blog/posts/2026-09-07-five-alembic-migration-tests.md`, lab in `docs/blog/lab/2026-09-07-five-alembic-migration-tests/`
- Found while measuring, fixed and released as alembic-gauntlet 0.2.2 (2026-09-06): the published 0.2.1 had no `asyncio` extra although every page says to install it (#32), and the testcontainers fixture imported a deprecated module (#33, #35). The post's numbers are from a run against 0.2.2. Also: Alembic applies the metadata naming convention to the name passed to `op.create_check_constraint`; the post has a section on it.
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

- File: `docs/blog/posts/YYYY-MM-DD-graceful-shutdown-is-a-protocol.md`, lab in `docs/blog/lab/2026-09-07-graceful-shutdown/`
- Blocked: measured on 0.9.1, readiness flips to 503 and the listener closes in the same tick, 44 of 48 requests refused in the second after SIGTERM, same as bare uvicorn; the Kubernetes page's "no preStop sleep needed" claim does not hold. Filed as [servicewright #46](https://github.com/bedrock-python/servicewright/issues/46), proposed `AppSpec(drain_delay_seconds=...)`. The post's centre is the before/after of that measurement.
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

- File: `docs/blog/posts/YYYY-MM-DD-idempotency-keys-the-part-everyone-gets-wrong.md`
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

- File: `docs/blog/posts/YYYY-MM-DD-why-i-stopped-wrapping-http-clients.md`
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

- File: `docs/blog/posts/YYYY-MM-DD-exactly-once-effects.md`
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

- File: `docs/blog/posts/YYYY-MM-DD-documentation-for-ai-coding-agents.md`
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

- File: `docs/blog/posts/YYYY-MM-DD-pgbouncer-transaction-mode-async-sqlalchemy.md`
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

- File: `docs/blog/posts/YYYY-MM-DD-rag-was-the-wrong-abstraction-for-team-chat.md`
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

- File: `docs/blog/posts/YYYY-MM-DD-safe-grpc-retries.md`
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

- File: `docs/blog/posts/YYYY-MM-DD-what-every-python-microservice-reimplements.md`
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

- File: `docs/blog/posts/YYYY-MM-DD-twelve-repositories-one-standard.md`
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

## Plans: blocks 2 to 4

One paragraph per post: the claim, what the reader takes away, what the post
shows, and the library it closes on. A plan becomes a brief in the format
above when the post is next up.

### 13. Retries can make an outage worse: designing a retry budget

Four attempts per hop across five hops is a thousand requests at the bottom
for one at the top, and that is the moment the bottom service is already
failing. The post walks through a retry storm from the first slow response to
the full outage, then introduces the retry budget: a ratio of retries to
requests per client, not a count per request. Shows a small load simulation
with and without the budget, measured. Closes on clientwright. Check whether
the retry policy already exposes a budget; if not, the post proposes it.

### 14. Testing database migrations with Testcontainers: up, down and up again

The hands-on companion to post 2. A pytest fixture starts PostgreSQL in a
container, walks every revision upgrade, downgrade, upgrade, and asserts the
schema at each step. Covers what running `alembic upgrade head` once in CI
does not catch, how long the loop takes on a real history, and how to keep it
under a minute. Closes on alembic-gauntlet as the fixture the post builds.

### 15. One lifecycle for HTTP, gRPC, workers and cron jobs

An HTTP server, a gRPC server, a Kafka consumer and a nightly job are one
application with four entrypoints, yet most codebases treat them as four
applications with four copies of startup, health and shutdown. The post
presents the host-and-entrypoints model: one lifecycle, shared DI scopes,
warmup and readiness, entrypoints that can run in one process or be split
across deployments without a code change. Shows a FastAPI app and a
scheduler under one host, then the same code as two deployments. Closes on
servicewright.

### 16. Transactional inbox: the other half of the outbox pattern

The outbox guarantees the event leaves; nothing guarantees it arrives once.
The post covers the consumer side: at-least-once delivery, the inbox table
keyed by message id, processing inside the consumer's own transaction, and
why the library must accept a caller-owned transaction rather than open its
own. Also what the inbox does not solve: side effects outside the database.
Shows the consumer code and the duplicate-delivery test. Closes on omni-box.

### 17. Circuit breakers should be per origin, not per client

One HTTP client, three origins, one of them dead: a breaker keyed on the
client opens for all three and the healthy two go dark. The post keys the
breaker on the origin, then works through half-open probes, what counts as a
failure (5xx, timeouts, 429 and connection errors are not the same), and how
breaker state should survive a client migration. Shows the failure scenario
reproduced against three local servers. Closes on clientwright.

### 18. Retry-After, backoff and jitter: what a production HTTP client actually does

A checklist post. Honour `Retry-After`, exponential backoff with full jitter
and a cap, retry only idempotent methods, treat 429 and 503 differently, and
treat a connection error differently from a read timeout because the request
may have been received. Measures a naive retry loop against the checklist
version on a deliberately flaky server: total time, duplicate requests,
thundering herd. Closes on clientwright.

### 19. Why application lifecycle should not belong to FastAPI

The opinion piece. Lifespan events tie the application's startup and
shutdown to the HTTP framework, and the worker and the cron job have no
FastAPI to hang them on, so they grow their own. The framework is an
entrypoint; the runtime is the host; startup order, warmup, readiness and
drain belong to the host. Shows the same service twice, lifecycle in
FastAPI and lifecycle in a host, and the diff when a worker is added.
Closes on servicewright. Expect disagreement; that is the point.

### 20. gRPC channels should not be pooled by address alone

Two callers ask for a channel to the same address with different
credentials, options or interceptors, and a pool keyed on the address hands
them the same one. The post defines channel identity as the full tuple,
shows the bug this prevents, and covers health monitoring of pooled channels
and when a pooled channel should be evicted. Closes on grpc-client-kit.

### 21. The Unit of Work pattern in SQLAlchemy 2

Before and after code. The use case owns the transaction boundary; the
repositories work inside it; commit happens once; rollback happens on any
exception; the async version is the same shape. Covers what goes wrong when
repositories commit for themselves and how to test a use case with a fake
unit of work. Closes on sqlalchemy-foundation-kit.

### 22. When should Redis fail open?

Redis is down and it is your idempotency store. Reject every write, or accept
the duplicates? The post argues the answer is per use, not per client: a
cache fails open, a rate limiter fails open with an alert, an idempotency
store depends on what the operation costs to repeat. Covers the client
timeouts that make fail-open possible and how Redis health feeds readiness
without taking the whole service down. Closes on redis-client-kit and
idempotency-kit together.

### 23. AI code review should not be fully autonomous

Why every comment the reviewer writes passes a human before it is posted.
The failure modes of autonomous bots: noise, confident nonsense, reviewer
fatigue, and the maintainer who stops reading. The pipeline brief, review,
human polish, post, and what the polish step actually changes, with real
examples of comments that were dropped. Closes on mr-review.

### 24. What happens when Kafka is down for an hour?

The operational post for the outbox. The backlog grows, the relay retries,
ordering holds, and then Kafka returns and the relay drains an hour of
events in a burst the consumers were not sized for. Covers sizing the outbox
table, monitoring the oldest unpublished record, draining at a controlled
rate, and keeping the outbox table itself from becoming the problem, which
is where partitioning it comes in. Closes on omni-box, with a pointer to
pg-partsmith for the table.

### 25. How to partition an existing PostgreSQL table without rewriting your application

The migration nobody wants: a live table into a partitioned one. Create the
partitioned table, move rows in batches, swap under a short lock; the
primary key must include the partition column, foreign keys pointing at the
table need rethinking, and indexes are per partition. Every step with the
lock it takes and how long it held on a table of a stated size. Closes on
pg-partsmith taking over after the swap.

### 26. The production checklist for aiokafka

Producer lifecycle and idempotent producer settings, acks and linger;
consumer group rebalance handling, commit strategy, max poll interval and
what happens when processing exceeds it; serialization at the boundary;
health checks; trace headers; shutdown. Each item with the failure it
prevents. Closes on aiokafka-foundation-kit.

### 27. Your models and your schema have drifted. Would CI notice?

Drift arrives through hand-edited migrations, hotfixes applied on production
and the limits of autogenerate. The post runs autogenerate against a
database migrated to head and treats any output as a failure, then lists
what autogenerate cannot see (server defaults, some constraint changes,
enums) and how to cover those. Closes on alembic-gauntlet's drift check.

### 28. The anatomy of a production Python gRPC server

Checklist post for `grpc.aio`: TLS and mTLS, the health service, interceptors
for auth, logging, metrics and tracing, error mapping, keepalive, message
size limits, graceful shutdown with a deadline. Each item with the incident
it prevents. Closes on grpc-server-kit.

### 29. Stop passing AsyncSession everywhere

A session threaded as a parameter through five layers is a resource with no
owner. The post argues sessions are resources scoped to a request or a job,
handed out by the container, with the transaction owned by the use case, and
shows what the code looks like when repositories receive a session from the
unit of work rather than from the caller. Closes on
sqlalchemy-foundation-kit's DI integration.

### 30. Idempotency for background jobs and Kafka consumers

Idempotency beyond HTTP: the message key or the job id as the idempotency
key, redelivery after a crash, result caching for jobs, TTL against
retention. Also when a consumer needs both an inbox and an idempotency
store, and when one is enough. Shows a consumer that survives a redelivery
and a job runner that survives a restart. Closes on idempotency-kit.

### 31. Partition retention is not DROP TABLE

A retention cron that drops the oldest partition is one line, and it is the
line that took a table it did not create. The post separates detach from
drop, adds archive-before-drop as a hook, checks ownership before anything
destructive, and puts a plan phase in front of it all. Closes on
pg-partsmith, referring back to the existing pg-partsmith post for the
design.

### 32. Graceful Kafka consumer shutdown in Kubernetes

SIGTERM arrives mid-batch. Finish the batch or abandon it, commit offsets or
not, leave the group cleanly so the rebalance is cheap, and fit all of it in
`terminationGracePeriodSeconds`. A timeline post with the numbers measured
on a consumer of a stated batch size. Closes on aiokafka-foundation-kit
under a servicewright lifecycle.

### 33. Why gRPC interceptors break on streaming RPCs

A unary interceptor wraps one call; a streaming RPC is an iterator, and the
wrapper that worked for unary silently measures the wrong thing, catches the
wrong exceptions and leaks the wrong context. The post shows the broken
version and the streaming-aware version for logging, metrics and error
mapping. Closes on grpc-server-kit and grpc-client-kit.

### 34. What to monitor in a SQLAlchemy connection pool

The metrics: connections checked out, overflow in use, checkout wait time,
checkouts per request, connection age. Which alert fires first before an
outage (checkout wait), which are noise, and what the dashboard looks like
during a deploy. Closes on sqlalchemy-foundation-kit's pool metrics.

### 35. Redis health checks: PING is not the whole story

PING answers while the cluster has uncovered slots, a replica is an hour
behind, or p99 latency is a second. The post defines a health check that
reads and writes, checks slot coverage on a cluster, and reports latency,
and argues what readiness should and should not depend on. Closes on
redis-client-kit's health check.

### 36. Can local LLMs review production code? Fifty real bugs, four models

The experiment. Fifty bugs taken from merged pull requests across the
Bedrock repositories, each reintroduced into a branch; four models (two
hosted, two local) review each; recall, false positives, cost and wall time
per model. Methodology first, results table second, what the local models
missed third. Closes on mr-review as the harness. Budget: this post is the
most expensive to produce and needs its own budget.

### 37. Warmup, readiness and liveness are three different things

Three definitions and the mistake each conflation causes: liveness that
checks the database restarts the pod during a database outage; readiness
that never flips during drain sends traffic to a pod that is leaving; warmup
folded into readiness serves cold caches. Shows the three probes as three
separate things in one lifecycle. Closes on servicewright.

### 38. Transport-independent errors: one domain error, HTTP and gRPC responses

A domain raises `NotFound`; the HTTP entrypoint answers 404; the gRPC
entrypoint answers `NOT_FOUND`; neither handler knows about the other. The
mapping table, error details that are safe to return, what stays in the log,
and how the mapping is tested once for both transports. Closes on
servicewright with grpc-server-kit.

### 39. Migrating from pg_partman to application-managed partitions

Why teams leave pg_partman: managed PostgreSQL without the extension, a
Python team that wants the logic in the application, a need to see the plan
before it runs. The post maps a pg_partman configuration onto a
pg-partsmith one, adopts the existing partitions without recreating them,
and runs both side by side during the transition. Closes on pg-partsmith.

### 40. Idempotency across a chain of microservices

The edge has an idempotency key; the third service down the chain does not.
The post propagates the key hop by hop with the same discipline as a
deadline, derives child keys for fan-out, and separates retries at the edge
from retries inside the chain. Shows the header contract and a chain of
three services surviving a retry at each hop. Closes on idempotency-kit and
deadline-budget as the same idea twice.

### 41. Should your application create Kafka topics on startup?

The convenience in development becomes configuration drift in production:
partition counts, retention and permissions set by whichever service started
first. The post lands on a policy, create in development, verify in
production and fail readiness if a topic is missing or misconfigured, and
shows the startup check. Closes on aiokafka-foundation-kit's topic
management.

### 42. Why enterprise AI answers need citations

An answer without a link is an answer nobody can verify, act on or challenge,
and inside a company that is the difference between an assistant and a
rumour. The post shows how a citation is produced from a search hit and a
permalink, what happens to trust when it is missing, and how permissions
follow the citation. Closes on mattermind.

### 43. Mapping Python exceptions to gRPC status codes without leaking internals

Validation to `INVALID_ARGUMENT`, missing to `NOT_FOUND`, everything unknown
to `INTERNAL` with a correlation id and nothing else. The mapping table, the
interceptor that applies it, and the test that proves a stack trace never
crosses the wire. Closes on grpc-server-kit.

### 44. UUIDv7 as a PostgreSQL partition key

Time-ordered UUIDs make range partitioning on an id column possible: the
bounds are computed from timestamps, the primary key already contains the
partition column, and there is no separate `created_at` to keep in step.
The pitfalls: clock skew, backfilled old data, ids generated off-host.
Shows the bound computation and a partitioned table keyed on it. Closes on
pg-partsmith.

### 45. Publishing to PyPI without API tokens: Trusted Publishing end to end

OIDC between GitHub Actions and PyPI, the environment that gates it, the
release workflow from a Release Please tag to a published wheel, and the
manual dispatch for the day something goes wrong. Every step as it runs in
a Bedrock repository. Closes on python-library-template.

### 46. Zero-dependency cores: why optional dependencies matter in infrastructure libraries

`pip install servicewright` pulls nothing. FastAPI, gRPC and OpenTelemetry
are extras; the core talks to them through protocols; import-linter
contracts keep it that way. The post argues why an infrastructure library
that drags in a framework is a liability, and shows the seams. Closes on
the Bedrock convention with servicewright as the example.

### 47. Reliability is not `retry=3`

The capstone of the reliability series. Deadline, timeout, retry, circuit
breaker and idempotency are five different problems solved at five
different layers, and `retry=3` addresses none of them well. One diagram of
the request path with each concern in its layer, one paragraph per layer
linking to the earlier posts, and the composition in code. Closes on
deadline-budget, clientwright, grpc-client-kit and idempotency-kit together.

### 48. How I start a production-grade Python library in 2026

The template walkthrough: uv, hatchling, Ruff, mypy strict, pytest, Release
Please, Trusted Publishing, GitHub settings as code, docs with an agents
page, all from one Copier command. What each choice replaced and why.
Closes on python-library-template and the year of posts behind it.

## Reserve

Topics with material but no slot. They replace a scheduled post when
something more timely comes up, or extend the plan past post 48.

- servicewright: designing a microservice runtime without becoming a framework; the readiness probe as part of the deployment algorithm.
- clientwright: the hidden cost of an internal HTTP wrapper; observability that survives a client migration; PII masking without losing observability; when an abstraction cannot support a feature, fail loudly.
- deadline-budget: latency budgets, designing APIs backwards from the SLO.
- grpc-client-kit: client-side load balancing without shared breaker state; an unchecked backend is not a healthy backend; the anatomy of a production gRPC client.
- grpc-server-kit: gRPC health checking against Kubernetes readiness; TLS against mTLS for internal services.
- sqlalchemy-foundation-kit: who should own the transaction; the 300 lines every SQLAlchemy microservice reimplements; closing pools during deployments.
- redis-client-kit: cluster changes more than the connection string; sync and async without two configuration systems; should you wrap redis-py at all.
- aiokafka-foundation-kit: tracing an event across Kafka with OpenTelemetry; Kafka configuration as infrastructure API.
- idempotency-kit: Stripe-style keys explained; idempotency against deduplication against exactly-once; what happens when the store goes down (folded into 22 unless it needs its own post).
- omni-box: why an outbox library should not own your transaction; designing an extensible processing pipeline; commit against publish, every failure window (folded into 6).
- alembic-gauntlet: `alembic upgrade head` is not a test; how migration branches reach production; naming conventions matter more than they look.
- pg-partsmith: RANGE plus HASH for multi-tenant data; maintenance as a Kubernetes CronJob; backfilling a partitioned table safely; desired-state management for partitions; why a partition manager reads bounds, not names.
- mr-review: self-hosted architecture and trade-offs; one review UI for five forges; what context to send the model.
- mattermind: search first, embed later as an enterprise RAG architecture; query expansion for bilingual teams; tool calling against RAG; a CLI assistant over Mattermost.
- python-library-template: what every open-source repository should configure on GitHub; Copier against copy-paste; documentation as an API for agents (folded into 7).
- Cross-cutting: effectively-once business operations in an at-least-once world (the capstone of that series, if 6 and 16 leave room for it).
