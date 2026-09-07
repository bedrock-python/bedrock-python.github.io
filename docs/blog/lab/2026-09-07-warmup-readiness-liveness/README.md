# Lab: warmup, readiness and liveness

One service with a three-second warmup, a readiness check on Redis and a route that needs neither.
The driver polls `livez`, `readyz` and the route every 100 ms through the whole lifecycle: the
warmup, a Redis outage played by pausing the container, and a `SIGTERM` with a two-second drain
delay. It prints every transition it saw.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "servicewright[fastapi]==0.10.0" redis "httpx==0.28.1" "testcontainers[redis]"
.venv/bin/python driver.py
```

| Script | What it is |
|---|---|
| `service.py` | the service: a warmer, a readiness check, one route, probes from the adapter |
| `driver.py` | Redis in a container, the poller, the pause and the signal |
