# Lab: idempotency for background jobs and consumers {#lab-idempotency-for-background-jobs-and-consumers}

Redis 7 runs in a disposable container. Queue redelivery is modeled in memory, and a local mail provider counts sends: this lab starts neither Kafka nor an SMTP server.

Acknowledgement fails after the first action and its result have been stored. The same invoice arrives with a new delivery ID. Assertions verify two deliveries and one successful ACK: without coordination there are two emails, with it there is one and the saved email ID is returned.

The key identifies tenant, order and invoice version. A new version sends another email; changing the recipient of an existing version raises `IdempotencyKeyReuseError`. The failure is injected at ACK, not by killing an OS process. The separate keys lab covers a failure before result storage and concurrent callers.

Requires Docker and `uv`. Run from `docs/blog/lab/2026-09-07-idempotency-for-jobs-and-consumers`:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python jobs_lab.py
```

Dependencies are pinned in `requirements.txt`: idempotency-kit 0.4.1, redis-py 8.1.0, Pydantic 2.13.5, testcontainers 4.15.0, HTTPX 0.28.1 and aiohttp 3.14.3.

Keep the sibling `2026-09-07-idempotency-keys` directory: this lab imports its shared code and requirements.

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-idempotency-for-jobs-and-consumers).
