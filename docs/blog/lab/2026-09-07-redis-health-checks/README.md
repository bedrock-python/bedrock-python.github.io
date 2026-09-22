# Lab: Redis health checks, PING is not the whole story

Docker must be running. The script creates three `redis:7-alpine` containers:
a healthy primary, a primary whose memory limit is set below current usage with
`noeviction`, and a read-only replica. It then pauses and resumes the healthy primary.

Run from this directory in a checkout of the repository. The lab imports the article's
functions and test doubles from the neighboring `2026-09-07-when-should-redis-fail-open`
directory, so keep both directories:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt health_lab.py
```

Dependencies are pinned to redis-client-kit 0.3.0, redis-py 8.1.0 and testcontainers 4.15.0.
The script prints the Redis server version (7.4.11 in the checked run).

It verifies that PING succeeds while writes fail on the read-only and memory-limited
servers. The kit's `write_key` probe performs PING followed by SET with a 60-second TTL;
it does not read the value back. The lab separately verifies the written value and TTL.

The same shop functions must return a database price despite a failed cache write,
refuse login and payment, and make no charge while writes are rejected. Removing
the memory limit and unpausing Redis must restore health with the same clients.
Assertions check these outcomes; a successful run ends with `PASS: Redis health scenarios`.
