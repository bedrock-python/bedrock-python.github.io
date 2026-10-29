# Lab: Read timeout and the total deadline {#lab-reliability-is-not-retry3}

The server sends ten bytes, one every 80 ms. Plain HTTPX with a 300 ms read timeout receives the full response because data keeps arriving. With clientwright's 350 ms total limit, body consumption raises `DeadlineExceededError` before completion.

A second check combines read timeouts and retries against a slow endpoint. It asserts one logical call and at most three attempts. If a further retry cannot fit, the final error can remain the last read timeout; a deadline policy does not require waiting until the deadline expires.

This uses the real HTTP fixture and functions in the neighbouring [HTTP clients lab](../2026-09-07-why-i-stopped-wrapping-http-clients/README.md). Keep that directory when copying the example. Timing assertions allow scheduling overhead; this is not a load test.

Run from `docs/blog/lab/2026-09-07-reliability-is-not-retry-3` in the repository checkout. Dependencies are pinned in `requirements.txt`.

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python reliability_lab.py
```

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-reliability-is-not-retry-3).
