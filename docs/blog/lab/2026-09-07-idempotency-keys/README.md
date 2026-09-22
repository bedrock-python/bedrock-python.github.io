# Lab: idempotency keys {#lab-idempotency-keys}

The script starts Redis 7 in a disposable Docker container. A local payment-provider fixture counts effects; no external payment service is used.

It asserts the three in-flight modes, completed-result replay, parameter mismatch, tenant separation, and rejection of invalid keys before an action runs. Concurrency uses events to hold the first action until the second reaches the coordinator.

Further checks lose a response after the provider's effect, expire a lease while its owner is still running, expire a completed result, and make Redis unreachable. Expected effects: `run=2`, `wait=1`, `raise=1`; a lost provider response gives two effects without provider deduplication and one with it. An expired lease and unavailable Redis both permit duplicate effects.

The normal result TTL is asserted to be one hour. Only the disposable test record is then shortened with `PEXPIRE` to avoid a one-hour wait. The provider failure is a raised exception after an effect, not an actual process crash. Logs for expected library errors are suppressed; assertions verify their consequences.

Requires Docker and `uv`. Run from `docs/blog/lab/2026-09-07-idempotency-keys`:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python measure.py
```

Dependencies are pinned in `requirements.txt`: idempotency-kit 0.4.1, redis-py 8.1.0, Pydantic 2.13.5, testcontainers 4.15.0, HTTPX 0.28.1 and aiohttp 3.14.3.

Article snippets come from `payment_flow.py`; `lab_support.py` provides fixtures and container management.

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-idempotency-keys).
