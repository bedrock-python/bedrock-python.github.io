# Lab: application lifecycle inside FastAPI {#lab-why-application-lifecycle-should-not-belong-to-fastapi}

`lifespan_api.py` opens the report store in FastAPI lifespan. `lifespan_worker.py` repeats the resource and warmup wiring for a worker. Both versions correctly close the resource, including when startup fails. The duplication is the reason to consider a shared runtime once the service has several entrypoints.

`check_lifespans.py` asserts all four paths: successful HTTP request, successful worker report and a startup failure in each. HTTP uses FastAPI's `TestClient`; the worker stops via an `asyncio.Event`.

The instrumented `ReportStore` comes from the [shared lifecycle lab](../2026-09-07-one-lifecycle/README.md). It is an in-memory database stand-in that checks resource lifetime, not a database client. Keep the neighbouring lab directory when copying these files.

Run from `docs/blog/lab/2026-09-07-lifecycle-not-fastapi` in the repository checkout:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python check_lifespans.py
```

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-lifecycle-not-fastapi).
