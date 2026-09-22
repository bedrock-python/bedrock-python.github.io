# Lab: Retry budget and requests received by the server {#lab-retries-can-make-an-outage-worse}

Fifty sequential calls reach an endpoint that always returns 503. With three attempts and `budget_ratio=None`, the server sees 150 requests. With `budget_ratio=0.1`, the verified run produced 64.

The breaker is disabled to isolate the retry budget. A fresh origin starts with ten tokens in clientwright 0.5.0; each subsequent logical call replenishes the bucket by the configured ratio. Assertions check 50 logical-call records, server/attempt counter agreement, initial retry capacity, the upper request bound and a `budget` skip reason. The policy is local to the client runtime, not a cluster-wide quota or an exact per-batch percentage.

This uses the neighbouring [HTTP clients lab](../2026-09-07-why-i-stopped-wrapping-http-clients/README.md). Keep that directory. The example counts real HTTP requests; it does not benchmark a concurrent retry storm.

Run from `docs/blog/lab/2026-09-07-retry-budget` in the repository checkout. Dependencies are pinned in `requirements.txt`.

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python storm_lab.py
```

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-retry-budget).
