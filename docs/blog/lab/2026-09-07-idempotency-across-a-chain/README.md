# Lab: idempotency across a chain of services {#lab-idempotency-across-a-chain-of-services}

The gateway is an HTTP client driving two local aiohttp servers, orders and payments. Redis 7 runs in a disposable container; a local provider counts charges. No external payment service is used.

The first payments response is lost after both the charge and its completed Redis record exist. The first orders response is also lost. Connections close deliberately rather than relying on a slow request to imply a successful charge.

Each design makes two calls to orders and three to payments. Assertions verify three charges without a coordinator, two when the gateway creates a new key on retry, and one when the key remains stable. A changed amount then gets HTTP 409, and a key containing a colon gets HTTP 400 before another charge.

This is a transport and idempotency lab. It has no authentication middleware: tenant IDs in its generated requests are trusted fixture data. A real API obtains tenant identity from authenticated context and authorizes access to the order.

Requires Docker and `uv`. Run from `docs/blog/lab/2026-09-07-idempotency-across-a-chain`:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python chain_lab.py
```

Dependencies are pinned in `requirements.txt`: idempotency-kit 0.4.1, redis-py 8.1.0, Pydantic 2.13.5, testcontainers 4.15.0, HTTPX 0.28.1 and aiohttp 3.14.3.

Keep the sibling `2026-09-07-idempotency-keys` directory: this lab imports its shared code and requirements.

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-idempotency-across-a-chain).
