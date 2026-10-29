# Lab: warmup, readiness and liveness {#lab-warmup-readiness-and-liveness}

This variant adds Redis as a required job-state dependency. The Redis health check has a 250 ms total limit. The client closes when the application scope exits, including on startup failure.

The driver starts `redis:7-alpine` with Testcontainers and pauses it to cause an actual network timeout. It asserts that the HTTP port is absent during warmup, both probes return 200 after startup, Redis failure changes only readiness to 503, and recovery restores readiness without restarting the application. A direct `/reports` request still works because this lab route does not use Redis; a readiness failure does not itself block incoming requests.

Finally it sets the public stop event, checks readiness=503 while HTTP still responds during the drain delay, and verifies resource cleanup. This is a local HTTP/Redis integration test, not a Kubernetes probe or signal test.

Docker is required. The scripts import the [shared reports service](../2026-09-07-one-lifecycle/README.md); keep that neighbouring directory.

Run from `docs/blog/lab/2026-09-07-warmup-readiness-liveness` in the repository checkout:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python driver.py
```

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-warmup-readiness-liveness).
