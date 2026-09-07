# Lab: when should Redis fail open?

Two scripts. Redis 7 runs in a container the scripts start; "Redis is gone" is the container paused,
so connections neither succeed nor fail, which is what a dead box on the network looks like.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "redis-client-kit[settings]" "idempotency-kit[redis]==0.3.0" "testcontainers[redis]"
.venv/bin/python retry_probe.py
.venv/bin/python fail_open_lab.py
```

`retry_probe.py` times one GET against the paused Redis per client configuration. `fail_open_lab.py`
runs a cache, a rate limiter, an idempotency coordinator and a health check with Redis up, paused,
and back.
