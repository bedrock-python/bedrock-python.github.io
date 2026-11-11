---
title: For AI agents
description: An index of the Bedrock Python repositories for coding assistants. What each library and tool is for, when to take it, and where its own page for agents is.
copy_page: true
---

# Bedrock Python for AI agents

> An index of every Bedrock Python repository for a coding assistant that builds a
> production async Python service: what each library and tool is for, when to take it, and
> where its own page for agents is. Give an agent this page first. It picks the libraries
> here and reads their pages for the API.

## How to read this page

Every library has a one-page reference for assistants at
`https://bedrock-python.github.io/<repo>/agents/`, with raw Markdown at
`https://bedrock-python.github.io/<repo>/agents.md`. This page is raw Markdown at
`https://bedrock-python.github.io/agents.md`.

This page has no API and no code. It says which repository solves which problem and how
the libraries meet in one service. Before writing code against a library, fetch its agent
page: the names, signatures and rules are there.

## What to take for which need

Take only what the service needs. A service on this stack needs Python 3.12 or newer.

| The service needs | Take |
|---|---|
| One process lifecycle for HTTP, gRPC, cron, daemons and one-shot jobs | [servicewright](#servicewright) |
| PostgreSQL through async SQLAlchemy | [sqlalchemy-foundation-kit](#sqlalchemy-foundation-kit) |
| Alembic migrations tested before production | [alembic-gauntlet](#alembic-gauntlet) |
| Events sent exactly when the transaction commits, messages handled once | [omni-box](#omni-box) |
| A retried request must not run twice | [idempotency-kit](#idempotency-kit) |
| Tables partitioned by time | [pg-partsmith](#pg-partsmith) |
| Redis | [redis-client-kit](#redis-client-kit) |
| Kafka | [aiokafka-foundation-kit](#aiokafka-foundation-kit) |
| Outbound HTTP calls | [clientwright](#clientwright) |
| A gRPC server | [servicewright](#servicewright) with [grpc-server-kit](#grpc-server-kit) |
| A gRPC client | [grpc-client-kit](#grpc-client-kit) |
| One time budget per request across downstream calls | [deadline-budget](#deadline-budget) |
| The same agent instructions and CI files in every repository | [touchmark](#touchmark) with [engineering-assets-template](#engineering-assets-template) |
| A new library of your own | [python-library-template](#python-library-template) |
| Code review by a model | [mr-review](#mr-review) |

## The runtime

### servicewright

The base of every service. It runs one process through one lifecycle: startup, warmup,
readiness, serving, drain, cleanup. One description of the service runs with any list of
entrypoints: a FastAPI or Litestar app, a gRPC server, a cron scheduler, a daemon loop, a
one-shot job. That is how an API and its worker stay one codebase and one image. It owns
signals, health probes, graceful shutdown and the setup of logs, metrics, tracing and
error tracking. It brings no DI container and no business logic; dishka plugs in through
an adapter.

Take it for every service. Start with it: the other libraries plug into its container and
lifecycle.

Pages: [for agents](https://bedrock-python.github.io/servicewright/agents/) ·
[project layout](https://bedrock-python.github.io/servicewright/blueprints/project-layout/) ·
[HTTP API blueprint](https://bedrock-python.github.io/servicewright/blueprints/http-api/) ·
[worker blueprint](https://bedrock-python.github.io/servicewright/blueprints/worker/)

## Data

### sqlalchemy-foundation-kit

The PostgreSQL layer a service would otherwise write itself: an async engine and session
manager with pooling and PgBouncer-safe settings, a Unit of Work, savepoints, advisory
locks, pool metrics, and a declarative `Base` with a naming convention for constraints.

Take it when the service uses SQLAlchemy with PostgreSQL over asyncpg. It has no
repositories, no migrations and no sync API.

Page: [for agents](https://bedrock-python.github.io/sqlalchemy-foundation-kit/agents/)

### alembic-gauntlet

A pytest toolkit that runs the real Alembic history against a real PostgreSQL in a
throwaway schema. One inherited test class gives seven tests: every migration up and down
step by step, the result compared with the ORM models, constraint names, enum values, a
single head.

Take it as a dev dependency when the service has Alembic migrations. It does not run
migrations in production.

Page: [for agents](https://bedrock-python.github.io/alembic-gauntlet/agents/)

### omni-box

Transactional outbox and inbox. Outbox: the event row is written in the same transaction
as the business state, and a relay sends it to the broker later. Inbox: incoming messages
are deduplicated and the handler runs in the same transaction as the inbox row.

Take it when an event must not be lost or sent without its database change, or when a
consumer must not handle a message twice. It owns no transaction, no migrations and no
scheduler: the tables go into your migrations and the relay loop into your worker.

Page: [for agents](https://bedrock-python.github.io/omni-box/agents/)

### idempotency-kit

Caches the result of an operation under a key the caller sends and replays it on a
repeat. It holds the key while the first call runs and can refuse a key reused with a
different request body. State lives in Redis.

Take it for HTTP or gRPC writes that clients retry: payments, order creation. It is not a
distributed lock or a transaction.

Page: [for agents](https://bedrock-python.github.io/idempotency-kit/agents/)

### pg-partsmith

Keeps a time-partitioned PostgreSQL table in its declared shape: creates partitions
ahead, detaches expired ones and drops them after a grace period, with a plan you can
inspect first. A library and a CLI, also shipped as a container image.

Take it when a table is partitioned by time: events, logs, an outbox with retention. The
parent table and its indexes stay in your migrations, and the schedule is yours: call it
from a scheduled job or a Kubernetes CronJob.

Page: [for agents](https://bedrock-python.github.io/pg-partsmith/agents/)

### redis-client-kit

Builds a configured redis-py client, single node or cluster, from one settings object,
with metrics, a health check and a clean close. The client it returns is plain redis-py.

Take it whenever the service talks to Redis. It adds no caching, locks or key prefixing.

Page: [for agents](https://bedrock-python.github.io/redis-client-kit/agents/)

## Messaging and calls to other services

### aiokafka-foundation-kit

Builds aiokafka producers and consumers from settings and manages their start and stop.
It also creates topics and probes cluster health.

Take it when the service produces to or consumes from Kafka. It has no consumer loop,
retries or dead-letter topic: the loop is a servicewright entrypoint you write, and
once-only handling is the omni-box inbox.

Page: [for agents](https://bedrock-python.github.io/aiokafka-foundation-kit/agents/)

### clientwright

Builds the native HTTP client you already use (httpx, aiohttp, requests, urllib3) with
one engine underneath: a total deadline, retries with a budget, a circuit breaker, header
injection, metrics and tracing.

Take it for every outbound HTTP call. Do not add a second retry layer on top.

Page: [for agents](https://bedrock-python.github.io/clientwright/agents/)

### grpc-server-kit

Everything around an async gRPC server except your servicers: validated options, TLS,
graceful shutdown, interceptors that understand streaming, the standard health service.

Do not start with it in a service: servicewright's `grpc` extra is built on it and puts
the server under the same lifecycle as everything else. Read its page for interceptors,
TLS and server settings.

Page: [for agents](https://bedrock-python.github.io/grpc-server-kit/agents/)

### grpc-client-kit

The calling side of gRPC: a channel pool, health-gated target selection, and one
interceptor chain with timeouts, retries, a circuit breaker, metrics and tracing for all
four RPC kinds.

Take it for every outbound gRPC call. Async only.

Page: [for agents](https://bedrock-python.github.io/grpc-client-kit/agents/)

### deadline-budget

Arithmetic on one countdown per request: how many seconds the next downstream call may
take, given what is left, per-call caps and a reserve for the response.

Take it when one request makes several downstream calls and must fit a total time. It
enforces nothing by itself: clientwright and grpc-client-kit apply the budget through
their `deadline` extra.

Page: [for agents](https://bedrock-python.github.io/deadline-budget/agents/)

## Tools and repository standards

### touchmark

Keeps shared files in sync across many repositories through pull requests, and never
overwrites a file a team has changed. It is the engine behind an engineering-assets hub.
Works on GitHub, GitLab, Gitea, Forgejo, Bitbucket and Azure DevOps.

Take it when several repositories must carry the same `AGENTS.md`, guidelines, review
prompts or CI files.

Page: [for agents](https://bedrock-python.github.io/touchmark/agents/)

### engineering-assets-template

The template for your own hub: a repository with packs of shared files and a list of
target repositories. For a service, its packs are `agents` (`AGENTS.md`, a project
profile, review prompts), `python-service` (Python, testing and database guidelines,
skills to run and test the service) and `claude` (Claude Code instructions, settings, a
reviewer subagent).

Take it once per organisation. A service repository then opts in with an
`.engineering-assets.yml` file and fills in `.agents/project.md`, which stays its own.

Repository: [engineering-assets-template](https://github.com/bedrock-python/engineering-assets-template)

### engineering-assets

The Bedrock Python organisation's own hub, made from the template. It delivers the docs
site assets, community files and agent instructions to every library here. Read it as a
working example of a hub; it does not deliver to repositories outside the organisation.

Repository: [engineering-assets](https://github.com/bedrock-python/engineering-assets)

### python-library-template

A Copier template for a new Python library with the organisation's layout: uv, ruff,
mypy, tests, a docs site with a page for agents, release automation.

Take it when you extract shared code into a library of your own. Not for services.

Repository: [python-library-template](https://github.com/bedrock-python/python-library-template)

### mr-review

A self-hosted tool that reviews merge requests with a language model. It connects to
GitLab, GitHub, Gitea, Forgejo or Bitbucket and works with Claude, OpenAI or any
OpenAI-compatible model.

Page: [for agents](https://bedrock-python.github.io/mr-review/agents/)

### mattermind

Answers natural-language questions about a Mattermost workspace with a model that calls
tools. Not part of a service's stack.

Page: [for agents](https://bedrock-python.github.io/mattermind/agents/)

## Order of assembly

1. **Skeleton.** servicewright with its project layout: settings, a dishka container, one
   service description, a main per process (`api_main`, `worker_main`).
2. **Database.** sqlalchemy-foundation-kit for sessions and the Unit of Work; models on
   its `Base`.
3. **Migrations.** Alembic, with alembic-gauntlet in the test suite from the first
   migration.
4. **Writes that clients retry.** redis-client-kit for the client, idempotency-kit on top.
5. **Events.** omni-box outbox in the write path, a relay in the worker,
   aiokafka-foundation-kit for the producer; the omni-box inbox for consumers.
6. **Calls to other services.** clientwright for HTTP, grpc-client-kit for gRPC,
   deadline-budget when one request makes several of them.
7. **Operations.** Health checks and metrics for every process through servicewright;
   pg-partsmith for partitioned tables.
8. **Repository.** Agent instructions and guidelines from your engineering-assets hub.

## Where the libraries meet

Facts that no single library page states. They were checked by assembling one service
from the released libraries and running it against PostgreSQL, Redis and Kafka.

- servicewright owns the process and the dishka container. Every other library gives a
  dishka provider or a client built once per process. Nothing is built per request or at
  import time.
- Each library asks for its settings by its own protocol type. One provider in the
  service hands each library its section of the settings.
- sqlalchemy-foundation-kit's database provider also asks for
  `PostgresMetricsProtocol | None`. Provide it even when metrics are off, or the
  container does not build.
- idempotency-kit's Redis provider takes exactly the client redis-client-kit's provider
  gives. No glue is needed.
- omni-box does not use the Unit of Work. Pass its repository the session of the current
  transaction, so the event commits with the business change.
- omni-box's tables go into your Alembic metadata and migrations. Their indexes are named
  `idx_...`, while sqlalchemy-foundation-kit's convention ends names with `_idx`: allow
  the `idx_` prefix in alembic-gauntlet's naming test.
- In Alembic's `env.py`, pass `version_table_schema` only for a schema other than
  `public`. An explicit `public` makes autogenerate add a drop of `alembic_version`.
- servicewright's Postgres and Redis health checks accept the session maker and the
  client the two kits build.
- clientwright and grpc-client-kit each keep the request budget in a context of their
  own. A service that uses both installs the budget in both.
- The scheduler in servicewright is in-process. Run it at one replica.
- APScheduler 4 has only pre-releases, which pip and uv skip by default. The
  `apscheduler3` extra installs without flags.

## Pages for agents

| Repository | Page |
|---|---|
| servicewright | <https://bedrock-python.github.io/servicewright/agents.md> |
| sqlalchemy-foundation-kit | <https://bedrock-python.github.io/sqlalchemy-foundation-kit/agents.md> |
| alembic-gauntlet | <https://bedrock-python.github.io/alembic-gauntlet/agents.md> |
| omni-box | <https://bedrock-python.github.io/omni-box/agents.md> |
| idempotency-kit | <https://bedrock-python.github.io/idempotency-kit/agents.md> |
| pg-partsmith | <https://bedrock-python.github.io/pg-partsmith/agents.md> |
| redis-client-kit | <https://bedrock-python.github.io/redis-client-kit/agents.md> |
| aiokafka-foundation-kit | <https://bedrock-python.github.io/aiokafka-foundation-kit/agents.md> |
| clientwright | <https://bedrock-python.github.io/clientwright/agents.md> |
| grpc-server-kit | <https://bedrock-python.github.io/grpc-server-kit/agents.md> |
| grpc-client-kit | <https://bedrock-python.github.io/grpc-client-kit/agents.md> |
| deadline-budget | <https://bedrock-python.github.io/deadline-budget/agents.md> |
| touchmark | <https://bedrock-python.github.io/touchmark/agents.md> |
| mr-review | <https://bedrock-python.github.io/mr-review/agents.md> |
| mattermind | <https://bedrock-python.github.io/mattermind/agents.md> |
