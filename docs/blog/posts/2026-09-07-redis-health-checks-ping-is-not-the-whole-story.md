---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - redis-client-kit
  - redis
  - health-checks
  - kubernetes
  - asyncio
---

# Redis health checks: PING is not the whole story

A health check that answers `True` for a server that cannot take a write is worse than no health check, because something acts on it. I started three Redis servers: a healthy one, one that had filled its memory limit with eviction turned off, and a read-only replica. All three answered `PONG`. Two of them fail every `SET` the application makes. Readiness stayed green, the pods kept taking traffic, and the only thing that noticed was the code doing the writing.

<!-- more -->

The numbers come from [the post's lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-redis-health-checks), three Redis 7 containers on one network. Versions: redis-client-kit 0.2.0, redis-py 8.1.0, Python 3.13.

## What PING answers

```text
  primary                          PING health=True  (  2.5 ms)   a plain SET: ok
  maxmemory 1mb, noeviction, full  PING health=True  (  0.2 ms)   a plain SET: OutOfMemoryError:
                                                                  command not allowed when used memory > 'maxmemory'
  replica of the primary           PING health=True  (  5.5 ms)   a plain SET: ReadOnlyError:
                                                                  You can't write against a read only replica
  paused primary                   PING health=False (501.8 ms)
```

`PING` is a liveness answer. It says a process is running, its event loop is turning and the socket works. Three of those four servers pass it, and only one of them can serve.

The middle two are not exotic failures. A Redis at its `maxmemory` limit with `noeviction` is the configuration you choose deliberately when the data matters — an idempotency store, a lock, a queue — precisely so that Redis refuses writes instead of quietly dropping keys. It does refuse them, and it refuses every one until somebody frees memory. A read-only replica is what a client reaches after a failover that did not fully complete, or when a DNS record or a Sentinel-aware client points at the wrong node. Both are the "Redis is up and my service is down" incident, and both report healthy.

The last line is what a check catching a dead server looks like: `False`, decided in half a second, which is the socket timeout doing its job. That is the case people design health checks for, and it is the easy one.

## Liveness and readiness are different questions

Kubernetes makes the distinction explicit and then invites you to answer both with the same handler. They are not the same question.

**Liveness** asks whether this process should be killed and restarted. For a dependency, the honest answer is almost always yes-it-is-alive: restarting my pod does not fix a full Redis, and a liveness probe that goes red on a dependency turns one broken dependency into a restart loop across every replica, at the worst possible moment. Dependencies do not belong in liveness probes.

**Readiness** asks whether this pod should receive traffic right now. That is where a dependency check belongs, and it is where `PING` gives the wrong answer, because the question readiness is really asking is "can I do my job", and the job involves writes.

So the check needs to be able to do what the application does. The kit's version takes an optional key and, when given one, pings and then writes:

```text
  primary                          write_key health=True  (0.7 ms)
  maxmemory 1mb, noeviction, full  write_key health=False (0.6 ms)
  replica of the primary           write_key health=False (0.8 ms)
  paused primary                   write_key health=False (503.8 ms)
```

Same four servers, and now the answers match reality. The probe is a `SET` with a short expiry on a key of your choosing, and the refusals — `OutOfMemoryError` on the full server, `ReadOnlyError` on the replica — come back as `False` rather than as an exception, the same way a connection failure already did. A health check that raises is a health check that takes the handler down with it.

## What it costs, and what it does not answer

The write probe costs one round trip more than the ping, which the lab measures at well under a millisecond on the same host. That is nothing per check and something per second if you check per request, which you should not: readiness runs on the kubelet's schedule, and a check that a hundred requests trigger a hundred times is a load generator aimed at the thing you are protecting.

It also has real limits, and they should be said out loud rather than discovered.

**One key is one slot.** On a Redis Cluster the probe writes to whichever slot the key hashes to, so it proves that one node can take a write, not that the cluster can. Slot coverage is a different question, answered by asking the cluster whether its state is `ok`.

**A write is a write.** The probe key lands in the same keyspace as the data, counts toward memory, and appears in the replication stream. Give it a short TTL and a name nobody will confuse with real data.

**It does not prove your access pattern works.** A Redis that accepts a two-byte `SET` may still refuse a hundred-kilobyte one when it is close to the limit. The probe is a lower bound on health, not a simulation.

And the default stays `PING`. Not every use of Redis writes: a cache read path that can fall through to the database is healthy on a read-only replica, and marking that pod unready would be the wrong call. The deeper probe is opt-in per caller, which is the same shape as the argument in [the fail-open post](2026-09-07-when-should-redis-fail-open.md): the client owes you a fast, honest answer, and what to do about it belongs to the use.

## The rule

A health check should answer the question the caller is actually asking, and the caller is asking about the operation it performs, not about the socket. If the service writes to Redis on the request path, its readiness check has to write. If it only reads, `PING` is the right check and the replica is fine.

The general form of this is worth keeping: **a check that never fails is not a check.** If a dependency probe has been green for a year, it is worth breaking the dependency in a lab and watching whether the probe notices. A full Redis with `noeviction` is one `docker run --maxmemory 1mb` away, and a read-only replica is one `--replicaof`. Both took about ten lines in the lab, and both would have gone unnoticed in production.

## The pieces

The check is [redis-client-kit](https://bedrock-python.github.io/redis-client-kit/): one function for a sync client and one for async, both returning `True` or `False` and never raising, both deciding inside the socket timeout, and both taking an optional key that turns the ping into a ping plus a write. The rest of the kit is the client itself, built from a settings object with explicit socket timeouts and an explicit retry policy.

Three servers answered `PONG`. Two of them could not have taken a single write.
