# Lab: Retry-After, payment deduplication and request replay {#lab-retry-after-backoff-and-jitter}

The driver asserts a one-second `Retry-After` delay, then checks that a 60-second delay is rejected when only 300 ms is available: the original 503 is returned without another request.

The payment route deliberately fails after recording a charge. A plain POST is not retried. Setting `idempotent=True` without a key records two charges; a stable key and the server's saved response keep the effect count at one, including a later repeated call.

It also checks that the HTTPX adapter buffers a finite request iterator and sends identical bytes on retries, while a 400 response is not retried. Backoff and jitter settings are in `client_flow.RETRIES`; this lab does not infer a statistical jitter distribution from wall-clock measurements.

The payment fixture stores keys in memory and handles sequential calls only. It is not a production idempotency implementation. The shared implementation is in the neighbouring [HTTP clients lab](../2026-09-07-why-i-stopped-wrapping-http-clients/README.md); keep that directory.

Run from `docs/blog/lab/2026-09-07-retry-after-backoff-jitter` in the repository checkout. Dependencies are pinned in `requirements.txt`.

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python backoff_lab.py
```

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-retry-after-backoff-jitter).
