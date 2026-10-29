# Lab: one lifecycle for HTTP and a worker {#lab-one-lifecycle-for-http-a-scheduler-and-a-worker}

A reports service has an HTTP route and a periodic worker. `one_lifecycle.py` connects them to the same `AppSpec` and container. The `api`, `worker` and `all` roles choose which entrypoints run. Separate processes get separate resources; they share the initialization code.

`report_store.py` is an instrumented in-memory database stand-in. It records opens, reports, cancellation and close, and fails if a report outlives its resource. `run_roles.py` checks all three roles, warmup failure, stop during warmup and failure of an essential worker. Assertions verify the order; timing measurements are not used as proof.

The periodic callback owns its one-second operation limit. `DaemonEntrypoint` does not turn an arbitrary callback into a bounded draining queue. In the `all` role, the Host waits for the callback to return before withdrawing readiness.

The driver uses real localhost HTTP and `Service.run(..., stop=event)` on Windows and Linux. It does not test OS signals or Kubernetes routing. For a manual run, execute `one_lifecycle.py api` with the same dependencies; it listens on `127.0.0.1:8080` and `run_sync` owns process signals.

Run from `docs/blog/lab/2026-09-07-one-lifecycle` in the repository checkout:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python run_roles.py
```

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-one-lifecycle).
