# Lab: finish accepted HTTP requests before closing resources {#lab-graceful-shutdown-is-a-protocol}

`driver.py` starts the shared reports service and sends real localhost HTTP requests. It tests two outcomes:

- An accepted 0.8-second report returns 200 after readiness has changed to 503; its store closes afterwards.
- A 30-second report exceeds Uvicorn's one-second graceful timeout, is cancelled and returns 500 before the response has started; cleanup follows cancellation. That response is the observed result for this route and pinned stack, not a general cancellation guarantee.

`AppSpec.drain_grace_seconds=3` leaves time for the HTTP adapter to finish after Uvicorn's request deadline. These are separate limits. `cleanup_timeout_seconds` is per shutdown step; the application scope must also bound its own resource cleanup.

`server_servicewright.py` and `server_plain.py` are manual entrypoints. The latter uses FastAPI lifespan and Uvicorn's own request draining, which is enough for many HTTP-only applications. The automated driver tests the servicewright path using `Service.run(..., stop=event)`; it does not send SIGTERM or simulate a Kubernetes rollout. Signal delivery and routing delay still need a deployment-level test.

Keep the neighbouring [shared lifecycle lab](../2026-09-07-one-lifecycle/README.md), whose store and route are reused here. No Docker is needed.

Run from `docs/blog/lab/2026-09-07-graceful-shutdown` in the repository checkout:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python driver.py
```

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-graceful-shutdown).
