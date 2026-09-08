# Lab: why I stopped wrapping HTTP clients

One script behind the measurements, against clientwright's in-process fault-injecting origin.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "clientwright[httpx,aiohttp,requests]==0.2.2" tenacity
.venv/bin/python wrappers_lab.py
```

Four scenes: the type of the client each `build()` returns; one retry policy driving httpx and
aiohttp against an endpoint that fails twice, with the metric record each produced; a tenacity
loop wrapped around a client that already retries; and what the build reports when an adapter
cannot express a setting, under `warn` and under `strict`.
