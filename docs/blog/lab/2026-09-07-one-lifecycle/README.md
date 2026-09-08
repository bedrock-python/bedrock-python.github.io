# Lab: one lifecycle for HTTP, a scheduler and a worker

`one_lifecycle.py` is one `AppSpec` with three entrypoints (a FastAPI server, an APScheduler job every
half second, a daemon loop) sharing one pool; `ROLE` picks which of them the process runs. Each
entrypoint is wrapped in a tracer that prints the four calls the Host makes on it. `run_roles.py`
starts the service as `all`, `api` and `worker`, drives it briefly, sends SIGTERM and prints the
timeline.

```bash
uv venv --python 3.13 .venv
uv pip install --prerelease=allow --python .venv/bin/python "servicewright[fastapi,apscheduler4]==0.10.0" "httpx==0.28.1"
.venv/bin/python run_roles.py
```

`--prerelease=allow` is for APScheduler 4, which is still a pre-release; pin httpx, or the same flag
pulls in a 1.0 development build.
