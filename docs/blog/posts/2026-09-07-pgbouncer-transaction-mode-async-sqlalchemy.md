---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - sqlalchemy-foundation-kit
  - sqlalchemy
  - pgbouncer
  - postgresql
  - asyncpg
  - connection-pooling
---

# PgBouncer transaction mode and async SQLAlchemy: the production setup nobody documents enough

Your SQLAlchemy configuration works perfectly against PostgreSQL, and then someone puts PgBouncer in front of the database in transaction mode, which is the only mode that solves the problem PgBouncer was installed for, and a class of things that used to be true stop being true. Session settings leak between requests. Prepared statements vanish or collide. The schema you set at connect time is silently not set. None of it shows up in a unit test, because the unit test talks to PostgreSQL. This post measures what transaction pooling takes away, which of the folklore fixes still matter on a current PgBouncer, which one actually breaks the connection, and the configuration that comes out the other end.

<!-- more -->

Everything below was measured with PostgreSQL 17 and PgBouncer 1.25.2 in containers, using [the post's lab scripts](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-pgbouncer-async-sqlalchemy). Versions: SQLAlchemy 2.0.52, asyncpg 0.31.0, sqlalchemy-foundation-kit 0.3.0, Python 3.13.

## What transaction mode takes away

PgBouncer in session mode gives each client its own server connection for the life of the client connection, which saves nothing. In transaction mode a server connection is assigned to a client for the duration of one transaction and goes back to the pool at `COMMIT`, so a thousand application connections can share twenty server connections, which is the point. The price is everything PostgreSQL keeps per *session*, because the session is no longer yours:

- `SET` outside a transaction changes the server connection, not your client, and the next client to borrow that connection inherits it.
- Named prepared statements live on the server connection; the client that prepared them may get a different connection for the next transaction.
- Session-level advisory locks, `LISTEN`, temporary tables, cursors held across transactions: all belong to a connection you will not see again.
- Startup parameters, the settings a client sends when it connects, are PgBouncer's to pass along or not, and it passes along only the handful it knows how to track.

The first one is easy to demonstrate and the one I would show a new team member first. One client connection runs a plain `SET`, outside any transaction, and returns its server connection to a pool of size one. A second client connection then asks:

```text
client A ran SET search_path TO leaked; client B sees search_path = 'leaked'
```

Client B never set anything. It is now reading and writing in a schema it has never heard of, and the bug will reproduce on exactly the requests that happen to land on that server connection. `SET LOCAL` inside a transaction dies with the transaction and is safe; a bare `SET` through a transaction pooler is a bug with a random blast radius.

## The prepared statement error, and when it stopped happening

The error every asyncpg-under-PgBouncer thread on the internet is about looks like this:

```text
asyncpg.exceptions.InvalidSQLStatementNameError: prepared statement "__asyncpg_stmt_333__" does not exist
```

asyncpg prepares every statement by name and caches the name per connection; through a transaction pooler the next transaction lands on a server connection that has never seen that name. The standard fixes are to turn the driver's statement cache off and to give each prepared statement a unique name so two clients cannot collide on one server connection. Here is what happens to twenty clients running twenty distinct statements each, twice, with the driver's defaults:

```text
plain SQLAlchemy + asyncpg, driver defaults (statement cache on)
  direct to PostgreSQL                                                   ok=800  errors=none
  PgBouncer transaction mode, defaults (max_prepared_statements=200)     ok=800  errors=none
  PgBouncer transaction mode, max_prepared_statements=0 (pre-1.22)       ok=484  errors={'DBAPIError': 316}
      first error: prepared statement "__asyncpg_stmt_333__" does not exist
```

Read the middle row twice. On a current PgBouncer, with no client-side configuration at all, the classic failure does not happen. PgBouncer learned to track protocol-level prepared statements in 1.21 and turned the feature on by default in 1.22, in early 2024: it remembers which server connection has which statement and re-prepares behind the client's back. The third row is the same run with that feature forced off, which is the world every blog post about this was written in, and it fails forty per cent of the time.

So the folklore is half right. If your PgBouncer is older than 1.22 or someone set `max_prepared_statements = 0`, the statement cache must be off and the statement names must be unique. If it is current, those settings cost you a little on the wire and buy you a little safety. What they never were is the setting that mattered most.

## The setting that actually breaks the connection

The one that matters is the one that looks harmless: a startup parameter. asyncpg lets you pass `server_settings` at connect time, and a natural thing to put there is `jit=off`, because JIT compilation is a well-known source of latency spikes on short queries, or `search_path=app`, because your tables live in a schema. Both arrive at PgBouncer as startup parameters, and PgBouncer's answer to a startup parameter it does not track is not to pass it along; it is to refuse the connection:

```text
sqlalchemy-foundation-kit 0.2.1, its "pgbouncer-safe" settings
  PgBouncer transaction mode, defaults     ok=0    errors={'ProtocolViolationError': 800}
      first error: unsupported startup parameter: jit
```

Zero connections. That was the previous release of my own library, configured the way its own documentation said was required for PgBouncer, and I found out by running this table. The admin-side workaround, `ignore_startup_parameters = jit,search_path` in PgBouncer's config, makes the connections succeed and does exactly what it says:

```text
                                                        jit    search_path
  direct to PostgreSQL                                  off    app
  PgBouncer, ignore_startup_parameters=jit,search_path  on     "$user", public
```

The parameters are ignored. JIT is on, the schema is the default, and every query lands in `public`. A setting the library accepted, the driver sent, and the database never applied, with no error anywhere. That is the worst kind of configuration: the kind that works in the environment without the pooler.

The rule that comes out of it: through a transaction pooler, nothing that lives on the session can be set from the client. It has to be set where the session is made, `ALTER ROLE app SET search_path = app` and `ALTER ROLE app SET jit = off` on the server, or told to PgBouncer as a parameter to track, or set per transaction with `SET LOCAL` as the first statement inside it. The last form is the only one the application controls, and it is what the fixed library does:

```text
sqlalchemy-foundation-kit 0.3.0
  PgBouncer transaction mode, defaults     ok=800  errors=none
  jit_probe through PgBouncer              jit='on'  search_path='app'
```

`jit` is no longer sent unless you ask for it, and `db_schema` is applied as `set_config('search_path', ..., true)` at the start of every transaction, on an engine event, so it is inside the transaction PgBouncer has pinned to a server connection and it dies with it. The probe shows the schema applied through the pooler and JIT following the server's setting, which is where that decision belongs.

## Pool sizing when there is a pool in front of your pool

Two pools, two sets of limits, and they have to agree:

```text
application     pool_size + max_overflow, per process     x  processes  =  client connections PgBouncer must accept
PgBouncer       max_client_conn                                          >= that number
PgBouncer       default_pool_size, per user/database pair                =  server connections PostgreSQL actually sees
PostgreSQL      max_connections                                          >  sum of every PgBouncer's pools, plus admins
```

The application pool is about concurrency inside one process: how many transactions this process may have open at once. Ten plus twenty overflow is a common default and usually too generous for an async service, where one process handles hundreds of requests but most of them are waiting on something other than the database. PgBouncer's pool is about the database: how many server connections this user gets, which is the number PostgreSQL pays for in memory and lock contention. The whole benefit of the setup is that the first number can be large and the second small, and it evaporates if `default_pool_size` is set to match the application pools.

The lab's server pool was five, shared by twenty clients running eight hundred statements, and nothing waited long enough to notice.

## What to monitor

The metric that predicts trouble is not connections in use. It is how long a request waited to get one. A pool at its limit with zero wait is a pool that is sized right; a pool at half its limit with a rising wait is a pool behind a database that has slowed down. The library exposes the pool's gauges, the wait in front of the pool, and how long each connection is held once it has one, which is the number the wait grows out of:

```text
postgres_db_pool_size                             gauge      what the pool is configured for
postgres_db_pool_checked_out                      gauge      connections in use right now
postgres_db_pool_overflow                         gauge      connections beyond pool_size, in use
postgres_db_connection_checkout_wait_seconds      histogram  how long a caller waited for a connection
postgres_db_connection_held_duration_seconds      histogram  how long it held the connection afterwards
postgres_db_connection_timeouts_total             counter    callers that never got one
```

Alert on the wait and the timeouts, graph the rest; [the pool monitoring post](2026-09-07-what-to-monitor-in-a-sqlalchemy-connection-pool.md) measures what all six do while a pool runs out. On the PgBouncer side, `SHOW POOLS` gives `cl_waiting` and `maxwait`, which are the same two facts one layer down: clients queued for a server connection, and how long the oldest has been queued. If `maxwait` grows while the application's own wait is flat, the bottleneck is `default_pool_size`; if both grow, it is PostgreSQL.

## Closing pools during a rollout

The last place transaction pooling bites is shutdown. A pod that is being replaced still has transactions in flight, and disposing the engine while they run turns each of them into a rolled-back request and a connection PgBouncer sees drop mid-transaction. The order has to be: stop accepting requests, let the in-flight transactions finish, then dispose the engine, with a bound on how long the dispose may take so a hung connection cannot hold the pod past its grace period. The library's session manager disposes under a timeout and never raises from it; the [shutdown post](2026-09-07-graceful-shutdown-is-a-protocol.md) covers the ordering that makes the dispose safe to call.

## The configuration

Everything above, as the engine the service actually builds:

```python
from pydantic import SecretStr
from sqlalchemy_foundation_kit import create_async_session_manager
from sqlalchemy_foundation_kit.contrib.settings import BasePostgresConfig, ConnectionSettings, PoolSettings

config = BasePostgresConfig(
    connection=ConnectionSettings(host="pgbouncer", port=6432, user="app", password=SecretStr("..."), database="app"),
    pool=PoolSettings(size=5, max_overflow=5),    # per process; PgBouncer's default_pool_size is the real limit
    application_name="orders",                    # the one startup parameter PgBouncer tracks and you want
    db_schema="app",                              # applied per transaction, not at connect
)
manager = create_async_session_manager(config)   # statement caches off, unique statement names, no jit, no search_path at startup
```

Three settings survived the measurement: the statement caches at zero and the unique statement names, which are insurance for an older PgBouncer and harmless on a new one; the schema applied inside the transaction; and the application name, which is the one thing worth sending at connect because PgBouncer carries it and `pg_stat_activity` shows it. What did not survive was `jit` as a startup parameter, and I am glad it was a table that told me rather than a rollout.

That configuration is [sqlalchemy-foundation-kit](https://bedrock-python.github.io/sqlalchemy-foundation-kit/guide/configuration/#pgbouncer), whose 0.3.0 is the version that stopped sending the two parameters that PgBouncer refuses. The library existed before this post; the PgBouncer section of its guide exists because of it.
