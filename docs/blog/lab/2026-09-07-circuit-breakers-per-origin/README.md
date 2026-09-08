# Lab: circuit breakers should be per origin

One script, against three in-process origins.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "clientwright[httpx]==0.2.2"
.venv/bin/python breakers_lab.py
```

Four scenes: one client talking to three upstreams of which one is down, with a hand-rolled breaker
keyed on the client and with a breaker keyed on the origin; which responses trip a breaker; a
breaker that counts attempts against one that counts logical calls, under retries; and the
half-open probe after the recovery timeout.
