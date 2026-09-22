# Lab: when should Redis fail open?

Runnable scenarios from [the article](../../posts/2026-09-13-redis-failures-and-health-checks.md).
Docker must be running. The scripts create and remove their own Redis containers;
they do not connect to an existing database or payment provider. Run from this directory
in a checkout of the repository:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt retry_probe.py
uv run --no-project --python 3.13 --with-requirements requirements.txt fail_open_lab.py
```

Python dependencies are pinned in `requirements.txt`: redis-client-kit 0.3.0,
redis-py 8.1.0 and testcontainers 4.15.0. The Redis image is `redis:7-alpine`;
the scripts print the server version (7.4.11 in the checked run).

`shop.py` contains the functions printed in both editions of the article.
`fail_open_lab.py` supplies a counted price lookup and an in-memory idempotent
payment provider. These test doubles make fallback reads and charges observable;
they do not verify a real PostgreSQL or payment integration.

The lab asserts cache reuse and fallback, concurrent login limits and expiry,
concurrent payment admission, retries after a lost payment response, cancellation,
database capacity limits, refused connections, a paused Redis, pool exhaustion
and recovery with the same client. Only the payment provider's modeled idempotency
contract prevents another charge after the Redis admission key expires. The lab
shortens selected key TTLs to avoid waiting for full windows.

`retry_probe.py` compares an attempt without retries, two retries without a total
limit, and those retries inside a 0.15-second total limit. Pausing a container stalls
command responses even on established connections. A separate reserved, non-listening
port checks a connection that cannot be established.

Each script raises on a failed assertion and prints `PASS` on success. Timings vary
with the host and scheduler; the timeout values are example settings, not performance targets.
